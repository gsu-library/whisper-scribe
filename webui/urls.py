from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views
from . import downloads
from . import api


app_name = 'webui'

urlpatterns = [
   path('', views.index, name='index'),
   path('view/<int:transcription_id>', views.view_transcription, name='view'),
   path('list/', views.list_transcriptions, name='list'),
   path('edit/<int:transcription_id>', views.edit_transcription, name='edit'),
   path('delete/<int:transcription_id>', views.delete_transcription, name='delete'),
   # Download routes
   path('download/text/<int:transcription_id>', downloads.download_text, name='download_text'),
   path('download/text_blob/<int:transcription_id>', downloads.download_text_blob, name='download_text_blob'),
   path('download/srt/<int:transcription_id>', downloads.download_srt, name='download_srt'),
   path('download/vtt/<int:transcription_id>', downloads.download_vtt, name='download_vtt'),
   path('download/json/<int:transcription_id>', downloads.download_json, name='download_json'),
   # API routes
   path('api/transcriptions/<int:transcription_id>', api.api_transcriptions_id, name='api_transcriptions_id'),
   path('api/segments/<int:segment_id>', api.api_segments_id, name='api_segments_id'),
   path('api/segments/', api.api_segments, name='api_segments'),
]

if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
