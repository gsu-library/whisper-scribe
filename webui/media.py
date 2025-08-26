from django.core.files import File
from django.conf import settings

from .models import *
from .utils import *

from datetime import datetime
from pathlib import Path
from yt_dlp import YoutubeDL
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline
import torch
import uuid


# Function: process_submission
def process_submission(transcription_id, upload_url, diarize):
   try:
      transcription = Transcription.objects.get(pk=transcription_id)
   except Transcription.DoesNotExist:
      return

   # Download media
   if upload_url:
      try:
         download_media(transcription_id, upload_url)
      except:
         transcription.fail_incomplete_statuses('Downloading media failed.')
         return

   # Transcribe file
   try:
      transcribe_file(transcription_id)
   except:
      transcription.fail_incomplete_statuses('Transcribing media failed.')
      return

   # Diarize transcription
   if diarize and settings.HUGGING_FACE_TOKEN:
      try:
         diarize_file(transcription_id)
      except:
         transcription.fail_incomplete_statuses('Diarizing media failed.')
         return

   return


# Function: download_media
def download_media(transcription_id, upload_url):
   try:
      transcription = Transcription.objects.get(pk=transcription_id)
   except Transcription.DoesNotExist:
      return

   download_status = transcription.statuses.get(process=TranscriptionStatus.DOWNLOADING)
   if download_status.status == TranscriptionStatus.FAILED: return
   download_status.status = TranscriptionStatus.PROCESSING
   download_status.start_time = datetime.now()
   download_status.save()

   # Can the opts for yt-dlp use a function to generate hex codes on the fly?
   hex = '_' + uuid.uuid4().hex[:7]

   ydl_opts = {
      'paths': {
         'home': str(Path(settings.MEDIA_ROOT).joinpath('temp')),
      },
      'outtmpl': '%(title)s' + hex,
      # This should force playlists to only download one item right now
      'playlist_items': '1',
   }

   with YoutubeDL(ydl_opts) as ydl:
      all_info = ydl.extract_info(upload_url, download=True)

   if '_type' in all_info and all_info['_type'] == 'playlist':
      # This can eventually be the loop for processing multiple videos
      for entry in all_info['entries']:
         single_info = entry
         # Only care about the first entry right now
         break
   else:
      single_info = all_info

   file_path = Path(single_info['requested_downloads'][0]['filepath'])

   transcription.title = single_info['title']
   transcription.upload_file = File(open(str(file_path), 'rb'), name=file_path.name)
   transcription.save(update_fields=['title', 'upload_file'])

   # Delete temp file
   Path(file_path).unlink(True)

   download_status.status = TranscriptionStatus.COMPLETED
   download_status.end_time = datetime.now()
   download_status.save()
   return


# Function: resegment_words
def resegment_word_list(word_list, max_characters, max_time):
   # Better than param defaults as checks for ''
   # Segments will get the first word, do not need to check for minimum length or time
   if not max_characters: max_characters = settings.MAX_SEGMENT_LENGTH
   if not max_time: max_time = settings.MAX_SEGMENT_TIME
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
         segment['text'] = segment['text'].strip()
         segments.append(segment)
         segment = None
         continue

      word_list_index += 1

   segment['text'] = segment['text'].strip()
   segments.append(segment)
   return segments


# Function: transcribe_file
def transcribe_file(transcription_id):
   try:
      transcription = Transcription.objects.get(pk=transcription_id)
   except Transcription.DoesNotExist:
      return

   transcription_status = transcription.statuses.get(process=TranscriptionStatus.TRANSCRIBING)
   if transcription_status.status == TranscriptionStatus.FAILED: return
   transcription_status.status = TranscriptionStatus.PROCESSING
   transcription_status.start_time = datetime.now()
   transcription_status.save()

   DESCRIPTION_MAX_LENGTH = 100
   word_list = []
   meta = transcription.meta
   model = 'base' if not meta['model'] else meta['model']
   language = None if not meta['language'] else meta['language']

   # Save audio duration and file size
   transcription.meta['duration'] = format_seconds(get_file_duration(transcription.upload_file.path), include_mill=False)
   transcription.meta['size'] = transcription.upload_file.size
   transcription.save(update_fields=['meta'])

   # Check for CUDA
   device = 'cpu'
   if torch.cuda.is_available():
      device = 'cuda'

   model = WhisperModel(meta['model'], device=device, compute_type='auto', download_root=str(settings.MODEL_CACHE_PATH))
   transcription_segments, info = model.transcribe(
      transcription.upload_file.path,
      language=language,
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

   # Save segments to database and generate a description.
   description = ''

   for segment in segments:
      segment['transcription'] = transcription
      segment_to_save = Segment(**segment)
      segment_to_save.save()

      if len(description) < DESCRIPTION_MAX_LENGTH:
         description += segment['text'] + ' '

   transcription.refresh_from_db()
   transcription.description = description[:DESCRIPTION_MAX_LENGTH].strip() + '...'
   transcription.save(update_fields=['description'])

   transcription_status.status = TranscriptionStatus.COMPLETED
   transcription_status.end_time = datetime.now()
   transcription_status.save()
   return


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
         speaker_bucket = next(bucket_iter, None)
         continue

      word_list_index += 1

   return word_list


# Function: diarize_file
def diarize_file(transcription_id):
   try:
      transcription = Transcription.objects.get(pk=transcription_id)
   except Transcription.DoesNotExist:
      return

   diarize_status = transcription.statuses.get(process=TranscriptionStatus.DIARIZING)
   if diarize_status.status == TranscriptionStatus.FAILED: return
   diarize_status.status = TranscriptionStatus.PROCESSING
   diarize_status.start_time = datetime.now()
   diarize_status.save()

   result = []
   meta = transcription.meta
   pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization-3.1', use_auth_token=settings.HUGGING_FACE_TOKEN, cache_dir=settings.MODEL_CACHE_PATH)

   if torch.cuda.is_available():
      pipeline.to(torch.device('cuda'))

   # Convert media to .wav
   temp_audio = extract_audio_to_wav(transcription.upload_file.path)

   diarization = pipeline(temp_audio)

   for turn, _, speaker in diarization.itertracks(yield_label=True):
      # print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
      result.append({'start': turn.start, 'end': turn.end, 'speaker': speaker})

   transcription.diarization = result
   transcription.save(update_fields=['diarization'])
   # Delete temp audio file
   temp_audio.unlink()

   word_list = diarize_assign_speakers(transcription)
   diarized_segments = resegment_word_list(word_list, meta['max_segment_length'], meta['max_segment_time'])
   # Remove existing segments
   transcription.segments.all().delete()

   for diarized_segment in diarized_segments:
      diarized_segment['transcription'] = transcription
      segment = Segment(**diarized_segment)
      segment.save()

   diarize_status.status = TranscriptionStatus.COMPLETED
   diarize_status.end_time = datetime.now()
   diarize_status.save()
   return
