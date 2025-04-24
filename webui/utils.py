from django.conf import settings

from pathlib import Path
import subprocess
import uuid


# Function: is_float
def is_float(number):
   try:
      float(number)
      return True
   except ValueError:
      return False


# Function: format_seconds
def format_seconds(seconds, always_include_hours = False, decimal_marker = '.', include_mill = True, segment_time = False):
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


# Function: get_file_duration
def get_file_duration(file):
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


# Function extract_audio_to_wav
def extract_audio_to_wav(input_file):
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
