from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from .forms import *
from .models import *
from core.settings import HUGGING_FACE_TOKEN, BASE_DIR, USE_DJANGO_Q, MAX_SEGMENT_LENGTH, MAX_SEGMENT_TIME

from pathlib import Path
from uuid import uuid4
from yt_dlp import YoutubeDL
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline
from django_q.tasks import async_task, result
from pprint import pp
import torch
import mimetypes
# TODO: fix multiple Path instances
# TODO: move form model listing to settings


FILE_UPLOAD_PATH = Path(__file__).resolve().parent.joinpath('files/uploads')
FILE_DOWNLOAD_PATH = Path(__file__).resolve().parent.joinpath('files/downloads')
# TODO: probably won't need download path
MODEL_CACHE_PATH = Path(__file__).resolve().parent.joinpath('files/models')
# TODO: at some point trim whitespace from final segments


# Function: index
def index(request):
   form = TranscriptionForm()
   transcriptions = Transcription.objects.all()

   # Form submission
   if request.method == 'POST':
      form = TranscriptionForm(request.POST, request.FILES)

      if form.is_valid():
         if request.FILES:
            # TODO: check file type against valid array?
            saved_transcription = Transcription(
               title = Path(request.FILES['upload_file'].name).stem,
               upload_file = form.cleaned_data['upload_file'],
               meta = {
                  'model': form.cleaned_data['model'],
                  'hotwords': form.cleaned_data['hotwords'],
                  'vad_filter': form.cleaned_data['vad_filter'],
                  'max_segment_length': form.cleaned_data['max_segment_length'],
                  'max_segment_time': form.cleaned_data['max_segment_time'],
               },
            )
            saved_transcription.save()
         elif form.cleaned_data['upload_url']:
            saved_transcription = handle_url_upload(form)

         if USE_DJANGO_Q:
            async_task(transcribe_file, saved_transcription, hook=transcription_complete)
         else:
            transcribe_file(saved_transcription)

         if form.cleaned_data['diarize']:
            if USE_DJANGO_Q:
               async_task(diarize_file, saved_transcription, hook=diarization_complete)
            else:
               diarize_file(saved_transcription)

         return HttpResponseRedirect(reverse('webui:index'))

   return render(request, 'webui/index.html', {'form': form, 'transcriptions': transcriptions})


def transcription_complete(task):
   print('transcription completed')


def diarization_complete(task):
   print('diarization completed')


# Function: view_transcription
def view_transcription(request, transcription_id):
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   segments = transcription.segment_set.all()
   return render(request, 'webui/view.html', {'segments': segments})


# Function: edit_transcription
def edit_transcription(request, transcription_id):
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   segments = transcription.segment_set.all()
   speakers = set(segments.exclude(speaker__exact='').values_list('speaker', flat=True).distinct())

   if request.POST:
      speaker_old = request.POST.get('speaker-old')
      speaker_new = request.POST.get('speaker-new', '').strip()

      if speaker_old and speaker_new:
         segments.filter(speaker=speaker_old).update(speaker=speaker_new)

      return HttpResponseRedirect(reverse('webui:edit', args=[transcription_id]))

   type = 'video'

   if mimetypes.guess_type(str(transcription.upload_file))[0].startswith('audio'):
      type = 'audio'

   properties = {
      'id': transcription.id,
      'title': transcription.title,
      'description': transcription.description,
      'notes': transcription.notes,
      'file': 'uploads/' + str(Path(str(transcription.upload_file)).name),
      'type': type,
      'speakers': speakers,
   }

   # TODO: can the template reference transcription from segments passed? (for title, id, etc.)

   return render(request, 'webui/edit.html', {'segments': segments, 'properties': properties})


# Function: delete_transcription
def delete_transcription(request, transcription_id):
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   transcription.delete()
   return HttpResponseRedirect(reverse('webui:index'))


# Function: handle_url_upload
def handle_url_upload(form):
   hex = '_' + uuid4().hex[:7]

   ydl_opts = {
      'paths': {
         'home': str(FILE_UPLOAD_PATH),
      },
      'outtmpl': '%(title)s' + hex,
   }

   # TODO: configure this to work with playlists
   with YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(form.cleaned_data['upload_url'])

   # Create relative file path to match model file field behavior.
   file_path = Path(info['requested_downloads'][0]['filepath']).relative_to(BASE_DIR)

   transcription = Transcription(
      title = info['title'],
      upload_file = str(file_path),
      meta = {
         'model': form.cleaned_data['model'],
         'hotwords': form.cleaned_data['hotwords'],
         'vad_filter': form.cleaned_data['vad_filter'],
         'max_segment_length': form.cleaned_data['max_segment_length'],
         'max_segment_time': form.cleaned_data['max_segment_time'],
      },
   )
   transcription.save()

   return transcription


# Function: transcribe_file
def transcribe_file(transcription):
   word_list = []
   meta = transcription.meta

   # Check for CUDA
   device = 'cpu'
   if torch.cuda.is_available():
      device = 'cuda'

   model = WhisperModel(meta['model'], device=device, compute_type='auto', download_root=str(MODEL_CACHE_PATH))
   transcription_segments, info = model.transcribe(
      transcription.upload_file.path,
      language=None, #TOOD: will probably implement language later
      beam_size=5,
      word_timestamps=True,
      vad_filter=meta['vad_filter'],
      hotwords=meta['hotwords'],
   )

   for transcription_segment in transcription_segments:
      for word in transcription_segment.words:
         word_list.append({
            'start': word.start,
            'end': word.end,
            'word': word.word,
            'probability': word.probability,
            'speaker': '',
         })


   transcription.word_list = word_list
   transcription.save(update_fields=['word_list'])

   segments = resegment_word_list(word_list, meta['max_segment_length'], meta['max_segment_time'])

   for segment in segments:
      segment['transcription'] = transcription
      segment_to_save = Segment(**segment)
      segment_to_save.save()

   pass


# Function: resegment_words
def resegment_word_list(word_list, max_characters, max_time):
   # Better than param defaults as checks for ''
   if not max_characters: max_characters = MAX_SEGMENT_LENGTH
   if not max_time: max_time = MAX_SEGMENT_TIME
   segments = []
   segment = None

   if not word_list: return segments
   word_list = sorted(word_list, key=lambda x: x['start'])
   word_list_index = 0

   # Process word list
   while word_list_index < len(word_list):
      word = word_list[word_list_index]

      if not segment:
         segment = {
            'start': word['start'],
            'end': word['end'],
            'text': word['word'],
            'speaker': word['speaker'],
            'probability': word['probability']
         }
      elif word['speaker'] == segment['speaker'] and \
         len(word['word']) + len(segment['text']) <= max_characters and \
         word['end'] - segment['start'] <= max_time:
         segment['text'] += word['word']
         segment['end'] = word['end']
         segment['probability'] = min(segment['probability'], word['probability'])
      else:
         segments.append(segment)
         segment = None
         continue

      word_list_index += 1

   segments.append(segment)
   return segments


# Function: diarize_separate_overlaps
# TODO: rework this function
def diarize_separate_overlaps(diarization):
   # Sort the speaker ranges by their start time
   diarization = sorted(diarization, key=lambda x: x['start'])

   # Initialize an empty list to store the separated ranges
   final_segments = []

   # Iterate through the speaker ranges
   for i in range(len(diarization)):
         # If this is the first range, add it to the separated ranges list

         if i == 0:
               final_segments.append(diarization[i])
         else:
               # Get the previous range
               previous_segment = dict(final_segments[-1])

               # If the current range starts after the previous range ends, add it to the separated ranges list
               if diarization[i]['start'] >= previous_segment['end'] or diarization[i]['speaker'] == previous_segment['speaker']:
                     final_segments.append(diarization[i])
               else:
                     # Otherwise, there is an overlap, so split the ranges
                     # First, add the part of the previous range that doesn't overlap
                     final_segments[-1]['end'] = diarization[i]['start']
                     # Then add the overlap as a new range
                     overlap = {
                        'speaker': 'OVERLAP',
                        'start': diarization[i]['start'],
                        'end': min(diarization[i]['end'], previous_segment['end'])
                     }
                     final_segments.append(overlap)
                     # Finally, add the part of the current range that doesn't overlap
                     if diarization[i]['end'] > previous_segment['end']:
                        non_overlap = {
                           'speaker': diarization[i]['speaker'],
                           'start': overlap['end'],
                           'end': diarization[i]['end']
                        }
                     else:
                        non_overlap = {
                           'speaker': previous_segment['speaker'],
                           'start': overlap['end'],
                           'end': previous_segment['end']
                        }
                     final_segments.append(non_overlap)

   return final_segments


# Function: diarize_assign_speakers
def diarize_assign_speakers(transcription):
   word_list = []
   if not transcription: return word_list
   speaker_buckets = diarize_separate_overlaps(transcription.diarization)
   transcription.refresh_from_db()
   word_list = transcription.word_list
   word_list = sorted(word_list, key=lambda x: x['start'])
   bucket_iter = iter(speaker_buckets)
   speaker_bucket = next(bucket_iter, None)
   last_speaker = speaker_bucket.get('speaker', '') if speaker_bucket else ''
   word_list_index = 0

   # Assign speakers to words in the word_list
   while word_list_index < len(word_list):
      word = word_list[word_list_index]

      # Words are left after buckets are exhausted
      if not speaker_bucket:
         word['speaker'] = last_speaker
      elif word['start'] < speaker_bucket['end']:
         word['speaker'] = speaker_bucket['speaker']
      else:
         last_speaker = speaker_bucket['speaker']
         speaker_bucket = next(bucket_iter)
         continue

      word_list_index += 1

   return word_list


# Function: diarize_file
def diarize_file(transcription):
   result = []
   meta = transcription.meta
   pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization-3.1', use_auth_token=HUGGING_FACE_TOKEN, cache_dir=MODEL_CACHE_PATH)

   if torch.cuda.is_available():
      pipeline.to(torch.device('cuda'))

   diarization = pipeline(transcription.upload_file.path)

   for turn, _, speaker in diarization.itertracks(yield_label=True):
      # print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
      result.append({'start': turn.start, 'end': turn.end, 'speaker': speaker})

   transcription.diarization = result
   transcription.save(update_fields=['diarization'])

   word_list = diarize_assign_speakers(transcription)
   diarized_segments = resegment_word_list(word_list, meta['max_segment_length'], meta['max_segment_time'])
   # Remove existing segments
   transcription.segment_set.all().delete()

   for diarized_segment in diarized_segments:
      diarized_segment['transcription'] = transcription
      segment = Segment(**diarized_segment)
      segment.save()
