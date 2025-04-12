from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.db import migrations
from django.utils import timezone
from django.conf import settings
# from .models import Quiz
# from django.db import migrations, models
import django.db.models.deletion
# Create your models here.



class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Ensure email is included and unique
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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
        return self.name.capitalize()


