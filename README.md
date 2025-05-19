# WhisperScribe
Code Repository: https://github.com/gsu-library/whisper-scribe  
Author: Matt Brooks <mbrooks34@gsu.edu>  
Date Created: 2024-05-21  
License: [GPLv3](LICENSE)  
Version: 1.6.0

## Description
WhisperScribe is a Django-powered web application that simplifies audio analysis by using AI for speech recognition (Faster Whisper) and speaker diarization (Pyannote.Audio). Users can upload or link media, generate accurate transcripts with speaker identification, and easily edit the results. This project also leverages CUDA support for quicker processing.

## Requirements
- Python v3.10.12
- FFmpeg
- Web Server
- NVIDIA drivers (if using CUDA)

## Installation
The following installation instructions are based on a Linux server install using Python v3.10.12.

1. [Install Python](https://wiki.python.org/moin/BeginnersGuide/Download). We recommend using version 3.10.12, as that is what this repository is built on. If you need to manage multiple Python versions, we suggest using [Pyenv](https://github.com/pyenv/pyenv).
1. [Install FFmpeg](https://www.ffmpeg.org/).
1. Install and [configure](#configuring-the-web-server) a web server for static and media file hosting. This can also be used as a reverse proxy server to proxy Gunicorn. Either [Apache](https://httpd.apache.org/) or [Nginx](https://nginx.org/) are recommended.
1. Either clone the WhisperScribe git repository or download the source code from the latest release. Move/extract the files in a location that is not being served by a web server.
1. Create a Python virtual environment inside the WhisperScribe folder - [venv](https://docs.python.org/3/library/venv.html) is recommended. Once created, activate and stay in the virtual environment for the remainder of the steps.
1. [Install the required Python packages](#installing-python-packages).
1. Copy the core/settings.sample.py file to core/settings.py and [configure the settings file](#configuring-the-settings-file). If wanting to use a database other than SQLite configure it now (see [Django's databases documentation](https://docs.djangoproject.com/en/5.1/ref/databases/)).
1. Run Django database migrations: `python manage.py migrate`.
1. Create the cache table: `python manage.py createcachetable`.
1. Move static files: `python manage.py collectstatic`.
1. [Install NVIDIA drivers](#nvidia-drivers) if using CUDA (optional).
1. Create Django admin user (optional): `python manage.py createsuperuser`.

### Installing Python Packages
To install the required Python packages it is recommended to use pip to install the freeze file that is used with this project: `pip install -r requirements-freeze.txt`. In some scenarios (not using Linux, different Python version, etc.) pip will fail to install the freeze file. If this is the case, installing the requirements.txt file should work: `pip install -r requirements.txt`.

### Configuring the Web Server
A web server will have to be configured to host static and media files used by WhisperScribe. Django has documentation on [how to deploy static files](https://docs.djangoproject.com/en/5.1/howto/static-files/deployment/).

### Configuring the Settings File
The SECRET_KEY and ALLOWED_HOST fields must be configured before running WhisperScribe. It is recommended to also take a look at the rest of the configurations in the settings file. See [Django settings reference](https://docs.djangoproject.com/en/5.1/ref/settings/) for additional information. If troubleshooting is needed for setup/configuration DEBUG can be enabled. **DO NOT LEAVE THIS ENABLED IN A PRODUCTION ENVIRONMENT!**

**SECRET_KEY** - REQUIRED  
Run the following command while within the WhisperScribe Python virtual environment to generate a secret key: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`

**ALLOWED_HOSTS** - REQUIRED  
A list of strings representing the host/domain names that this Django site can serve.

CSRF_TRUSTED_ORIGINS  
If using a reverse proxy to Gunicorn this will have to be set to Gunicorn's bind address. See [CSRF trusted origins](https://docs.djangoproject.com/en/5.1/ref/settings/#csrf-trusted-origins) for more information.

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

MEDIA_URL  
The URL that handles the media served from MEDIA_ROOT. This must end in a slash.

MEDIA_ROOT  
The absolute filesystem path to the directory that will store the media files.

STATIC_URL  
The URL to use when referring to the static files located in STATIC_ROOT. This must end in a slash.

STATIC_ROOT  
The absolute filesystem path to the directory where the collectstatic command will move static files for deployment.

### NVIDIA Drivers
The NVIDIA drivers available will depend on the OS and the video card installed. Ubuntu provides a [helpful article](https://documentation.ubuntu.com/server/how-to/graphics/install-nvidia-drivers/) that goes over searching for and installing NVIDIDA drivers. We have had success on our setup using the nvidida-driver-535-server package.

### MySQL Drivers
To connect WhisperScribe to a MySQL database a MySQL pip package, headers, and libraries will have to be installed. The mysqlclient pip package is recommended. The installation instructions can be found on the [mysqlclient pypi.org page](https://pypi.org/project/mysqlclient/).

## Usage
### Manual Startup
Use the following commands to start the Django application and to run Django Q (within the Python virtual environment). If Django Q is disabled in the settings file the qcluster command does not need to be included.

```bash
gunicorn core.wsgi
python manage.py qcluster
```

If wanting to run Gunicorn on a port other than 8000 the `-b` flag can be passed to set the bind address and port.

### Using Systemd Service
The systemd service can be used to run WhisperScribe on Linux operating systems. To set this up first copy both the whisperscribe.sample.service and whisperscribe-q.sample.service files to whisperscribe.service and whisperscribe-q.service respectively. Then edit both copied files to update the paths for WorkingDirectory, Environment, and ExecStart. For all three make sure the absolute path to WhisperScribe is used and for the Environment and ExecStart directives make sure the name of the virtual environment folder is correct. Also make sure the path for Environment includes the correct version of Python. Once configured the files can be added to systemd with the following commands. You will need to edit the command to use the path to your instance of WhisperScribe.

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

## Updates
Check the release notes to see if there are any major changes with the core/settings.sample.py file, if the requirements-freeze.txt pip packages file has been updated, if a migration is required, or if static files need to be migrated.

It never hurts to run the commands below after an update (while in the Python virtual environment).

### Update Python pip Packages
When the requirements-freeze.txt file is updated, Python packages need to be updated.

```bash
pip install -r requirements-freeze.txt
```

### Run Database Migration
When a model in Django is updated a database migration needs to be run. Backing up your databases before running the migration is recommended in case of an issue.

```bash
python manage.py migrate
```

### Run Static File Collection
When static files (CSS, JavaScript, etc.) are updated in the project they will need to be moved (collected) to your static file location. Running the command below will overwrite any local customizations on static files.

```bash
python manage.py collectstatic
```

## Additional Information
### Reverse Proxy Server
At some point you will want to reverse proxy a web server to WhisperScribe in order to use SSL certificates. [Apache](https://httpd.apache.org/docs/2.4/howto/reverse_proxy.html) and [NGINX](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/) provide well documented guides on setting up reverse proxies. Gunicorn also provides a [guide](https://docs.gunicorn.org/en/latest/deploy.html) on setting up a reverse proxy using Nginx. Do note that if using a reverse proxy server some additional settings will need to be adjusted such as max post size.

## Developer Notes
The Django project folder is 'core' and the application folder is 'webui'.

## Dependencies
- [Python v3.10.12](https://www.python.org/)
- [Faster-Whisper v1.1.1](https://github.com/SYSTRAN/faster-whisper)
- [Pyannote.Audio v3.3.2](https://github.com/pyannote/pyannote-audio)
- [YT-DLP v2025.2.19](https://github.com/yt-dlp/yt-dlp)
- [Gunicorn v23.0.0](https://gunicorn.org/)
- [FFmpeg](https://www.ffmpeg.org/)
- [Django v5.1.6](https://www.djangoproject.com/)
- [Django Cleanup v8.1.0](https://github.com/un1t/django-cleanup/)
- [Django Q2 v1.7.6](https://django-q2.readthedocs.io/en/master/)
- [NVIDIA cuBLAS v12.1.3.1](https://developer.nvidia.com/cublas)
- [NVIDIA cuDNN v8.9.2.26](https://developer.nvidia.com/cudnn)
- [Bootstrap v5.3.6](https://getbootstrap.com/)
- [Bootstrap Icons v1.13.1](https://icons.getbootstrap.com/)
- [DataTables v2.3.1](https://datatables.net/)
- [jQuery v3.7.0](https://jquery.com/)
- [Moment.js v2.29.4](https://momentjs.com/)
