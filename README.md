# WhisperScribe
Code Repository: https://github.com/gsu-library/whisper-scribe  
Author: Matt Brooks <mbrooks34@gsu.edu>  
Date Created: 2024-05-21  
License: [GPLv3](LICENSE)  
Version: 0.0.1

## Description
WhisperScribe is currently a work in progress. Check the develop branch for the latest commits.

## Installation
In the core folder rename settings.sample.py to settings.py and fill out the following fields:

* SECRET_KEY - generate using...
* HUGGING_FACE_TOKEN - for diarization see...
* ALLOWED_HOSTS - link to description
* DATABASES - if using a database other than sqlite...
* TIME_ZONE - to your current time zone

pip install  
migrate DB  
create superuser  
create cachetable  
maybe collectstatic  

### Systemd Service Files
Copy sample files to whisper.service and whisper-q.service.  
Update WorkingDirectory, ExecStart, and Environment paths in whisper.service and whisper-q.service.  
Enable service files.  
Start Whisper service.

### Reverse Proxy
nginx - client_max_body_size

### Nvidia Drivers
nvidia-driver-535-server

### MySQL
https://pypi.org/project/mysqlclient/

## Usage
`python manage.py qcluster`  
`python manage.py runserver`

## Updating
`pip install -r requirements-freeze.txt`  
`python manage.py migrate`

## Developer Notes
The Django project folder is 'core' and the application folder is 'webui'.

## Dependencies
- Bootstrap v5.3.3
- Bootstrap Icons v1.11.3
