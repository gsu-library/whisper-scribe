from django.contrib import admin
from django.utils.text import Truncator

from .models import Transcription, Segment


# Class: TranscriptionAdmin
class TranscriptonAdmin(admin.ModelAdmin):
   _max_chars = 200
   list_display = ('title', 'get_description', 'get_notes', 'upload_file', 'meta', 'submitted')

   def get_description(self, obj):
      trunc = Truncator(obj.description)
      return trunc.chars(self._max_chars)

   def get_notes(self, obj):
      trunc = Truncator(obj.notes)
      return trunc.chars(self._max_chars)

   get_description.short_description = 'description'
   get_notes.short_description = 'notes'


# Class: SegmentAdmin
class SegmentAdmin(admin.ModelAdmin):
   pass


admin.site.register(Transcription, TranscriptonAdmin)
admin.site.register(Segment, SegmentAdmin)
