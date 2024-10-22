# WhisperScribe
Code Repository: https://github.com/gsu-library/whisper-scribe  
Author: Matt Brooks <mbrooks34@gsu.edu>  
Date Created: 2024-05-21  
License: [GPLv3](LICENSE)  
Version: 0.0.1

## Description
WhisperScribe is a Django-powered web application that simplifies audio analysis by using AI for speech recognition (Faster Whisper) and speaker diarization (Pyannote.Audio). Users can upload or link media, generate accurate transcripts with speaker identification, and easily edit the results. This project also leverages CUDA support for quicker processing.

## Requirements
- Python >= v3.10
- FFmpeg
- The python packages in [requirements.txt](requirements.txt)
- NVIDIA drivers (if using CUDA)

## Installation
The following installation instructions are based on a Linux install. This mostly works in a Windows environment with some extra configuration.

1. [Install Python](https://wiki.python.org/moin/BeginnersGuide/Download) v3.10 or greater.
1. [Install FFmpeg](https://www.ffmpeg.org/).
1. Either clone the WhisperScribe git repository or download the source code from the latest release. Move/extract the files in a location that is not being served by a web server.
1. Create a Python virtual environment inside the WhisperScribe folder - [venv](https://docs.python.org/3/library/venv.html) is recommended.
1. Activate the Python virtual envrionment (stay in the virtual environment for the remainder of the steps). Once activated install the pip requirements: `pip install -r requirements.txt`.
1. Copy the core/settings.sample.py file to core/settings.py and [configure the settings file](#configuring-the-settings-file). If wanting to use a database other than SQLite configure it now (see [Django's databases documentation](https://docs.djangoproject.com/en/5.1/ref/databases/)).
1. Run Django database migrations: `python manage.py migrate`.
1. Create the cache table: `python manage.py createcachetable`.
1. Create Django admin user (optional): `python manage.py createsuperuser`.
1. [Install NVIDIA drivers](#nvidia-drivers) if using CUDA (optional).

### Configuring the Settings File
The SECRET_KEY and ALLOWED_HOST fields must be configured before running WhisperScribe. It is recommended to also take a look at the rest of the configurations in the settings file. See [Django settings reference](https://docs.djangoproject.com/en/5.1/ref/settings/) for additional information. If troubleshooting is needed for setup/configuration DEBUG can be enabled. **DO NOT LEAVE THIS ENABLED IN A PRODUCTION ENVIRONMENT!**

**SECRET_KEY** - REQUIRED  
Run the following command while within the WhisperScribe Python virtual environment to generate a secret key: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`

**ALLOWED_HOSTS** - REQUIRED  
A list of strings representing the host/domain names that this Django site can serve.

CSRF_TRUSTED_ORIGINS  
May be needed depending on the web server setup. See [CSRF trusted origins](https://docs.djangoproject.com/en/5.1/ref/settings/#csrf-trusted-origins) for more information.

HUGGING_FACE_TOKEN  
This is required to use diarization. In order to create a token you must:
1. Accept [pyannote/segmentation-3.0](https://hf.co/pyannote/segmentation-3.0) user conditions,
1. accept [pyannote/speaker-diarization-3.1](https://hf.co/pyannote/speaker-diarization-3.1) user conditions,
1. and create an access token at [hf.co/settings/tokens](https://hf.co/settings/tokens).

UPPERCASE_SPEAKER_NAMES  
If speaker names should be in uppercase or not in file downloads.

MAX_SEGMENT_LENGTH  
The default max number of characters per segment.

MAX_SEGMENT_TIME  
The default max length of segments in seconds.

WHISPER_LANGUAGE  
The default for the langauge spoken in the audio. Set to None or '' for auto detection as a default.

WHISPER_MODELS  
The list of models available to Whisper (tiny.en, tiny, base.en, base, small.en, small, medium.en, medium, large-v1, large-v2, large-v3, large, distil-large-v2, distil-medium.en, distil-small.en, distil-large-v3). See <https://huggingface.co/Systran>.

WHISPER_MODEL_DEFAULT  
The default whisper model to show (from the list of WHISPER_MODELS).

USE_DJANGO_Q  
Whether to use Django Q or not. This may cause issues in a Windows environemnt. If disabled the WhisperScribe interface will hang while processing audio.

DATABASES  
Configure what kind of database you want to use. The default is SQLite. See <https://docs.djangoproject.com/en/5.1/ref/settings/#databases> and <https://docs.djangoproject.com/en/5.1/ref/databases/>.

TIME_ZONE  
Set to your local time zone.

### NVIDIA Drivers
The NVIDIA drivers available will depend on the OS and the video card installed. Ubuntu provides a [helpful article](https://documentation.ubuntu.com/server/how-to/graphics/install-nvidia-drivers/) that goes over searching for and installing NVIDIDA drivers. We have had success on our setup using the nvidida-driver-535-server package.

## Usage
### Manual Startup
Use the following commands to start the Django application and to run Django Q (within the Python virtual environment). If Django Q is disabled in the settings file the qcluster command does not need to be included.

```bash
python manage.py qcluster
python manage.py runserver
```

### Using Systmed Service
The systemd service can be used to run WhisperScribe on Linux operating systems. To set this up first copy both the whisperscribe.sample.service and whisperscribe-q.sample.service files to whisperscribe.service and whisperscribe-q.service respectively. Then edit both copied files to update the paths for WorkingDirectory, Environemnt, and ExecStart. For all three make sure the absolute path to WhisperScribe is used and for the Environment and ExecStart directives make sure the name of the virtual environment folder is correct. Once configured the files can be added to systemd with the following commands. You will need to edit the command to use the path to your instance of WhisperScribe.

```bash
sudo systemctl enable /path/to/whisperscribe/whisperscribe.service
sudo systemctl enable /path/to/whisperscribe/whisperscribe-q.service
```

Once both services are enabled WhisperScribe will start automatically during normal boot. WhisperScribe can also be started, stopped, and restarted with the following commands.

```bash
sudo systemctl start whisperscribe
sudo systemctl stop whisperscribe
sudo systemctl restart whisperscribe
```

## Additional Information
### Reverse Proxy Server
At some point you will possible want to reverse proxy a web server to WhisperScribe in order to use SSL certificates. [Apache](https://httpd.apache.org/docs/2.4/howto/reverse_proxy.html) provides a well documented guide on setting up a reverse proxy as does [NGINX](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/). Do note that if using a reverse proxy server some additional settings will need to be adjusted such as max post size.

## Updates
Check the [CHANGELOG](CHANGELOG.md) and release notes to see if there are any major changes with the core/settings.sample.py file, if a migration is required, or if the requirements.txt pip packages file has been updated.

It never hurts to run the commands below after an update (while in the Python virtual environment).

```bash
pip install -r requirements.txt
python manage.py migrate
```

## Developer Notes
The Django project folder is 'core' and the application folder is 'webui'.

## Dependencies
- [Faster-Whisper v1.0.3](https://github.com/SYSTRAN/faster-whisper)
- [Pyannote.Audio v3.3.2](https://github.com/pyannote/pyannote-audio)
- [YT-DLP v2024-9-27](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg](https://www.ffmpeg.org/)
- [Django v5.1.1](https://www.djangoproject.com/)
- [Django Cleanup v8.1.0](https://github.com/un1t/django-cleanup/)
- [Django Q2 v1.7.2](https://django-q2.readthedocs.io/en/master/)
- [NVIDIA cuBLAS v12.1](https://developer.nvidia.com/cublas)
- [NVIDIA cuDNN v8.9](https://developer.nvidia.com/cudnn)
- [Bootstrap v5.3.3](https://getbootstrap.com/)
- [Bootstrap Icons v1.11.3](https://icons.getbootstrap.com/)
