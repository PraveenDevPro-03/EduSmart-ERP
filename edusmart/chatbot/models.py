from django.db import models

class ChatMessage(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message}"