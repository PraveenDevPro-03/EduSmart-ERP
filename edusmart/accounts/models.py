# from django.db import models
# from django.contrib.auth.models import AbstractUser

# class CustomUser(AbstractUser):
#     USER_TYPE_CHOICES = (
#         ('student', 'Student'),
#         ('teacher', 'Teacher'),
#     )
#     user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
#     department = models.CharField(max_length=100, blank=True, null=True)
#     designation = models.CharField(max_length=100, blank=True, null=True)
#     course = models.CharField(max_length=100, blank=True, null=True)
#     branch = models.CharField(max_length=100, blank=True, null=True)
#     roll_number = models.CharField(max_length=50, blank=True, null=True)
#     profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
#     bio = models.TextField(blank=True, null=True)
#     is_email_verified = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     is_sub_admin = models.BooleanField(default=False)  # Added field


#     def __str__(self):
#         return self.username



# class Message(models.Model):
#     sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
#     receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False)

#     class Meta:
#         ordering = ['timestamp']

#     def __str__(self):
#         return f"{self.sender} to {self.receiver}: {self.content[:50]}"



# class AdminInviteToken(models.Model):
#     token = models.CharField(max_length=100, unique=True)
#     created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'admin', 'is_sub_admin': False})
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()
#     used = models.BooleanField(default=False)

#     def is_valid(self):
#         return not self.used and self.expires_at > timezone.now()













from django.db import models
from django.contrib.auth.models import AbstractUser
# import timezone  # Add import if needed
from django.utils import timezone

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),  # Added admin choice
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    department = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    course = models.CharField(max_length=100, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_sub_admin = models.BooleanField(default=False)  # Added field

    def __str__(self):
        return self.username

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender} to {self.receiver}: {self.content[:50]}"

class AdminInviteToken(models.Model):
    token = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'admin', 'is_sub_admin': False})
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and self.expires_at > timezone.now()