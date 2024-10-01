from django.contrib import admin
from django.utils.text import Truncator

from .models import Transcription, Segment


# Class: TranscriptionAdmin
class TranscriptonAdmin(admin.ModelAdmin):
   _max_chars = 200
   list_display = ('title', 'upload_file', 'model', 'get_segments', 'get_diarization', 'submitted')

   def get_segments(self, obj):
      trunc = Truncator(obj.base_segments)
      return trunc.chars(self._max_chars)

   def get_diarization(self, obj):
      trunc = Truncator(obj.diarization)
      return trunc.chars(self._max_chars)

   get_segments.short_description = 'base segments'
   get_diarization.short_description = 'diarization'


# Class: SegmentAdmin
class SegmentAdmin(admin.ModelAdmin):
   pass


admin.site.register(Transcription, TranscriptonAdmin)
admin.site.register(Segment, SegmentAdmin)
