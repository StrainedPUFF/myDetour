from django.test import TestCase
from django.contrib.auth.models import User
from Discussion.models import Session, UserRoleInSession, Quiz, Question, Answer, QuizRecord
from Coordinator.models import Role
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

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
