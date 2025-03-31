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
class Segment(models.Model):
   transcription = models.ForeignKey(Transcription, on_delete=models.CASCADE, related_name='segments')
   start = models.FloatField()
   end = models.FloatField()
   text = models.TextField()
   speaker = models.CharField(max_length=255, default='')
   probability = models.FloatField(null=True, default=None)

   def __str__(self):
      return f'{self.text}'

   class Meta:
      ordering = ['start', 'end']


# Class: TranscriptionStatus
class TranscriptionStatus(models.Model):
   DOWNLOADING = 10
   TRANSCRIBING = 20
   DIARIZING = 30
   PENDING = 10
   PROCESSING = 20
   COMPLETED = 30
   FAILED = 40

   PROCESS_CHOICES = [
      (DOWNLOADING, 'Downloading'),
      (TRANSCRIBING, 'Transcribing'),
      (DIARIZING, 'Diarizing')
   ]
   STATUS_CHOICES = [
      (PENDING, 'Pending'),
      (PROCESSING, 'Processing'),
      (COMPLETED, 'Completed'),
      (FAILED, 'Failed')
   ]

   transcription = models.ForeignKey(Transcription, on_delete=models.CASCADE, related_name='statuses')
   process = models.IntegerField(choices=PROCESS_CHOICES)
   status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)
   start_time = models.DateTimeField(auto_now_add=True)
   end_time = models.DateTimeField(null=True, default=None)
   error_message = models.TextField(null=True, default=None)

   def __str__(self):
      return f'{self.process} - {self.status}'
