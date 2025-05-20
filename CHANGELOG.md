# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1] - 2025
- Fix bug that caused confirmation for transcription deletion to not show.

## [1.6.1] - 2025-05-20
- Fix for transcriptions not showing on the list page if they were created before the TranscriptionStatus model existed.

## [1.6.0] - 2025-05-19
- Update transcription list page with DataTables, transcriptions can now be searched and sorted.
- Only completed transcriptions are now shown on list page.
- Show process statuses on transcription list page.
- Add confirmation before deleting transcriptions.
- Change seconds_to_segment_time function to format_seconds.
- Change time_filters file to filters.
- Add get_status_of method to transcription model.
- Add versioning template filter for static web files.
- Use cache for versioning.
- Update versions of Bootstrap and Bootstrap Icons.

## [1.5.0] - 2025-04-29
- Add tooltips to buttons on edit page.
- Update downloader to only process one video (for now).
- Change start and end time format on edit page.
- Add visual responses for successful/unsuccessful changes on edit page.
- Add more checks for API calls.
- Update general look and feel on edit page.
- Add scroll to top button on edit page.
- Add alert notifications to edit page if segment creation or deletion fails.
- Add error checks and messaging on edit page if no file or segments are found.
- Update transcription status model start time field to be null by default.
- Update how transcriptions statuses work, start time now only applies when the status is not pending.

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
