from django.http import HttpResponse, JsonResponse

from .models import *

import json


# Function: is_float
def is_float(number):
   try:
      float(number)
      return True
   except ValueError:
      return False


# Function: api_transcriptions_id
def api_transcriptions_id(request, transcription_id):
   if 'X-Requested-With' not in request.headers or request.headers['X-Requested-With'] != 'XMLHttpRequest':
      return JsonResponse({'message': 'malformed header'}, status=400)

   try:
      transcription = Transcription.objects.get(pk=transcription_id)
   except Transcription.DoesNotExist:
      return JsonResponse({'message': f'transcripton {transcription_id} not found'}, status=404)

   if(request.method == 'POST'):
      data = json.loads(request.body)
      # TODO: use setattr instead of hard picking title?
      title = data.get('value')

      if title:
         transcription.title = title
         transcription.save(update_fields=['title'])
         return JsonResponse({'message': 'success'})

   return JsonResponse({'message': 'bad request'}, satus=400)


# Function: api_segments_id
def api_segments_id(request, segment_id):
   if 'X-Requested-With' not in request.headers or request.headers['X-Requested-With'] != 'XMLHttpRequest':
      return JsonResponse({'message': 'malformed header'}, status=400)

   try:
      segment = Segment.objects.get(pk=segment_id)
   except Segment.DoesNotExist:
      return JsonResponse({'message': f'segment {segment_id} not found'}, status=404)

   if(request.method == 'POST'):
      data = json.loads(request.body)
      field = data.get('field')
      value = data.get('value', '').strip()
      method = data.get('method')

      if method == 'DELETE':
         segment.delete()
         return HttpResponse(status=204)

      if field and value:
         if (field == 'start' or field == 'end') and not is_float(value):
            return JsonResponse({'message': f'{field} value is not numeric'}, status=400)

         setattr(segment, field, value)
         segment.save(update_fields=[field])
         return JsonResponse({'message': 'sucess'}, status=200)

   return JsonResponse({'message': 'bad request'}, status=400)
