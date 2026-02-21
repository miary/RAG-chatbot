from django.urls import path
from . import views

urlpatterns = [
    # Health / status
    path('', views.health_check, name='health-check'),
    path('status/', views.service_status, name='service-status'),

    # Sessions
    path('sessions/', views.session_list, name='session-list'),
    path('sessions/<uuid:session_id>/', views.session_detail, name='session-detail'),
    path('sessions/<uuid:session_id>/clear/', views.clear_session, name='session-clear'),

    # Chat
    path('chat/', views.send_message, name='send-message'),

    # Feedback
    path('messages/<uuid:message_id>/feedback/', views.message_feedback, name='message-feedback'),

    # Admin / Ingest
    path('ingest/', views.ingest_data, name='ingest-data'),
]
