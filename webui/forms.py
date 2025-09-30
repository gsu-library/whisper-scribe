from django import forms
from django.conf import settings


def create_model_choices():
   """
   Helper function that returns tuples of model choices defined in the settings.

   Returns:
      tuple: A tuple of (model, model) pairs for available Whisper models.
   """
   choices = []

   for model in settings.WHISPER_MODELS:
      choices.append((model, model))

   return tuple(choices)


class TranscriptionForm(forms.Form):
   """
   A Django form for handling transcription requests.

   Fields:
      upload_file: Optional file upload field for the audio file.
      upload_url: Optional URL field for the audio file.
      model: Choice field for selecting the transcription model.
      language: Optional field for specifying the language of the audio.
      diarize: Optional boolean field to enable speaker diarization.
      hotwords: Optional field for providing hint phrases to the model.
      vad_filter: Optional boolean field to enable voice activity detection.
      max_segment_length: Optional field for specifying the maximum segment length.
      max_segment_time: Optional field for specifying the maximum segment time.

   Validation:
      Ensures that at least one of 'upload_file' or 'upload_url' is provided.
   """
   upload_file = forms.FileField(required=False)
   upload_url = forms.URLField(required=False)
   model = forms.ChoiceField(
      choices=create_model_choices(),
      initial=settings.WHISPER_MODEL_DEFAULT,
   )
   language = forms.CharField(required=False, initial=settings.WHISPER_LANGUAGE)
   diarize = forms.BooleanField(required=False)
   hotwords = forms.CharField(
      required=False,
      help_text='Hotwords/hint phrases to provide the model with.',
   )
   vad_filter = forms.BooleanField(
      required=False,
      label='VAD filter',
      help_text='Enable the voice activity detection (VAD) to filter out parts of the audio without speech.',
   )
   max_segment_length = forms.IntegerField(required=False, initial=settings.MAX_SEGMENT_LENGTH)
   max_segment_time = forms.IntegerField(required=False, initial=settings.MAX_SEGMENT_TIME)


   # Add form-control class to form fields.
   def __init__(self, *args, **kwargs):
      """
      Initializes the TranscriptionForm class and applies custom CSS classes to form
      widgets based on their input type.
      """
      super(TranscriptionForm, self).__init__(*args, **kwargs)

      for visible in self.visible_fields():
         if visible.field.widget.input_type == 'select':
            visible.field.widget.attrs['class'] = 'form-select'
         elif visible.field.widget.input_type == 'checkbox':
            visible.field.widget.attrs['class'] = 'form-check-input'
         else:
            visible.field.widget.attrs['class'] = 'form-control'


   def clean(self):
      """
      Perform custom validation to ensure that at least one of 'upload_file' or
      'upload_url' is provided in the form data. If neither is provided, validation
      errors are added to both fields.
      """
      cleaned_data = super().clean()
      upload_file = cleaned_data.get('upload_file')
      upload_url = cleaned_data.get('upload_url')

      if not upload_file and not upload_url:
         msg = 'You must either upload a file or provide an upload URL.'
         self.add_error('upload_file', msg)
         self.add_error('upload_url', msg)
