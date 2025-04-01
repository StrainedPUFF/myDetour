from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from Discussion.models import Session, Quiz
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from Coordinator.views import create_quiz_for_session

class UserAuthTests(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_signup_view(self):
        response = self.client.post(reverse('Coordinator:signup'), {
            'username': 'newuser',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view(self):
        response = self.client.post(reverse('Coordinator:login'), {
            'username': self.username,
            'password': self.password,
        })
        self.assertRedirects(response, reverse('Coordinator:dashboard'))  # Verify redirect
        self.assertEqual(response.wsgi_request.user.username, self.user.username)  # Validate user login

    def test_logout_view(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('Coordinator:logout'))
        self.assertRedirects(response, reverse('Coordinator:login'))  # Verify redirect after logout
        self.assertFalse(response.wsgi_request.user.is_authenticated)

class SessionManagementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        # Set the session date to be more than 3 hours in the future
        self.session = Session.objects.create(
            name='Test Session',
            date=timezone.now() + timedelta(days=1),  # This ensures it's in the future
            host=self.user
        )
        self.session.users_joined.add(self.user)  # Associate user with the session

    def test_dashboard_view(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('Coordinator:dashboard'))
        self.assertEqual(response.status_code, 200)  # Check for successful response
        self.assertContains(response, 'Test Session')  # Ensure session is displayed

    def test_book_session(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.post(reverse('Coordinator:book_session', args=[self.session.id]))
        self.assertRedirects(response, reverse('Coordinator:dashboard'))  # Verify redirect
        self.assertIn(self.session, self.user.joined_sessions.all())

    def test_cancel_booking(self):
        self.client.login(username='testuser', password='testpassword123')
        self.user.joined_sessions.add(self.session)
        response = self.client.post(reverse('Coordinator:cancel_booking', args=[self.session.id]))
        self.assertRedirects(response, reverse('Coordinator:dashboard'))  # Verify redirect
        self.assertNotIn(self.session, self.user.joined_sessions.all())

class QuizManagementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        self.session = Session.objects.create(
            name='Test Session',
            date=timezone.now() + timezone.timedelta(days=1),
            host=self.user
        )
        self.session.users_joined.add(self.user)  # Associate user with the session
        self.quiz = Quiz.objects.create(title='Test Quiz', session=self.session)

    def test_attempt_quiz(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('Coordinator:attempt_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)  # Check for successful response
        self.assertContains(response, 'Test Quiz')  # Ensure the quiz title is displayed
        self.assertTemplateUsed(response, 'coordinator/attempt_quiz.html')  # Check correct template usage

    def test_attempt_quiz_not_joined(self):
        new_user = User.objects.create_user(username='newuser', password='newpassword123')
        self.client.login(username='newuser', password='newpassword123')
        response = self.client.get(reverse('Coordinator:attempt_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 403)  # Verify forbidden access

class QuizModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Create sessions
        self.session = Session.objects.create(
            name="Future Session",
            date=timezone.now() + timezone.timedelta(days=1),
            host=self.user  # Assuming there's a host field
        )
        self.past_session = Session.objects.create(
            name="Past Session",
            date=timezone.now() - timezone.timedelta(days=1),
            host=self.user  # Assuming there's a host field
        )

    def test_unique_quiz_titles(self):
        Quiz.objects.create(title="Unique Quiz", session=self.session)
        with self.assertRaises(ValidationError):
            Quiz.objects.create(title="Unique Quiz", session=self.past_session)

    def test_quiz_title_validation(self):
        quiz = Quiz(title="   ", session=self.session)
        with self.assertRaises(ValidationError):
            quiz.full_clean()  # Use full_clean to validate all fields

    def test_session_date_validation(self):
        quiz = Quiz(title="Valid Quiz", session=self.past_session)
        with self.assertRaises(ValidationError):
            quiz.full_clean()  # Use full_clean to validate all fields



class CreateQuizForSessionTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="password")

        # Create a test session
        self.session = Session.objects.create(
            name="Test Session",
            date=now() + timedelta(days=1),  # Future session
            description="A test session for quiz creation.",
            host=self.user  # Assign the test user as the host
        )

        # Prepare valid quiz data
        self.valid_quiz_data = {
            'title': "Test Quiz",
        }

        # Prepare invalid quiz data (missing title)
        self.invalid_quiz_data = {
            'title': "",
        }

    def test_create_quiz_with_valid_data(self):
        # Test creating a quiz with valid data
        success, result = create_quiz_for_session(self.session, self.valid_quiz_data)

        self.assertTrue(success)  # Ensure success is True
        self.assertIsInstance(result, Quiz)  # Ensure the result is a Quiz instance
        self.assertEqual(result.title, "Test Quiz")  # Validate title
        self.assertEqual(result.session, self.session)  # Ensure session is linked

    def test_create_quiz_with_invalid_data(self):
        # Test creating a quiz with invalid data
        success, result = create_quiz_for_session(self.session, self.invalid_quiz_data)

        self.assertFalse(success)  # Ensure success is False
        self.assertIsInstance(result, dict)  # Ensure result contains errors
        self.assertIn('title', result)  # Validate error field

    def test_create_quiz_for_past_session(self):
        # Test attempting to create a quiz for a past session
        self.session.date = now() - timedelta(days=1)  # Set session date in the past
        self.session.save()

        success, result = create_quiz_for_session(self.session, self.valid_quiz_data)

        self.assertFalse(success)  # Ensure success is False
        self.assertIsInstance(result, str)  # Ensure result contains an error message
        self.assertIn("Cannot assign a quiz to a session that is in the past.", result)
