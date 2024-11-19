from django.db import models


# Class: transcription
class Transcription(models.Model):
   title = models.CharField(max_length=255)
   description = models.TextField(default='')
   notes = models.TextField(default='')
   upload_file = models.FileField(max_length=255)
   # TODO: make sure file paths + names are not longer than upload_file max_length
   word_list = models.JSONField(null=True, default=None)
   diarization = models.JSONField(null=True, default=None)
   meta = models.JSONField(null=True, default=None)
   submitted = models.DateTimeField(auto_now=True)


# Class: segment
class Segment(models.Model):
   transcription = models.ForeignKey(Transcription, on_delete=models.CASCADE)
   start = models.FloatField()
   end = models.FloatField()
   text = models.TextField()
   speaker = models.CharField(max_length=255, default='')
   probability = models.FloatField(null=True, default=None)

   class Meta:
      ordering = ['start', 'end']
