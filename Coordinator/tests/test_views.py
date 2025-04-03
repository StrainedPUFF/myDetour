from django.test import TestCase
from django.urls import reverse
from Discussion.models import Session, Quiz
from django.utils.timezone import now
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from Coordinator.views import create_quiz_for_session

# Dynamically fetch the custom user model
User = get_user_model()

class UserAuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword123', email='testuser@example.com'
        )

    def test_signup_view(self):
        response = self.client.post(reverse('Coordinator:signup'), {
            'username': 'newuser',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
            'email': 'newuser@example.com',
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view(self):
        response = self.client.post(reverse('Coordinator:login'), {
            'username': self.user.username,
            'password': 'testpassword123',
        })
        self.assertRedirects(response, reverse('Coordinator:dashboard'))  # Verify redirect
        self.assertEqual(response.wsgi_request.user.username, self.user.username)

    def test_logout_view(self):
        self.client.login(username=self.user.username, password='testpassword123')
        response = self.client.get(reverse('Coordinator:logout'))
        self.assertRedirects(response, reverse('Coordinator:login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

class SessionManagementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword123', email='testuser@example.com'
        )
        self.session = Session.objects.create(
            name='Test Session',
            date=now() + timedelta(days=1),
            host=self.user
        )
        self.session.users_joined.add(self.user)

    def test_dashboard_view(self):
        self.client.login(username=self.user.username, password='testpassword123')
        response = self.client.get(reverse('Coordinator:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Session')

    def test_book_session(self):
        self.client.login(username=self.user.username, password='testpassword123')
        response = self.client.post(reverse('Coordinator:book_session', args=[self.session.id]))
        self.assertRedirects(response, reverse('Coordinator:dashboard'))
        self.assertIn(self.session, self.user.joined_sessions.all())

    def test_cancel_booking(self):
        self.client.login(username=self.user.username, password='testpassword123')
        self.user.joined_sessions.add(self.session)
        response = self.client.post(reverse('Coordinator:cancel_booking', args=[self.session.id]))
        self.assertRedirects(response, reverse('Coordinator:dashboard'))
        self.assertNotIn(self.session, self.user.joined_sessions.all())

class QuizManagementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword123', email='testuser@example.com'
        )
        self.session = Session.objects.create(
            name='Test Session',
            date=now() + timedelta(days=1),
            host=self.user
        )
        self.session.users_joined.add(self.user)
        self.quiz = Quiz.objects.create(title='Test Quiz', session=self.session)

    def test_attempt_quiz(self):
        self.client.login(username=self.user.username, password='testpassword123')
        response = self.client.get(reverse('Coordinator:attempt_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Quiz')
        self.assertTemplateUsed(response, 'coordinator/attempt_quiz.html')

    def test_attempt_quiz_not_joined(self):
        new_user = User.objects.create_user(
            username='newuser', password='newpassword123', email='newuser@example.com'
        )
        self.client.login(username=new_user.username, password='newpassword123')
        response = self.client.get(reverse('Coordinator:attempt_quiz', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 403)

class QuizModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword123', email='testuser@example.com'
        )
        self.session = Session.objects.create(
            name="Future Session",
            date=now() + timedelta(days=1),
            host=self.user
        )
        self.past_session = Session.objects.create(
            name="Past Session",
            date=now() - timedelta(days=1),
            host=self.user
        )

    def test_unique_quiz_titles(self):
        Quiz.objects.create(title="Unique Quiz", session=self.session)
        with self.assertRaises(ValidationError):
            Quiz.objects.create(title="Unique Quiz", session=self.past_session)

    def test_quiz_title_validation(self):
        quiz = Quiz(title="   ", session=self.session)
        with self.assertRaises(ValidationError):
            quiz.full_clean()

    def test_session_date_validation(self):
        quiz = Quiz(title="Valid Quiz", session=self.past_session)
        with self.assertRaises(ValidationError):
            quiz.full_clean()

class CreateQuizForSessionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password", email="testuser@example.com"
        )
        self.session = Session.objects.create(
            name="Test Session",
            date=now() + timedelta(days=1),
            host=self.user
        )
        self.valid_quiz_data = {'title': "Test Quiz"}
        self.invalid_quiz_data = {'title': ""}

    def test_create_quiz_with_valid_data(self):
        success, result = create_quiz_for_session(self.session, self.valid_quiz_data)
        self.assertTrue(success)
        self.assertIsInstance(result, Quiz)
        self.assertEqual(result.title, "Test Quiz")
        self.assertEqual(result.session, self.session)

    def test_create_quiz_with_invalid_data(self):
        success, result = create_quiz_for_session(self.session, self.invalid_quiz_data)
        self.assertFalse(success)
        self.assertIsInstance(result, dict)
        self.assertIn('title', result)

    def test_create_quiz_for_past_session(self):
        self.session.date = now() - timedelta(days=1)
        self.session.save()
        success, result = create_quiz_for_session(self.session, self.valid_quiz_data)
        self.assertFalse(success)
        self.assertIsInstance(result, str)
        self.assertIn("Cannot assign a quiz to a session that is in the past.", result)
