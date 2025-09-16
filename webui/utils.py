from django.conf import settings
from django.core.cache import cache

from pathlib import Path
import subprocess
import uuid


def is_float(number):
   """
   Checks if a given number can be converted to a float.

   Args:
      number: The value to check.

   Returns:
      bool: True if the number can be converted to a float, False otherwise.
   """
   try:
      float(number)
      return True
   except ValueError:
      return False


def get_version(prefix = ''):
   """
   Retrieves the version from the README.md file and caches it.

   Args:
      prefix (str): A string to prepend to the version number.

   Returns:
      str: The version string with the optional prefix.
   """
   README = 'README.md'
   CACHE_NAME = 'readme_version'
   CACHE_TIMEOUT = 300
   version = cache.get(CACHE_NAME)

   if version:
      return prefix + version

   try:
      with open(settings.BASE_DIR / README, 'r') as f:
         for line in f:
            if line.startswith('Version:'):
               version = line[len('Version:'):].strip()
               cache.set(CACHE_NAME, version, CACHE_TIMEOUT)
               return prefix + version
   except FileNotFoundError:
      cache.set(CACHE_NAME, '', CACHE_TIMEOUT)
      print(f'README file not found.')

   cache.set(CACHE_NAME, '', CACHE_TIMEOUT)
   return prefix


def format_seconds(seconds, always_include_hours = False, decimal_marker = '.', include_mill = True, segment_time = False):
   """
   Formats a number of seconds into a time string (e.g., HH:MM:SS.mmm).

   Args:
      seconds (float): The number of seconds to format.
      always_include_hours (bool): If True, always includes the hours part even if it's 0.
      decimal_marker (str): The character to use for the decimal point.
      include_mill (bool): If True, includes milliseconds in the output.
      segment_time (bool): If True, formats the time for segments (M:SS.mmm or H:MM:SS.mmm).

   Returns:
      str: The formatted time string.
   """
   if not isinstance(seconds, (int, float)):
      return seconds

   milliseconds = round(seconds * 1000.0)
   hours = milliseconds // 3_600_000
   milliseconds -= hours * 3_600_000
   minutes = milliseconds // 60_000
   milliseconds -= minutes * 60_000
   seconds = milliseconds // 1_000
   milliseconds -= seconds * 1_000

   if segment_time:
      if hours:
         total = f'{hours:d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}'
      else:
         total = f'{minutes:d}:{seconds:02d}.{milliseconds:03d}'
   else:
      hours_marker = f'{hours:02d}:' if always_include_hours or hours > 0 else ''
      mills = f'{decimal_marker}{milliseconds:03d}' if include_mill else ''
      total = f'{hours_marker}{minutes:02d}:{seconds:02d}{mills}'

   return total


def get_file_duration(file):
   """
   Gets the duration of a media file using ffprobe.

   Args:
      file (str|Path): The path to the media file.

   Returns:
      float: The duration of the file in seconds.

   Raises:
      Exception: If ffprobe fails to get the duration.
   """
   if not file: return None

   cmd = [
      'ffprobe',
      '-v',
      'error',
      '-show_entries',
      'format=duration',
      '-of',
      'default=noprint_wrappers=1:nokey=1',
      file,
   ]

   result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

   if result.returncode == 0:
      return float(result.stdout)
   else:
      raise Exception(f'Error getting file duration: {result.stderr}')


def extract_audio_to_wav(input_file):
   """
   This function uses ffmpeg to convert a media file to a WAV format and saves it to a
   temporary directory.

   Args:
      input_file (str|Path): The path to the input media file.

   Returns:
      Path: The path to the newly created WAV file, or None if an error occurred.
   """
   if not input_file: return None

   temp_dir = Path(settings.MEDIA_ROOT).joinpath('temp')

   try:
      temp_dir.mkdir(exist_ok=True)
   except Exception as e:
      print(f'Error creating temporary directory: {e}')
      return None

   try:
      random_filename = str(uuid.uuid4()) + '.wav'
      output_file = temp_dir.joinpath(random_filename)

      cmd = [
         'ffmpeg',
         '-i', input_file,
         '-acodec', 'pcm_s16le',
         '-ac', '1',
         output_file
      ]

      subprocess.run(cmd, stderr=subprocess.PIPE, check=True)
      return output_file
   except subprocess.CalledProcessError as e:
      print(f'FFmpeg error: {e.stderr.decode()}')
      return None
   except Exception as e:
      print(f'Error: {e}')
      return None
