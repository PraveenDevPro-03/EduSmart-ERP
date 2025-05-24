from django.db import models
from accounts.models import CustomUser

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.CharField(max_length=100, blank=True, help_text="Subject of the quiz (e.g., Math, Science)")  # New field
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'teacher'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    options = models.JSONField()  # Stores options as a list, e.g., ["Option 1", "Option 2", "Option 3", "Option 4"]
    correct_option = models.IntegerField(default=0)  # Index of the correct option (0-3), default to 0

    def __str__(self):
        return self.text

class QuizResult(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'student'}
    )
    score = models.FloatField()  # Percentage score (0-100)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}: {self.score}%"

    class Meta:
        unique_together = ('quiz', 'user')  # Prevent duplicate results for the same quiz and user