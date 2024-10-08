from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from .forms import *
from .models import *
from core.settings import HUGGING_FACE_TOKEN, BASE_DIR, USE_DJANGO_Q

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
            file_title = Path(request.FILES['upload_file']._name).stem # TODO: check _name usage
            saved_transcription = Transcription(
               title = file_title,
               model = form.cleaned_data['model'],
               upload_file = form.cleaned_data['upload_file'],
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
      model = form.cleaned_data['model'],
      upload_file = str(file_path),
   )
   transcription.save()

   return transcription


# Function: transcribe_file
def transcribe_file(transcription):
   segment_list = []

   # Check for CUDA
   device = 'cpu'
   if torch.cuda.is_available():
      device = 'cuda'

   model = WhisperModel(transcription.model, device=device, compute_type='auto', download_root=str(MODEL_CACHE_PATH))
   transcription_segments, info = model.transcribe(transcription.upload_file.path, beam_size=5, word_timestamps=True)

   for transcription_segment in transcription_segments:
      word_list = []
      min_probability = 1.0

      for word in transcription_segment.words:
         word_list.append({
            'start': word.start,
            'end': word.end,
            'word': word.word,
            'probability': word.probability,
         })

         if word.probability < min_probability: min_probability = word.probability

      segment_list.append({
         # 'id': segment.id - 1, # TODO: probably remove this, not needed
         'start': transcription_segment.start,
         'end': transcription_segment.end,
         'text': transcription_segment.text,
         'words': word_list,
      })

      segment = Segment(
         transcription = transcription,
         start = transcription_segment.start,
         end = transcription_segment.end,
         text = transcription_segment.text,
         probability = min_probability,
      )

      segment.save()

   transcription.base_segments = segment_list
   transcription.save(update_fields=['base_segments'])


# Function: diarize_separate_overlaps
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


# Function diarize_word_list
def diarize_word_list(transcription):
   diarized_segments = diarize_separate_overlaps(transcription.diarization)

   # Add text and probability.
   for segment in diarized_segments:
      segment['text'] = ''
      segment['probability'] = 1.0

   # Generate word list
   word_list = []
   # Need refresh if q is used
   transcription.refresh_from_db()
   for segment in transcription.base_segments:
      for words in segment['words']:
         word_list.append(words)

   # Make sure word list is sorted by start time
   word_list = sorted(word_list, key=lambda x: x['start'])
   word_index = 0

   # Helper function for diarized segment processing
   def add_word_probability():
      segment['text'] += word['word']
      segment['probability'] = min(segment['probability'], word['probability'])

   for segment in diarized_segments:
      # TODO: is there a better way to do this without copying?
      while word_index < len(word_list):
         word = word_list[word_index]

         # If word start happens during segment
         if word['start'] >= segment['start'] and word['start'] <= segment['end']:
            add_word_probability()
            # segment['end'] = max(word['end'], segment['end']) # todo: keep/remove this?
         # If word end happens during segment
         elif word['end'] >= segment['start'] and word['end'] <= segment['end']:
            add_word_probability()
            # segment['start'] = min(word['start'], segment['start']) # todo: keep/remove this?
         # If the word ended before the current segment started
         elif word['end'] < segment['start']:
            add_word_probability()
            # segment['start'] = word['start'] # todo: keep/remove this?
         else:
            break

         word_index += 1

      # TODO: look into updating segments ends here
      # Make sure segment end aligns with last word added?
      # segment['end'] = word['end']

   segment = diarized_segments[-1]

   # Are there leftover words that didn't fit a segment?
   while word_index < len(word_list):
      word = word_list[word_index]
      add_word_probability()
      # segment['end'] = word['end'] # todo: keep/remove this?
      word_index += 1

   # Remove segments that are empty
   diarized_segments[:] = [segment for segment in diarized_segments if segment['text']]
   # TODO: Resegment diarized segments
   return diarized_segments


# Function: diarize_file
def diarize_file(transcription):
   result = []
   pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization-3.1', use_auth_token=HUGGING_FACE_TOKEN, cache_dir=MODEL_CACHE_PATH)

   if torch.cuda.is_available():
      pipeline.to(torch.device('cuda'))

   diarization = pipeline(transcription.upload_file.path)

   for turn, _, speaker in diarization.itertracks(yield_label=True):
      # print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
      result.append({'start': turn.start, 'end': turn.end, 'speaker': speaker})

   transcription.diarization = result
   transcription.save(update_fields=['diarization'])

   diarized_segments = diarize_word_list(transcription)
   # Remove all related segments from transcription.
   # TODO: if diarization is selected on initial form maybe don't store segments
   # would be helpful to have if the diarizer fails though
   transcription.segment_set.all().delete()

   for diarized_segment in diarized_segments:
      diarized_segment['transcription'] = transcription
      segment = Segment(**diarized_segment)
      segment.save()
