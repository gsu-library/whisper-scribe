from django import template

from ..utils import format_seconds, get_version


register = template.Library()

# Function: seconds_to_segment_time
@register.filter(name='seconds_to_segment_time')
def seconds_to_segment_time(value):
   return format_seconds(value, segment_time=True)


# Function: version
@register.filter(name='version')
def version(prefix = ''):
   return get_version(prefix)


# Function: spacify
@register.filter(name='spacify')
def spacify(value):
   return value.replace('_', ' ')
