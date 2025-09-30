from django.db import models

from datetime import datetime


class Transcription(models.Model):
   """
   This model represents a transcription process and its associated metadata, statuses,
   and file uploads.

   Attributes:
      title (str): The title of the transcription.
      description (str): A brief description of the transcription. Defaults to an empty string.
      notes (str): Additional notes related to the transcription. Defaults to an empty string.
      upload_file (FileField): The file associated with the transcription.
      word_list (JSONField): A JSON field to store a list of words related to the transcription. Can be null.
      diarization (JSONField): A JSON field to store diarization data. Can be null.
      meta (JSONField): A JSON field to store additional metadata. Can be null.
      submitted (DateTimeField): The timestamp when the transcription was submitted. Automatically set to the current time.
   """
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
      """
      Returns the most relevant status for the transcription.

      The hierarchy of status importance is FAILED (not cancelled), PROCESSING, PENDING,
      COMPLETED, and FAILED (cancelled).
      """
      # If failed, exclude processes that never started
      status = self.statuses.filter(status=TranscriptionStatus.FAILED, start_time__isnull=False).order_by('start_time').first()
      if status: return status
      # If processing, start time should be present if process statis is processing
      status = self.statuses.filter(status=TranscriptionStatus.PROCESSING).order_by('start_time').first()
      if status: return status
      # If pending, must order by process number
      status = self.statuses.filter(status=TranscriptionStatus.PENDING).order_by('process').first()
      if status: return status
      # If completed, get last completed
      status = self.statuses.filter(status=TranscriptionStatus.COMPLETED).order_by('-start_time').first()
      if status: return status
      # If a process was cancelled
      status = self.statuses.filter(status=TranscriptionStatus.FAILED, start_time__isnull=True).order_by('start_time').first()
      if status: return status

   def get_status_of(self, process):
      """
      Retrieve the status of a given process.

      Args:
          process: The process whose status is to be retrieved.

      Returns:
          The status of the specified process if it exists, otherwise None.
      """
      try:
         return self.statuses.get(process=process)
      except TranscriptionStatus.DoesNotExist:
         return None

   def fail_incomplete_statuses(self, error_message='Transcription processing failed.', processes_to_fail=None):
      """
      Marks incomplete transcription statuses as failed.

      Args:
         error_message (str): The error message to be stored with the failed status.
         processes_to_fail (list): A list of process IDs to mark as failed. If None, all
            incomplete statuses will be failed.
      """
      if processes_to_fail is None:
         incomplete_statuses = self.statuses.exclude(status=TranscriptionStatus.COMPLETED)
      else:
         incomplete_statuses = self.statuses.exclude(status=TranscriptionStatus.COMPLETED).filter(process__in=processes_to_fail)

      incomplete_statuses.update(status=TranscriptionStatus.FAILED, error_message=error_message, end_time=datetime.now())

   def fail_pending_statuses(self, error_message='Transcription processing failed.'):
      """
      Marks pending transcription statuses as failed.

      Args:
         error_message (str): The error message to be stored with the failed status.
      """
      self.statuses.filter(status=TranscriptionStatus.PENDING).update(
         status=TranscriptionStatus.FAILED,
         error_message=error_message,
         end_time=datetime.now())


class Segment(models.Model):
   """
   Represents a single segment of a transcription.

   Attributes:
      transcription (int): The transcription ID (foreign key) this segment belongs to.
      start (float): The start time of segment (in seconds).
      end (float): The end time of segment (in seconds).
      text (str): The text spoken during segment.
      speaker (str): The speaker of the segment. Can be blank.
      probability (float): The accuracy of the segment. Defaults to null.
   """
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


class TranscriptionStatus(models.Model):
   """
   Tracks the status of the different transcription processes.

   Each transcription can have multiple statuses, corresponding to different stages like
   downloading, transcribing, and diarizing.

   Attributes:
      transcription (int): The transcription ID (foreign key) this status belongs to.
      process (int): The process this is tracking.
      status (int): The status of the process.
      start_time (DateTimeField): When the process started. Can be null.
      end_time (DateTimeField): When the process completed. Can be null.
      error_message (str): An error message associated with this status. Can be null.
   """
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
      """
      Returns a string representation of the process and its status.
      """
      process = dict(TranscriptionStatus.PROCESS_CHOICES).get(self.process, 'unknown process')
      status = dict(TranscriptionStatus.STATUS_CHOICES).get(self.status, 'unknown status')
      return f'{process} - {status}'

   def print_process(self):
      """
      Returns the string representation of the process.
      """
      process = dict(TranscriptionStatus.PROCESS_CHOICES).get(self.process, 'unknown process')
      return f'{process}'

   def print_status(self):
      """
      Returns the string representation of the status.
      """
      status = dict(TranscriptionStatus.STATUS_CHOICES).get(self.status, 'unknown status')
      return f'{status}'

   class Meta:
      verbose_name_plural = 'transcription statuses'
