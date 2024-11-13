import subprocess


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
      raise Exception(f"Error getting file duration: {result.stderr}")
