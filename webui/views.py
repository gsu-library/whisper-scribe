from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

from .forms import *
from .models import *
from .media import *

import mimetypes


# Function: index
def index(request):
   form = TranscriptionForm()
   transcriptions = Transcription.objects.all()

   # Form submission
   if request.method == 'POST':
      form = TranscriptionForm(request.POST, request.FILES)

      if form.is_valid():
         async_task(process_submission, request, form)
         return HttpResponseRedirect(reverse('webui:index'))

   return render(request, 'webui/index.html', {'form': form, 'transcriptions': transcriptions})


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

   return HttpResponseRedirect(reverse('webui:index'))
