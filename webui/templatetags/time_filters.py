from django import template


register = template.Library()

@register.filter(name='seconds_to_segment_time')
def seconds_to_segment_time(value):
   if isinstance(value, (int, float)):
      total_milliseconds = int(value * 1000)
      milliseconds = total_milliseconds % 1000
      total_seconds = total_milliseconds // 1000
      seconds = total_seconds % 60
      total_minutes = total_seconds // 60
      minutes = total_minutes % 60
      hours = total_minutes // 60

      if hours:
         output = f'{hours}:{minutes:02d}:'
      else:
         output = f'{minutes}:'

      return output + f'{seconds:02d}.{milliseconds:03d}'

   return value
