from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings

from .models import Transcription
from .utils import format_timestamp

import json, re


# Function: format_filename
def format_filename(name):
   whitespace_pattern = re.compile('\\s+', re.UNICODE)
   remove_pattern = re.compile('[^a-zA-Z0-9_-]+', re.UNICODE)
   name = whitespace_pattern.sub('_', name)
   return remove_pattern.sub('', name)


# Function: download_text
def download_text(request, transcription_id):
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   segments = transcription.segment_set.all()
   output = ''

   for segment in segments:
      if segment.speaker:
         if settings.UPPERCASE_SPEAKER_NAMES:
            output += segment.speaker.upper()
         else:
            output += segment.speaker

         output += ':\t'

      output += segment.text + '\n\n'

   output = output.rstrip('\n') + '\n'

   return HttpResponse(output, headers = {
      'Content-Type': 'text/plain',
      'Content-Disposition': f'attachment; filename="{format_filename(transcription.title)}.txt"',
   })


# Function: download_text_blob
def download_text_blob(request, transcription_id):
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   segments = transcription.segment_set.all()
   output = ''

   for segment in segments:
      output += segment.text + ' '

   output = output.rstrip(' ')

   return HttpResponse(output, headers = {
      'Content-Type': 'text/plain',
      'Content-Disposition': f'attachment; filename="{format_filename(transcription.title)}.txt"',
   })


# Function: download_srt
def download_srt(request, transcription_id):
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   segments = transcription.segment_set.all()
   output = ''
   count = 1

   for segment in segments:
      output += f'{count!s}\n'
      output += f'{format_timestamp(segment.start, True, ",")} --> {format_timestamp(segment.end, True, ",")}\n'

      if segment.speaker:
         if settings.UPPERCASE_SPEAKER_NAMES:
            output += segment.speaker.upper()
         else:
            output += segment.speaker

         output += ': '

      output += f'{segment.text}\n\n'
      count += 1

   output = output.rstrip('\n') + '\n'

   return HttpResponse(output, headers = {
      'Content-Type': 'text/plain',
      'Content-Disposition': f'attachment; filename="{format_filename(transcription.title)}.srt"',
   })


# Function: download_vtt
def download_vtt(request, transcription_id):
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   segments = transcription.segment_set.all()
   output = 'WEBVTT\n\n'

   for segment in segments:
      output += f'{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}\n'

      if segment.speaker:
         if settings.UPPERCASE_SPEAKER_NAMES:
            output += segment.speaker.upper()
         else:
            output += segment.speaker

         output += ': '

      output += f'{segment.text}\n\n'

   output = output.rstrip('\n') + '\n'

   return HttpResponse(output, headers = {
      'Content-Type': 'text/vtt',
      'Content-Disposition': f'attachment; filename="{format_filename(transcription.title)}.vtt"',
   })


# Function: download_json
def download_json(request, transcription_id):
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   segments = transcription.segment_set.all()
   output = []

   for segment in segments:
      segment_dict = segment.__dict__
      del segment_dict['_state']
      output.append(segment_dict)

   return HttpResponse(json.dumps(output), headers = {
      'Content-Type': 'application/json',
      'Content-Disposition': f'attachment; filename="{format_filename(transcription.title)}.json"',
   })
