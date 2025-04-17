from django import template

import math


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

      output = f'{hours}:' if hours > 0 else ''

      if hours:
         output = output + f'{minutes:02d}:'
      else:
         output = f'{minutes}:'

      output = output + f'{seconds:02d}.{milliseconds:03d}'
      # return f'{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}'
      return output

   return value
