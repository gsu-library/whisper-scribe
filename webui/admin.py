from django.contrib import admin
from django.utils.text import Truncator

from .models import *


class TranscriptonAdmin(admin.ModelAdmin):
   """
   ModelAdmin class to customize the display of Transcription objects in the admin interface.
   """
   _max_chars = 200
   list_display = ('title', 'get_description', 'get_notes', 'upload_file', 'meta', 'submitted')

   def get_description(self, obj):
      """
      Truncates and returns description.
      """
      trunc = Truncator(obj.description)
      return trunc.chars(self._max_chars)

   def get_notes(self, obj):
      """
      Truncates and returns notes.
      """
      trunc = Truncator(obj.notes)
      return trunc.chars(self._max_chars)

   get_description.short_description = 'description'
   get_notes.short_description = 'notes'


class SegmentAdmin(admin.ModelAdmin):
   """
   ModelAdmin class to customize the display of Segment objects in the admin interface.
   """
   list_display = [field.name for field in Segment._meta.fields if field.name != 'id']


class TranscriptionStatusAdmin(admin.ModelAdmin):
   """
   ModelAdmin class to customize the display of TranscriptionStatus objects in the admin interface.
   """
   list_display = [field.name for field in TranscriptionStatus._meta.fields if field.name != 'id']


admin.site.register(Transcription, TranscriptonAdmin)
admin.site.register(Segment, SegmentAdmin)
admin.site.register(TranscriptionStatus, TranscriptionStatusAdmin)
