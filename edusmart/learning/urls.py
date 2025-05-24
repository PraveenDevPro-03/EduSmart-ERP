from django.urls import path
from . import views
app_name = 'learning'  # Define namespace
urlpatterns = [
    path('upload/', views.upload_video, name='upload_video'),
    path('videos/', views.video_learning, name='video_learning'),
    path('chatbot/', views.chatbot, name='chatbot'),
]