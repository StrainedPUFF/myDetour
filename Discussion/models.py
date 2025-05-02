from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from Coordinator.models import Role
from django.utils import timezone
from django.shortcuts import redirect
from datetime import timedelta
from django.core.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)
import uuid
import os
from django.utils.timezone import now

def session_document_path(instance, filename):
    # Define the upload path using the session ID and original filename
    return os.path.join(f'sessions/{instance.id}/documents/', filename)
    # return f'sessions/{instance.id}/documents/{filename}'
# def session_document_path(instance, filename):
#     path = f'sessions/{instance.id}/documents/{filename}'
#     print(f"Generated path: {path}")
#     return path



class SessionManager(models.Manager):
    def get_upcoming_for_user(self, user):
        return self.filter(
            date__gte=timezone.now() - timedelta(minutes=30) # Sessions in the future
        ).exclude(
            users_joined__id=user.id,  # Exclude sessions joined by the current user
        ).distinct().order_by('date')  # Ensure no duplicates and sort by date
    
class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    date = models.DateTimeField(default=now)
    description = models.TextField(blank=True, null=True)
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        default=1,
        on_delete=models.CASCADE,
        related_name='hosted_main_sessions'
    )
    users_joined = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='joined_sessions'
    )
    users_accessed_react = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='sessions_accessed_react',
        blank=True
    )
    # The related_name here must also not clash with Quiz
    quiz = models.OneToOneField(
        'Quiz',
        on_delete=models.CASCADE,
        related_name='session_quiz',
        null=True,
        blank=True
    )
    document = models.FileField(upload_to=session_document_path, null=True, blank=True)
    objects = SessionManager()

    def clean(self):
        if self.date < now():
            raise ValidationError("The session date cannot be in the past.")
        
    def save(self, *args, **kwargs):
        # Ensure instance ID is generated before saving the file
        if not self.id:
            super().save(*args, **kwargs)  # First save to generate the ID
        super().save(*args, **kwargs)  # Save again to handle the file path correctly

    def __str__(self):
        return f"Session: {self.name} (Host: {self.host})"

    def has_expired(self):
        expiration_time = self.date + timedelta(hours=3)
        return timezone.now() > expiration_time

    class Meta:
        indexes = [
            models.Index(fields=['date']),
        ]

class Quiz(models.Model):
    title = models.CharField(max_length=255, unique=True)  # Enforcing unique titles
    session = models.OneToOneField(
        'Session',
        on_delete=models.CASCADE,
        related_name='quiz_session',
        null=True,  # Allow the session to be assigned later
        blank=True  # Ensure forms do not require it immediately
    )
    date = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Ensure the quiz title is not blank or whitespace
        if not self.title.strip():
            raise ValidationError("Quiz title cannot be blank or contain only whitespace.")
        
        # Validate that the associated session is in the future
        if self.session and self.session.date < now():
            raise ValidationError("Cannot assign a quiz to a session that is in the past.")

    def save(self, *args, **kwargs):
        # Perform validation during the save process
        self.clean()
        super().save(*args, **kwargs)

    # def __str__(self):
        # return f"{self.title} (Session: {self.session})" if self.session else self.title
    def __str__(self):
        return f"{self.title} (Host: {self.session.host})" if self.session and self.session.host else self.title


    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, default=1, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    multiple_answers_allowed = models.BooleanField(default=False)  # New field

    def __str__(self):
        return self.text
    
class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
    



class QuizRecord(models.Model):
    # quiz = models.ForeignKey(Quiz, related_name='quiz_records', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, related_name='quiz_records', on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=255)
    score = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='quiz_records', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('quiz', 'user')  # Add unique constraint to prevent duplicate records

    def __str__(self):
        return f"{self.name} - {self.score} - {self.quiz.title}"

  

class UserRoleInSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, default=1, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=True)  # Indicates if the role is currently active

    def __str__(self):
        return f"{self.user.username} - {self.role.name} in {self.session.title}"


    

