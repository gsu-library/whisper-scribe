from django.db import models


# Class: transcription
class Transcription(models.Model):
   title = models.CharField(max_length=255)
   upload_file = models.FileField(upload_to='webui/files/uploads/')
   # TODO: move upload to OR use MEDIA_ROOT & MEDIA_URL
   model = models.CharField(max_length=255)
   base_segments = models.JSONField(null=True, default=None)
   diarization = models.JSONField(null=True, default=None)
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
