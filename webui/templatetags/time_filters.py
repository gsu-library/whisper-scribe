from django import template

from webui.utils import format_seconds


register = template.Library()

@register.filter(name='seconds_to_segment_time')
def seconds_to_segment_time(value):
   return format_seconds(value, segment_time=True)
