from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
# TODO: check https://docs.djangoproject.com/en/5.0/topics/forms/#working-with-form-templates


# Create choices tuples for choice model.
def create_model_choices():
   choices = []

   for model in settings.WHISPER_MODELS:
      choices.append((model, model))

   return tuple(choices)


# Class: TranscriptionForm
class TranscriptionForm(forms.Form):
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
   # TODO: check out form-floating labels later
   def __init__(self, *args, **kwargs):
      super(TranscriptionForm, self).__init__(*args, **kwargs)

      for visible in self.visible_fields():
         if visible.field.widget.input_type == 'select':
            visible.field.widget.attrs['class'] = 'form-select'
         elif visible.field.widget.input_type == 'checkbox':
            visible.field.widget.attrs['class'] = 'form-check-input'
         else:
            visible.field.widget.attrs['class'] = 'form-control'


   # Validation for providing one the two fields: upload_file and upload_url.
   def clean(self):
      cleaned_data = super().clean()
      upload_file = cleaned_data.get('upload_file')
      upload_url = cleaned_data.get('upload_url')

      if not upload_file and not upload_url:
         # raise ValidationError('You must either upload a file or provide an upload URL.')
         msg = 'You must either upload a file or provide an upload URL.'
         self.add_error('upload_file', msg)
         self.add_error('upload_url', msg)
