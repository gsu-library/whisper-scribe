from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

from .forms import *
from .models import *
from .media import *

import mimetypes
from django_q.tasks import async_task


# Function: index
def index(request):
   form = TranscriptionForm()

   current_statuses = []
   for transcription in Transcription.objects.all().order_by('submitted'):
      current_status = transcription.current_status()
      if current_status and current_status.status in [TranscriptionStatus.PENDING, TranscriptionStatus.PROCESSING]:
         current_statuses.append(current_status)

   # Form submission
   if request.method == 'POST':
      form = TranscriptionForm(request.POST, request.FILES)

      if form.is_valid():
         upload_url = None

         saved_transcription = Transcription(
            meta = {
               'model': form.cleaned_data['model'],
               'language': form.cleaned_data['language'],
               'hotwords': form.cleaned_data['hotwords'],
               'vad_filter': form.cleaned_data['vad_filter'],
               'max_segment_length': form.cleaned_data['max_segment_length'],
               'max_segment_time': form.cleaned_data['max_segment_time'],
            },
         )
         saved_transcription.save()

         # Create transcription statuses
         if form.cleaned_data['upload_url']:
            TranscriptionStatus(transcription = saved_transcription, process = TranscriptionStatus.DOWNLOADING, status = TranscriptionStatus.PENDING).save()

         TranscriptionStatus(transcription = saved_transcription, process = TranscriptionStatus.TRANSCRIBING, status = TranscriptionStatus.PENDING).save()

         if form.cleaned_data['diarize']:
            TranscriptionStatus(transcription = saved_transcription, process = TranscriptionStatus.DIARIZING, status = TranscriptionStatus.PENDING).save()
         # End create transcription statuses

         if request.FILES:
            saved_transcription.title = Path(request.FILES['upload_file'].name).stem
            saved_transcription.upload_file = form.cleaned_data['upload_file']
            saved_transcription.save(update_fields=['title', 'upload_file'])
         # Download media
         elif form.cleaned_data['upload_url']:
            upload_url = form.cleaned_data['upload_url']
            saved_transcription.title = upload_url
            saved_transcription.save(update_fields=['title'])
         else:
            return

         if settings.USE_DJANGO_Q:
            async_task(process_submission, saved_transcription.id, upload_url, form.cleaned_data['diarize'])
         else:
            process_submission(saved_transcription.id, upload_url, form.cleaned_data['diarize'])

         return HttpResponseRedirect(reverse('webui:index'))

   return render(request, 'webui/index.html', {'form': form, 'statuses': current_statuses})


# Function: view_transcription
def view_transcription(request, transcription_id):
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   segments = transcription.segments.all()
   return render(request, 'webui/view.html', {'segments': segments})


# Function: list_transcriptions
def list_transcriptions(request):
   transcriptions = Transcription.objects.all()
   return render(request, 'webui/list.html', {'transcriptions': transcriptions})


# Function: edit_transcription
def edit_transcription(request, transcription_id):
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   segments = transcription.segments.all()
   speakers = set(segments.exclude(speaker__exact='').values_list('speaker', flat=True).distinct())

   if request.POST:
      speaker_old = request.POST.get('speaker-old')
      speaker_new = request.POST.get('speaker-new', '').strip()

      if speaker_old and speaker_new:
         segments.filter(speaker=speaker_old).update(speaker=speaker_new)

      return HttpResponseRedirect(reverse('webui:edit', args=[transcription_id]))

   type = 'video'

   file_mimetype = mimetypes.guess_type(str(transcription.upload_file))[0]

   if file_mimetype and file_mimetype.startswith('audio'):
      type = 'audio'

   properties = {
      'id': transcription.id,
      'title': transcription.title,
      'description': transcription.description,
      'notes': transcription.notes,
      'file': transcription.upload_file,
      'type': type,
      'speakers': speakers,
   }

   return render(request, 'webui/edit.html', {'segments': segments, 'properties': properties})


# Function: delete_transcription
def delete_transcription(request, transcription_id):
   transcription = get_object_or_404(Transcription, pk=transcription_id)
   transcription.delete()

   return HttpResponseRedirect(reverse('webui:list'))
