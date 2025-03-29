from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from Coordinator.models import Role
from django.utils import timezone
from django.shortcuts import redirect
from datetime import timedelta
from django.core.exceptions import ValidationError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from django.shortcuts import render, HttpResponse
from google.auth.exceptions import RefreshError
import logging
logger = logging.getLogger(__name__)
import time
import base64
import requests
import http.client
import json
import uuid
import os
from django.utils.timezone import now

def session_document_path(instance, filename):
    # Define the upload path using the session ID and original filename
    return os.path.join(f'sessions/{instance.id}/documents/', filename)

class SessionManager(models.Manager):
    def get_upcoming_for_user(self, user):
        return self.filter(
            date__gte=timezone.now()  # Sessions in the future
        ).exclude(
            users_joined=user  # Exclude sessions the current user has already joined
        ).distinct()  # Ensure results are unique


class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    date = models.DateTimeField(default=now)  # Automatically uses a timezone-aware datetime
    description = models.TextField(blank=True, null=True)
    host = models.ForeignKey(User, default=1, on_delete=models.CASCADE, related_name='hosted_main_sessions')
    users_joined = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='joined_sessions')
    users_accessed_react = models.ManyToManyField(User, related_name = 'sessions_accessed_react', blank='True')  
    quiz = models.OneToOneField('Quiz', on_delete=models.CASCADE, null=True, blank=True)
    document = models.FileField(upload_to=session_document_path, null=True, blank=True)
    objects = SessionManager()
    def clean(self):
        # Ensure the session date is not in the past
        if self.date < now():
            raise ValidationError("The session date cannot be in the past.")

    def __str__(self):
        return f"Session: {self.name} (Host: {self.host})"
    def has_expired(self):
        expiration_time = self.date + timedelta(hours=3)
        return timezone.now() > expiration_time
    
    
class Quiz(models.Model):
    title = models.CharField(max_length = 255)
    date = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return self.title
    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, default=1, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

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
        return f"{self.name} - {self.score}"




# class InteractiveSession(models.Model):
#     session = models.OneToOneField(Session, default=0, on_delete=models.CASCADE, related_name='interactive_session')
#     # title = models.CharField(max_length=255, blank=True)
#     description = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     host = models.ForeignKey(User, default=1, related_name='hosted_interactive_sessions', on_delete=models.CASCADE)
#     is_active = models.BooleanField(default=True)
#     video_conference_link = models.URLField(blank=True, null=True)
#     whiteboard_link = models.URLField(blank=True, null=True)
    

#     def save(self, *args, **kwargs):
#         # # Set the title to the session's name
#         # if self.session and not self.title:
#         #     self.title = self.session.name
#         if not self.video_conference_link:
#             self.video_conference_link = self.create_zoom_meeting_link()
#         if not self.whiteboard_link:
#             self.whiteboard_link = self.create_zoom_whiteboard_link()
#         super().save(*args, **kwargs)
#     def __str__(self):
#         return f"{self.session.name} - Interactive Session"
#     # Existing methods remain unchanged...


#     def get_zoom_access_token(self, user):
#         zoom_token = ZoomToken.objects.filter(user=user).first()
#         if zoom_token and zoom_token.expires_at > timezone.now():
#             print(f"Zoom token found for user {user}: {zoom_token.access_token}")
#             return zoom_token.access_token
#         else:
#             print(f"No valid zoom token found for user {user}. Refreshing token...")
#         return self.refresh_zoom_access_token(user)


#     def refresh_zoom_access_token(self, user):
#         zoom_token = ZoomToken.objects.filter(user=user).first()
#         if not zoom_token:
#             print("No zoom token found for user.")
#             return None

#         refresh_token = zoom_token.refresh_token
#         client_id = settings.ZOOM_CLIENT_ID
#         client_secret = settings.ZOOM_CLIENT_SECRET
#         token_url = "https://zoom.us/oauth/token"

#         data = {
#             "grant_type": "refresh_token",
#             "refresh_token": refresh_token
#         }

#         headers = {
#             "Authorization": f"Basic {base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()}"
#         }

#         response = requests.post(token_url, data=data, headers=headers)
#         access_token_info = response.json()

#         if 'access_token' not in access_token_info:
#             print(f"Failed to refresh access token. Response: {access_token_info}")
#             return None
#         print("Successfully refreshed access token.")
#         # Additional debugging to ensure tokens are updated properly
#         print(f"New access token: {new_access_token}")
#         print(f"New refresh token: {new_refresh_token}")   
#         new_access_token = access_token_info.get('access_token')
#         new_refresh_token = access_token_info.get('refresh_token')
#         expires_in = access_token_info.get('expires_in')
#         expires_at = timezone.now() + timedelta(seconds=expires_in)

#         zoom_token.access_token = new_access_token
#         zoom_token.refresh_token = new_refresh_token
#         zoom_token.expires_at = expires_at
#         zoom_token.save()

#         return new_access_token
 

#     def create_zoom_meeting_link(self):
#         access_token = self.get_zoom_access_token(self.host)
#         if not access_token:
#             print("No access token found.")
#             return ''

#         conn = http.client.HTTPSConnection("api.zoom.us")
#         headers = {
#             'Authorization': f"Bearer {access_token}",
#             'Content-Type': 'application/json'
#         }

#         # Fetch the user ID
#         conn.request("GET", "/v2/users/me", headers=headers)
#         res = conn.getresponse()
#         if res.status != 200:
#             print(f"Failed to fetch user ID. Status: {res.status}")
#             error_data = res.read()
#             print(f"Error Response: {error_data.decode('utf-8')}")
#             return ''
    
#         user_data = res.read()
#         user_info = json.loads(user_data.decode("utf-8"))
#         user_id = user_info.get('id')

#         if not user_id:
#             print("User ID not found in response.")
#             return ''

#         body = json.dumps({
#             "topic": "Interactive Session",
#             "type": 1,  # Instant meeting
#             "settings": {
#                 "meeting_authentication": False
#             }
#         })

#         conn.request("POST", f"/v2/users/{user_id}/meetings", body, headers)
#         res = conn.getresponse()
#         data = res.read()
#         response_data = json.loads(data.decode("utf-8"))

#         if res.status != 201:
#             print(f"Failed to create Zoom meeting. Status: {res.status}, Response: {response_data}")
#             return ''

#         print(f"Zoom meeting created successfully. Response: {response_data}")
#         return response_data.get('join_url', '')



#     def create_zoom_whiteboard_link(self):
#         access_token = self.get_zoom_access_token(self.host)
#         if not access_token:
#             print("No access token found.")
#             return ''

#         conn = http.client.HTTPSConnection("api.zoom.us")
#         headers = {
#             'Authorization': f"Bearer {access_token}",
#             'Content-Type': 'application/json'
#         }

#         body = json.dumps({
#             "name": "New Whiteboard Session"
#         })

#         print(f"Sending request to Zoom to create whiteboard: {body}")
#         conn.request("POST", "/v2/whiteboards", body, headers)
#         res = conn.getresponse()
#         data = res.read()
#         response_data = json.loads(data.decode("utf-8"))

#         # Debugging: log the full response
#         print(f"Zoom whiteboard response: {response_data}")

#         if res.status != 201:
#             print(f"Failed to create Zoom whiteboard. Status: {res.status}, Response: {response_data}")
#             return ''

#         print(f"Successfully created Zoom whiteboard. Response: {response_data}")
#         whiteboard_id = response_data.get('whiteboard_id', '')

#         if whiteboard_id:
#             # Construct the whiteboard link using the whiteboard ID
#             whiteboard_link = f"https://zoom.us/wb/{whiteboard_id}"
#             return whiteboard_link
#         else:
#             print("Failed to get whiteboard link.")
#             return ''


# class ZoomToken(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='zoom_token')
#     access_token = models.TextField()
#     refresh_token = models.TextField()
#     expires_at = models.DateTimeField()  # Store the expiry time of the access token

#     def __str__(self):
#         return f"{self.user.username}'s Zoom Token"




        
# class Poll(models.Model):
#     session = models.ForeignKey(InteractiveSession, on_delete=models.CASCADE, related_name='polls')
#     question_text = models.CharField(max_length=200)
#     pub_date = models.DateTimeField('date published')
#     creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_polls')

#     def __str__(self):
#         return self.question_text

# class Choice(models.Model):
#     poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='choices')
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)

#     def __str__(self):
#         return self.choice_text

class UserRoleInSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, default=1, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=True)  # Indicates if the role is currently active

    def __str__(self):
        return f"{self.user.username} - {self.role.name} in {self.session.title}"


    

