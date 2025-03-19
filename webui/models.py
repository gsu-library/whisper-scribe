from django.db import models


# Class: Transcription
class Transcription(models.Model):
   title = models.CharField(max_length=255)
   description = models.TextField(default='')
   notes = models.TextField(default='')
   upload_file = models.FileField(max_length=255)
   word_list = models.JSONField(null=True, default=None)
   diarization = models.JSONField(null=True, default=None)
   meta = models.JSONField(null=True, default=None)
   submitted = models.DateTimeField(auto_now=True)

   def __str__(self):
      return f'{self.title}'


# Class: Segment
# TODO: set related_name on foreign key and update references?
# https://docs.djangoproject.com/en/5.1/topics/db/queries/#backwards-related-objects
class Segment(models.Model):
   transcription = models.ForeignKey(Transcription, on_delete=models.CASCADE)
   start = models.FloatField()
   end = models.FloatField()
   text = models.TextField()
   speaker = models.CharField(max_length=255, default='')
   probability = models.FloatField(null=True, default=None)

   def __str__(self):
      return f'{self.text}'

   class Meta:
      ordering = ['start', 'end']


# Class: ProcessStatus
class ProcessStatus(models.Model):
   PROCESS_NAME = [
      ('downloading', 'Downloading'),
      ('transcribing', 'Transcribing'),
      ('diarizing', 'Diarizing')
   ]
   STATUS_CHOICES = [
      ('pending', 'Pending'),
      ('processing', 'Processing'),
      ('completed', 'Completed'),
      ('failed', 'Failed'),
    ]
   transcription = models.ForeignKey(Transcription, on_delete=models.CASCADE, related_name='process_statuses')
   process_name = models.CharField(max_length=50, choices=PROCESS_NAME)
   status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
   start_time = models.DateTimeField(auto_now_add=True)
   end_time = models.DateTimeField(null=True, default=None)
   error_message = models.TextField(null=True, default=None)
   # TODO: what do we do with multiple error messages or do we have multiple processes per transcription?

   def __str__(self):
      return f'{self.process_name} - {self.status}'

   # TODO: do we set the meta for ordering? sort by end_time, start_time, id?
