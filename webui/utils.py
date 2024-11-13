import subprocess
import tempfile
import os
import uuid


# Function: is_float
def is_float(number):
   try:
      float(number)
      return True
   except ValueError:
      return False


# Function: format_timestamp
def format_timestamp(seconds: float, always_include_hours: bool = False, decimal_marker: str = '.', include_mill = True):
   assert seconds >= 0, 'non-negative timestamp expected'
   milliseconds = round(seconds * 1000.0)

   hours = milliseconds // 3_600_000
   milliseconds -= hours * 3_600_000

   minutes = milliseconds // 60_000
   milliseconds -= minutes * 60_000

   seconds = milliseconds // 1_000
   milliseconds -= seconds * 1_000

   hours_marker = f'{hours:02d}:' if always_include_hours or hours > 0 else ''
   mills = f'{decimal_marker}{milliseconds:03d}' if include_mill else ''
   return (f'{hours_marker}{minutes:02d}:{seconds:02d}{mills}')


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
      # TODO: may not want exception
      raise Exception(f'Error getting file duration: {result.stderr}')


def extract_audio_to_wav(input_file):
    try:
        # Generate a unique random filename
        random_filename = str(uuid.uuid4()) + '.wav'

        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        output_file = os.path.join(temp_dir, random_filename)

        # Construct the FFmpeg command
        ffmpeg_cmd = [
            'ffmpeg',              # FFmpeg executable
            '-i', input_file,    # Input file path
            '-acodec', 'pcm_s16le',  # Audio codec (WAV)
            '-ac', '1',           # Number of audio channels (mono)
            # '-ar', '48000',
            output_file           # Output file path
        ]

        # Execute the FFmpeg command using subprocess
        subprocess.run(ffmpeg_cmd, stderr=subprocess.PIPE, check=True)

        return output_file

    except subprocess.CalledProcessError as e:
        print(f'FFmpeg error: {e.stderr.decode()}')  # Print FFmpeg's error output
        return None
    except Exception as e:
        print(f'Error: {e}')
        return None


def get_sample_rate(input_file):
    try:
        # Construct the FFprobe command
        ffprobe_cmd = [
            'ffprobe',
            '-v', 'error',  # Suppress verbose output
            '-select_streams', 'a:0',  # Select the first audio stream
            '-show_entries', 'stream=sample_rate',  # Show only the sample rate
            '-of', 'default=noprint_wrappers=1:nokey=1',  # Output only the value
            input_file
        ]

        # Execute the FFprobe command and capture the output
        result = subprocess.run(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        sample_rate = int(result.stdout.decode().strip())
        return sample_rate

    except subprocess.CalledProcessError as e:
        print(f'FFprobe error: {e.stderr.decode()}')
        return None
    except Exception as e:
        print(f'Error: {e}')
        return None
