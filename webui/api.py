from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string

from .models import *
from .utils import is_float, format_seconds

import json


def api_transcriptions_id(request, transcription_id):
   """
   Handles API POST requests to update transcriptions.

   Args:
      transcription_id (int): ID of the transcription to update.

   Returns:
      JsonResponse: JSON message and status of the result.
   """
   if 'X-Requested-With' not in request.headers or request.headers['X-Requested-With'] != 'XMLHttpRequest':
      return JsonResponse({'message': 'malformed header'}, status=400)

   try:
      transcription = Transcription.objects.get(pk=transcription_id)
   except Transcription.DoesNotExist:
      return JsonResponse({'message': f'transcripton {transcription_id} not found'}, status=404)

   if(request.method == 'POST'):
      data = json.loads(request.body)
      field = data.get('field')
      value = data.get('value', '')
      if isinstance(value, (str)):
         value = value.strip()

      # Do not allow a blank title to be submitted
      if field == 'title' and not value:
         return JsonResponse({'message': 'bad request'}, status=400)

      # If value is empty it can be saved as an empty string
      if field and (value == '' or value):
         setattr(transcription, field, value)
         transcription.save(update_fields=[field])
         return JsonResponse({'message': 'sucess'}, status=200)

   return JsonResponse({'message': 'bad request'}, status=400)


def api_segments(request):
   """
   Handles API POST requests for segment creation.

   Returns:
      JsonResponse: JSON message of a newly rendered segment (if successfull) and the
      status of the result.
   """
   if 'X-Requested-With' not in request.headers or request.headers['X-Requested-With'] != 'XMLHttpRequest':
      return JsonResponse({'message': 'malformed header'}, status=400)

   # Create new segment
   if(request.method == 'POST'):
      data = json.loads(request.body)
      clicked_id = data.get('segmentId')
      other_id = int(data.get('otherId', -1))
      where = int(data.get('where', 0))
      other_segment = None

      try:
         clicked_segment = Segment.objects.get(pk=clicked_id)
      except Segment.DoesNotExist:
         return JsonResponse({'message': f'segment {clicked_id} not found'}, status=404)

      if other_id > 0:
         try:
            other_segment = Segment.objects.get(pk=other_id)
         except Segment.DoesNotExist:
            return JsonResponse({'message': f'segment {other_id} not found'}, status=404)

      # If the new segment is before
      if where < 0:
         if other_segment:
            new_start = other_segment.end
         else:
            new_start = clicked_segment.start

         new_end = clicked_segment.start
      # If the new segment is after
      elif where > 0:
         new_start = clicked_segment.end

         if other_segment:
            new_end = other_segment.start
         else:
            new_end = clicked_segment.end

      new_segment = Segment(
         transcription = clicked_segment.transcription,
         start = new_start,
         end = new_end,
         text = ' ',
      )

      new_segment.save()

      # Create segment from template part
      rendered_segment = render_to_string('webui/_segment.html', {'segment': new_segment})
      data = { 'segment': rendered_segment }

      return JsonResponse(data, status=200)

   else:
      # Return segment list if ever implemented
      pass

   return JsonResponse({'message': 'bad request'}, status=400)


def api_segments_id(request, segment_id):
   """
   Handles API POST requests to update segments.

   Args:
      segment_id (int): ID of the segment to update.

   Returns:
      JsonResponse: JSON message and status of the result..
   """
   if 'X-Requested-With' not in request.headers or request.headers['X-Requested-With'] != 'XMLHttpRequest':
      return JsonResponse({'message': 'malformed header'}, status=400)

   try:
      segment = Segment.objects.get(pk=segment_id)
   except Segment.DoesNotExist:
      return JsonResponse({'message': f'segment {segment_id} not found'}, status=404)

   if(request.method == 'POST'):
      data = json.loads(request.body)
      field = data.get('field')
      value = data.get('value', '')
      method = data.get('method')
      if isinstance(value, (str)):
         value = value.strip()

      if method == 'DELETE':
         segment.delete()
         return HttpResponse(status=204)

      # Allow value of speaker to be an empty string
      if field and value is not None:
         if (field == 'start' or field == 'end') and not is_float(value):
            return JsonResponse({'message': f'{field} value is not numeric'}, status=400)

         setattr(segment, field, value)
         segment.save(update_fields=[field])
         return JsonResponse({'message': 'sucess'}, status=200)

   return JsonResponse({'message': 'bad request'}, status=400)
