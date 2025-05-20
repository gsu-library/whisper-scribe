from django.db import models

from datetime import datetime


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

   def current_status(self):
      # If failed, exclude processes that never started
      status = self.statuses.filter(status=TranscriptionStatus.FAILED, start_time__isnull=False).order_by('start_time').first()
      if status: return status
      # If processing, start time should be present if process statis is processing
      status = self.statuses.filter(status=TranscriptionStatus.PROCESSING).order_by('start_time').first()
      if status: return status
      # If pending, must order by process number
      status = self.statuses.filter(status=TranscriptionStatus.PENDING).order_by('process').first()
      if status: return status
      # Else completed, start time should be present
      return self.statuses.order_by('-start_time').first()

   def get_status_of(self, process):
      try:
         return self.statuses.get(process=process)
      except TranscriptionStatus.DoesNotExist:
         return None

   def fail_incomplete_statuses(self, error_message="Transcription processing failed.", processes_to_fail=None):
      if processes_to_fail is None:
         incomplete_statuses = self.statuses.exclude(status=TranscriptionStatus.COMPLETED)
      else:
         incomplete_statuses = self.statuses.exclude(status=TranscriptionStatus.COMPLETED).filter(process__in=processes_to_fail)

      incomplete_statuses.update(status=TranscriptionStatus.FAILED, error_message=error_message, end_time = datetime.now())


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
      (DOWNLOADING, 'downloading'),
      (TRANSCRIBING, 'transcribing'),
      (DIARIZING, 'diarizing')
   ]
   STATUS_CHOICES = [
      (PENDING, 'pending'),
      (PROCESSING, 'processing'),
      (COMPLETED, 'completed'),
      (FAILED, 'failed')
   ]

   transcription = models.ForeignKey(Transcription, on_delete=models.CASCADE, related_name='statuses')
   process = models.IntegerField(choices=PROCESS_CHOICES)
   status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)
   start_time = models.DateTimeField(null=True, default=None)
   end_time = models.DateTimeField(null=True, default=None)
   error_message = models.TextField(null=True, default=None)

   def __str__(self):
      process = dict(TranscriptionStatus.PROCESS_CHOICES).get(self.process, 'unknown process')
      status = dict(TranscriptionStatus.STATUS_CHOICES).get(self.status, 'unknown status')
      return f'{process} - {status}'

   def print_process(self):
      process = dict(TranscriptionStatus.PROCESS_CHOICES).get(self.process, 'unknown process')
      return f'{process}'

   def print_status(self):
      status = dict(TranscriptionStatus.STATUS_CHOICES).get(self.status, 'unknown status')
      return f'{status}'

   class Meta:
      verbose_name_plural = 'transcription statuses'
