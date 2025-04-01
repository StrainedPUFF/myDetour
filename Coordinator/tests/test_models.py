from django.test import TestCase
from Coordinator.models import CustomUser, Role, Profile
from django.contrib.auth.models import User

class CustomUserTestCase(TestCase):
    def test_create_user(self):
        user = CustomUser.objects.create_user(username="testuser", password="testpass")
        self.assertEqual(user.username, "testuser")



class ProfileTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        self.profile = Profile.objects.create(user=user, bio="Test Bio")

    def test_profile_creation(self):
        self.assertEqual(self.profile.user.username, "testuser")
        self.assertEqual(self.profile.bio, "Test Bio")

    def test_str_method(self):
        self.assertEqual(str(self.profile), "testuser")



class RoleTestCase(TestCase):
    def test_role_creation(self):
        role = Role.objects.create(name=Role.MODERATOR)
        self.assertEqual(role.name, Role.MODERATOR)

    def test_str_method(self):
        role = Role.objects.create(name=Role.COLLABORATOR)
        self.assertEqual(str(role), "Collaborator")

