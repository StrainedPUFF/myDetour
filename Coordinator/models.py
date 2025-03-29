from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.db import migrations
from django.utils import timezone
from django.conf import settings
# from .models import Quiz
# from django.db import migrations, models
import django.db.models.deletion
# Create your models here.



# Extend User model if needed
class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

# Profile model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username

# Role model
class Role(models.Model):
    MODERATOR = 'moderator'
    COLLABORATOR = 'collaborator'

    ROLE_CHOICES = [
        (MODERATOR, 'Moderator'),
        (COLLABORATOR, 'Collaborator'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.name


# Create a db for Quizzes 
# class Quiz(models.Model):
#     title = models.CharField(max_length = 255)
#     date = models.DateTimeField(auto_now_add = True)
    
#     def __str__(self):
#         return self.title
# Add questions which will be linked to specific quizzes
# class Question(models.Model):
#     quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
#     text = models.CharField(max_length=255)

#     def __str__(self):
#         return self.text
# # Add answers to the questions
# class Answer(models.Model):
#     question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
#     text = models.CharField(max_length=255)
#     is_correct = models.BooleanField(default=False)

#     def __str__(self):
#         return self.text
    



# class QuizRecord(models.Model):
#     # quiz = models.ForeignKey(Quiz, related_name='quiz_records', on_delete=models.CASCADE)
#     quiz = models.ForeignKey(Quiz, related_name='quiz_records', on_delete=models.CASCADE, default=1)
#     name = models.CharField(max_length=255)
#     score = models.IntegerField()
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='quiz_records', on_delete=models.CASCADE)
#     date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.name} - {self.score}"
