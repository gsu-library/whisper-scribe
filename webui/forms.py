from django import forms
from django.core.exceptions import ValidationError
# TODO: check https://docs.djangoproject.com/en/5.0/topics/forms/#working-with-form-templates


# Class: TranscriptionForm
class TranscriptionForm(forms.Form):
   # Entire model list:
   # tiny, tiny.en, base, base.en, small, small.en, distil-small.en, medium, medium.en, distil-medium.en, large-v1, large-v2, large-v3, large, distil-large-v2,  distil-large-v3
   upload_file = forms.FileField(required=False)
   upload_url = forms.URLField(required=False)
   model = forms.ChoiceField(
      choices=(
         ('tiny', 'tiny'),
         ('base', 'base'),
         ('small', 'small'),
         ('medium', 'medium'),
         ('large-v1', 'large-v1'),
         ('large-v2', 'large-v2'),
         ('large-v3', 'large-v3'),
      ),
      initial='base',
   )
   diarize = forms.BooleanField(required=False)


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

