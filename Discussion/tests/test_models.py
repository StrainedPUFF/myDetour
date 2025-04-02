from django.test import TestCase
from django.contrib.auth.models import User
from Discussion.models import Session, UserRoleInSession, Quiz, Question, Answer, QuizRecord
from Coordinator.models import Role
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now
import uuid
class SessionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.session = Session.objects.create(name="Test Session", host=self.user)

    def test_clean_method(self):
        self.session.date = timezone.now() - timedelta(days=1)  # Set date in the past
        with self.assertRaises(ValidationError):
            self.session.clean()

    def test_has_expired(self):
        self.session.date = timezone.now() - timedelta(hours=4)  # Set expired date
        self.assertTrue(self.session.has_expired())




class QuizTestCase(TestCase):
    def setUp(self):
        self.quiz = Quiz.objects.create(title="Test Quiz")

    def test_str_method(self):
        self.assertEqual(str(self.quiz), "Test Quiz")

class QuestionTestCase(TestCase):
    def setUp(self):
        self.quiz = Quiz.objects.create(title="Test Quiz")
        self.question = Question.objects.create(quiz=self.quiz, text="Test Question")

    def test_question_creation(self):
        self.assertEqual(self.question.quiz, self.quiz)

class AnswerTestCase(TestCase):
    def setUp(self):
        self.quiz = Quiz.objects.create(title="Test Quiz")
        self.question = Question.objects.create(quiz=self.quiz, text="Test Question")
        self.answer = Answer.objects.create(question=self.question, text="Test Answer", is_correct=True)

    def test_answer_creation(self):
        self.assertEqual(self.answer.question, self.question)
        self.assertTrue(self.answer.is_correct)




class QuizRecordTestCase(TestCase):
    def setUp(self):
        self.quiz = Quiz.objects.create(title="Test Quiz")
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.quiz_record = QuizRecord.objects.create(quiz=self.quiz, user=self.user, name="Test Record", score=90)

    def test_unique_constraint(self):
        with self.assertRaises(Exception):  # Replace Exception with a specific error (e.g., IntegrityError) for your database
            QuizRecord.objects.create(quiz=self.quiz, user=self.user, name="Duplicate Record", score=80)



class UserRoleInSessionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.session = Session.objects.create(name="Test Session", host=self.user)
        self.role = Role.objects.create(name=Role.MODERATOR)
        self.user_role = UserRoleInSession.objects.create(user=self.user, session=self.session, role=self.role)

    def test_relationships(self):
        self.assertEqual(self.user_role.user, self.user)
        self.assertEqual(self.user_role.session, self.session)
        self.assertEqual(self.user_role.role.name, Role.MODERATOR)
class SessionManagerTestCase(TestCase):
    def setUp(self):
        # Create a unique user
        self.user = User.objects.create_user(username=f"testuser_{uuid.uuid4()}", password="password")

        # Create upcoming sessions
        self.session1 = Session.objects.create(
            name=f"Session 1 {uuid.uuid4()}",
            date=now() + timedelta(days=1),  # Tomorrow
            host=self.user
        )
        self.session2 = Session.objects.create(
            name=f"Session 2 {uuid.uuid4()}",
            date=now() + timedelta(days=2),  # Day after tomorrow
            host=self.user
        )
        # Create a past session
        self.past_session = Session.objects.create(
            name=f"Past Session {uuid.uuid4()}",
            date=now() - timedelta(days=1),  # Yesterday
            host=self.user
        )

        # Simulate the user joining the first session
        self.session1.users_joined.add(self.user) 

    def test_get_upcoming_for_user(self):
        # Get upcoming sessions for the user
        upcoming_sessions = Session.objects.get_upcoming_for_user(self.user)
        
        # Verify the upcoming sessions are correctly returned
        self.assertIn(self.session2, upcoming_sessions)  # Should include session2
        self.assertNotIn(self.session1, upcoming_sessions)  # Should exclude session1 (already joined)
        self.assertNotIn(self.past_session, upcoming_sessions)  # Should exclude past sessions
        self.assertTrue(upcoming_sessions.exists())  # Ensure we have upcoming session