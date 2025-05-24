from django.db import models
from accounts.models import CustomUser
from django.db import models
from accounts.models import CustomUser
class Video(models.Model):
    title = models.CharField(max_length=200)
    video_id = models.CharField(max_length=100, unique=True)  # YouTube video ID, e.g., "dQw4w9WgXcQ"
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'teacher'},
        related_name='uploaded_videos'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-uploaded_at']  # Newest videos first




# class ChatMessage(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     message = models.TextField()
#     response = models.TextField(blank=True)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username}: {self.message}"