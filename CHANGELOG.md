# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.] - 2025-
- Add tooltips to buttons on edit page.

## [1.4.0] - 2025-04-14
- Add and implement transcription status model.
- Register transcription status model on admin page.
- Display submission status (while still pending or processing) on home page.
- Move transcriptions to new page.
- Catch failures for downloading, transcribing, and diarizing.
- Update transcription model to show current status and to fail incomplete statuses.
- Add navbar and body color.
- Update footer.
- Modify updates section of readme.
- Squash migrations between this and previous release.

## [1.3.0] - 2025-03-17
- Use update_fields on model saves when able to.
- Async form submission methods together.
- Remove dark theme.

## [1.2.1] - 2025-02-26
- Remove unused imports.
- Update pip packages, requirements.txt, and requirements-freeze.txt.

## [1.2.0] - 2024-12-10
- The new large-v3-turbo model is now available.
- Update pip packages to latest versions.
- Update Python requirements.

## [1.1.0] - 2024-11-19
- Convert media files to temporary .wav files for diarizer.
- Reorganize some functions into utils.py and media.py.
- Use django.conf settings instead of importing constants directly from core settings.

## [1.0.0] - 2024-11-5
- Initial release.
