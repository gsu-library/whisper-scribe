from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings

from .models import Transcription
from .utils import format_seconds

import json, re


def format_filename(name):
   """
   Replaces whitespace with underscores and removes any characters that are not
   alphanumeric, underscores, or hyphens.

   Args:
      name (str): The string to format.

   Returns:
      string: The formatted string.
   """
   whitespace_pattern = re.compile('\\s+', re.UNICODE)
   remove_pattern = re.compile('[^a-zA-Z0-9_-]+', re.UNICODE)
   name = whitespace_pattern.sub('_', name)
   return remove_pattern.sub('', name)


def download_text(request, transcription_id):
   """
   Downloads a formatted text file of the requested transcription, including speaker
   names if available.

   Args:
      transcription_id (int): ID of the transcription to download.

   Returns:
      HttpResponse: A formatted text file of the transcription.
   """
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   segments = transcription.segments.all()
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


def download_text_blob(request, transcription_id):
   """
   Downloads a text blob of the requested transcription.

   Args:
      transcription_id (int): ID of the transcription to download.

   Returns:
      HttpResponse: A text blob of the transcription.
   """
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   segments = transcription.segments.all()
   output = ''

   for segment in segments:
      output += segment.text + ' '

   output = output.rstrip(' ')

   return HttpResponse(output, headers = {
      'Content-Type': 'text/plain',
      'Content-Disposition': f'attachment; filename="{format_filename(transcription.title)}.txt"',
   })


def download_srt(request, transcription_id):
   """
   Downloads an SRT of the requested transcription, including speaker names if
   available.

   Args:
      transcription_id (int): ID of the transcription to download.

   Returns:
      HttpResponse: An SRT file of the transcription.
   """
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   segments = transcription.segments.all()
   output = ''
   count = 1

   for segment in segments:
      output += f'{count!s}\n'
      output += f'{format_seconds(segment.start, True, ",")} --> {format_seconds(segment.end, True, ",")}\n'

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


def download_vtt(request, transcription_id):
   """
   Downloads a VTT of the requested transcription, including speaker names if available.

   Args:
      transcription_id (int): ID of the transcription to download.

   Returns:
      HttpResponse: A VTT file of the transcription.
   """
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   segments = transcription.segments.all()
   output = 'WEBVTT\n\n'

   for segment in segments:
      output += f'{format_seconds(segment.start)} --> {format_seconds(segment.end)}\n'

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


def download_json(request, transcription_id):
   """
   Downloads a JSON representation of the requested transcription, including speaker
   names if available.

   Args:
      transcription_id (int): ID of the transcription to download.

   Returns:
      HttpResponse: A JSON representation of the transcription.
   """
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   segments = transcription.segments.all()
   output = []

   for segment in segments:
      segment_dict = segment.__dict__
      del segment_dict['_state']
      output.append(segment_dict)

   return HttpResponse(json.dumps(output), headers = {
      'Content-Type': 'application/json',
      'Content-Disposition': f'attachment; filename="{format_filename(transcription.title)}.json"',
   })
