from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Discussion.models import Session,Quiz, Question, Answer,QuizRecord
from django.utils import timezone
from .forms import SessionForm
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from .forms import QuestionForm, AnswerForm, QuizForm
from django.conf import settings
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from datetime import timedelta
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .forms import DocumentForm
from django.http import JsonResponse, Http404
from django.utils.timezone import now
from django.urls import reverse
import requests
import http.client
import json
import requests
import base64
import os

def homepage_to_signup(request):
    return render(request, 'Coordinator/signup.html')

def homepage_to_login(request):
    return render(request, 'Coordinator/login.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('Coordinator:dashboard')  # Redirect to a home page or any other page
        else:
            errors = form.errors
    else:
        form = UserCreationForm()
        errors = None
    return render(request, 'coordinator/signup.html', {'form': form, 'errors': errors})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('Coordinator:dashboard')  # Redirect to a home page or any other page
        else:
            errors = form.errors
    else:
        form = AuthenticationForm()
        errors = None
    return render(request, 'coordinator/login.html', {'form': form, 'errors': errors})



def home_view(request):
    return render(request, 'coordinator/home.html')

@login_required
def profile_view(request):
    user = request.user
    return render(request, 'coordinator/userprofile.html', {'user': user})


# @login_required
# def dashboard_view(request):
#     user = request.user
#     joined_sessions = user.joined_sessions.distinct()  # Ensure no duplicates
#     upcoming_sessions = Session.objects.filter(date__gte=timezone.now()).exclude(users_joined=user).distinct()  # Ensure no duplicates
#     quiz_records = user.quiz_records.all()

#     if request.method == 'POST':
#         form = SessionForm(request.POST)
#         quiz_form = QuizForm(request.POST)
#         print(f"Form data: {request.POST}")  # Debugging statement for form data
#         if form.is_valid():
#             print("Form is valid.")
#             try:
#                 new_session = form.save(commit=False)
#                 new_session.host = user
#                 new_session.save()
#                 new_session.users_joined.add(user)

#                 # Check if interactive session should be created
#                 if form.cleaned_data['create_interactive'] and form.cleaned_data['interactive_description']:
#                     InteractiveSession.objects.create(
#                         session=new_session,
#                         description=form.cleaned_data['interactive_description'],
#                         host=user,
#                     )
#                 else:
#                     # Create a quiz if not an interactive session
#                     quiz_form = QuizForm(request.POST)
#                     if quiz_form.is_valid():
#                         quiz = quiz_form.save()
#                         print(f"Quiz created with ID: {quiz.id}")
#                         new_session.quiz = quiz
#                         new_session.save()
#                         print("Redirecting to add_question_and_answers")
#                         return redirect('Coordinator:add_question_and_answers', quiz_id=quiz.id)

#                 messages.success(request, f"Session {new_session.name} created and joined successfully.")
#                 return redirect('Coordinator:dashboard')  # Redirect to refresh the form
#             except Exception as e:
#                 messages.error(request, f"Error creating session: {e}")
#         else:
#             print("Form errors:")
#             for field, errors in form.errors.items():
#                 print(f"{field}: {errors}")
#             messages.error(request, "Form is not valid")
#     else:
#         form = SessionForm()
#         quiz_form = QuizForm()

#     return render(request, 'Coordinator/dashboard.html', {
#         'user': user,
#         'joined_sessions': joined_sessions,
#         'upcoming_sessions': upcoming_sessions,
#         'quiz_records': quiz_records,
#         'form': form,
#         'quiz_form': quiz_form
#     })

@login_required
def dashboard_view(request):
    user = request.user
    joined_sessions = user.joined_sessions.filter(date__gte=timezone.now() - timedelta(hours=3)).distinct()
    upcoming_sessions = Session.objects.get_upcoming_for_user(user)
    quiz_records = user.quiz_records.all()

    if request.method == 'POST':
        form = SessionForm(request.POST)
        quiz_form = QuizForm(request.POST)
        print(f"Form data: {request.POST}")  # Debugging statement for form data

        if form.is_valid():
            print("Form is valid.")
            try:
                with transaction.atomic():
                    new_session = form.save(commit=False)
                    new_session.host = user
                    new_session.save()
                    new_session.users_joined.add(user)

                    # Quiz creation logic
                    print("Attempting to create quiz...")
                    quiz_data = request.POST.copy()
                    quiz_data['title'] = new_session.name
                    quiz_form = QuizForm(quiz_data)

                    if quiz_form.is_valid():
                        print("Quiz form is valid.")
                        quiz = quiz_form.save()
                        print(f"Quiz created with ID: {quiz.id}")
                        new_session.quiz = quiz
                        new_session.save()
                        print("Redirecting to the upload page")
                        return redirect('Coordinator:upload_document', session_id=new_session.id)
                    else:
                        print("Quiz form errors:")
                        for field, errors in quiz_form.errors.items():
                            print(f"{field}: {errors}")

                messages.success(request, f"Session {new_session.name} created and joined successfully.")
                return redirect('Coordinator:dashboard')  # Redirect to refresh the form

            except Exception as e:
                messages.error(request, f"Error creating session: {e}")
        else:
            print("Form errors:")
            for field, errors in form.errors.items():
                print(f"{field}: {errors}")
            messages.error(request, "Form is not valid")
    else:
        form = SessionForm()
        quiz_form = QuizForm()

    return render(request, 'Coordinator/dashboard.html', {
        'user': user,
        'joined_sessions': joined_sessions,
        'upcoming_sessions': upcoming_sessions,
        'quiz_records': quiz_records,
        'form': form,
        'quiz_form': quiz_form
    })

@login_required
def book_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if request.method == 'POST':
        if session not in request.user.joined_sessions.all():
            request.user.joined_sessions.add(session)
            messages.success(request, f'You have successfully booked the session: {session.name}')
        else:
            messages.info(request, f'You have already booked the session: {session.name}')
        return redirect('Coordinator:dashboard')
    return render(request, 'coordinator/dashboard.html', {'session': session})

@login_required
def cancel_booking(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    user = request.user

    if request.method == 'POST':
        # Ensure the session hasn't started yet
        if session.date > timezone.now():
            # Check if the user is a participant but hasn't joined the session
            if session in user.joined_sessions.all():
                session.users_joined.remove(user)
                session.save()
                messages.success(request, f'You have successfully canceled your booking for the session: {session.name}')
            else:
                messages.info(request, f'You have not booked the session: {session.name}')
        else:
            messages.warning(request, f"The session '{session.name}' has already started, so you cannot cancel your booking.")

        return redirect('Coordinator:dashboard')

    return render(request, 'coordinator/dashboard.html', {'session': session})

@login_required
def cancel_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if request.method == 'POST':
        if session.creator == request.user:
            session.delete()
            messages.success(request, f'You have successfully canceled the session: {session.name}')
        else:
            messages.info(request, f'You do not have permission to cancel the session: {session.name}')
        return redirect('Coordinator:dashboard')
    return render(request, 'coordinator/dashboard.html', {'session': session})

def home_session_view(request):
    print("View is being executed")  # Add this line
    sessions = Session.objects.filter(date__gte=timezone.now())
    print("Sessions fetched:", sessions)  # Add this line
    return render(request, 'Coordinator/home.html', {'sessions': sessions})

@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        answer_form = AnswerForm(request.POST)
        if question_form.is_valid() and answer_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()
            answer = answer_form.save(commit=False)
            answer.question = question
            answer.save()
            return redirect('quiz_detail', quiz_id=quiz.id)
    else:
        question_form = QuestionForm()
        answer_form = AnswerForm()
    return render(request, 'Coordinator/add_question.html', {
        'quiz': quiz,
        'question_form': question_form,
        'answer_form': answer_form
    })





@login_required
def attempt_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    session = get_object_or_404(Session, quiz=quiz)

    # Check if the user has already attempted the quiz
    if QuizRecord.objects.filter(quiz=quiz, user=request.user).exists():
        # Handle the case where the user has already attempted the quiz
        return redirect('Coordinator:attempt_once')

    if request.method == 'POST':
        selected_answers = request.POST
        score = calculate_score(quiz, selected_answers)
        
        try:
            with transaction.atomic():
                QuizRecord.objects.create(
                    quiz=quiz,
                    name=request.user.username,
                    score=score,
                    user=request.user
                )
        except IntegrityError:
            # Handle the duplicate record case
            return redirect('Coordinator:attempt_once')
        except Exception as e:
            # Handle other errors
            print(f"Error saving quiz record: {e}")
            messages.error(request, f"Error saving quiz record: {e}")
        
        return redirect('Coordinator:quiz_result', quiz_id=quiz.id)
    
    return render(request, 'coordinator/attempt_quiz.html', {
        'quiz': quiz
    })


def attempt_once(request):

    return render(request, 'coordinator/attempt_once.html')

@login_required
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        selected_answers = request.POST
        score = calculate_score(quiz, selected_answers)

        try:
            quiz_record = QuizRecord.objects.create(
                quiz=quiz,
                name=request.user.username,
                score=score,
                user=request.user
            )
        except Exception as e:
            print(f"Error saving quiz record: {e}")

        return redirect('Coordinator:quiz_result', quiz_record_id=quiz_record.id)

    return redirect('Coordinator:attempt_quiz', quiz_id=quiz.id)

def calculate_score(quiz, selected_answers):
    score = 0
    for question in quiz.questions.all():
        selected_answer_id = selected_answers.get(f'question_{question.id}')
        if not selected_answer_id:
            # Handle missing answers here if needed, e.g., log it or pass
            print(f"Question {question.id} was not answered.")
            continue
        selected_answer = get_object_or_404(Answer, id=selected_answer_id)
        if selected_answer.is_correct:
            score += 1
    return score

def quiz_result(request, quiz_record_id):
    quiz_record = get_object_or_404(QuizRecord, id=quiz_record_id)
    return render(request, 'coordinator/quiz_result.html', {'score': quiz_record.score})


from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required

@login_required
def join_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    user = request.user

    # Check if the session date and time has arrived
    if session.date > timezone.now():
        messages.warning(request, f"The session '{session.name}' is scheduled for {session.date}. You cannot join it yet.")
        return redirect('Coordinator:dashboard')

    if session.users_joined.filter(id=user.id).exists():
        # User already joined the session
        messages.info(request, "You have already joined this session.")
    else:
        # Add the user to the session's participants
        session.users_joined.add(user)
        session.save()
        messages.success(request, "You have successfully joined the session.")

        # Redirect user to the React app before proceeding
    if not session.users_accessed_react.filter(id=user.id).exists():
        session.users_accessed_react.add(user)
        session.save()
        return redirect(reverse('react-app'))  # Directs to `/react/'

    # Default redirection to the dashboard
    return redirect('Coordinator:dashboard')

# @login_required
# def interactive_session_view(request, session_id):
    # interactive_session = get_object_or_404(InteractiveSession, session_id=session_id)
    # return render(request, 'Coordinator/interactivesessions.html', {'interactive_session': interactive_session})

# @login_required
# def create_session(request):
#     if request.method == 'POST':
#         session_form = SessionForm(request.POST)
#         if session_form.is_valid():
#             session = session_form.save(commit=False)
#             create_interactive = request.POST.get('create_interactive') == 'on'  # Check if checkbox is checked
            
#             if create_interactive:
#                 # For interactive session, no quiz creation, redirect to dashboard
#                 session.save()
#                 return redirect('Coordinator:dashboard')
#             else:
#                 # For regular session, redirect to add_question_and_answers
#                 quiz_form = QuizForm(request.POST)
#                 if quiz_form.is_valid():
#                     quiz = quiz_form.save()
#                     session.quiz = quiz
#                     session.save()
#                     return redirect('Coordinator:add_question_and_answers', quiz_id=quiz.id)
#                 else:
#                     # Handle case where quiz form is not valid (optional)
#                     session.save()
#                     return redirect('Coordinator:dashboard')
#     else:
#         session_form = SessionForm()
#         quiz_form = QuizForm()

#     return render(request, 'Coordinator/sessions.html', {'session_form': session_form, 'quiz_form': quiz_form})

@login_required
def add_question_and_answers(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    if request.method == 'POST':
        print(request.POST)  # Debugging: Print POST data
        try:
            with transaction.atomic():
                question_index = 0
                while f'question_{question_index}_text' in request.POST:
                    question_text = request.POST.get(f'question_{question_index}_text')
                    if question_text.strip():  # Skip empty questions
                        question = Question.objects.create(quiz=quiz, text=question_text)

                        answer_index = 1  # Start answer index from 1
                        while f'answer_{question_index}_{answer_index}_text' in request.POST:
                            answer_text = request.POST.get(f'answer_{question_index}_{answer_index}_text')
                            is_correct = request.POST.get(f'answer_{question_index}_{answer_index}_is_correct') == 'on'
                            print(f"Creating answer for question {question_index}: {answer_text}, correct: {is_correct}")  # Debugging: Print answer data
                            Answer.objects.create(question=question, text=answer_text, is_correct=is_correct)
                            answer_index += 1
                    question_index += 1
                return redirect('Coordinator:quiz_detail', quiz_id=quiz.id)
        except Exception as e:
            messages.error(request, f"Error adding questions and answers: {str(e)}")
    else:
        question_form = QuestionForm()

    return render(request, 'Coordinator/add_question.html', {'quiz': quiz, 'question_form': question_form})

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    questions = quiz.questions.all()
    return render(request, 'Coordinator/quiz_detail.html', {'quiz': quiz, 'questions': questions})



def upload_document(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the validated document to the session
            session.document = form.cleaned_data['document']
            session.save()

            # Redirect to the "Add Questions" page for the associated quiz
            if session.quiz:
                return redirect('Coordinator:add_question_and_answers', quiz_id=session.quiz.id)
            else:
                return HttpResponseRedirect('/success/url/')
        else:
            # Form is invalid (e.g., file not a PDF)
            return render(request, 'coordinator/upload.html', {'form': form, 'session': session})
    else:
        form = DocumentForm()

    return render(request, 'coordinator/upload.html', {'form': form, 'session': session})

# def react_index(request):
#     return render(request, 'Coordinator/react_index.html')


# def index(request):
#     return render(request, 'frontend/build/index.html')

from django.views.generic import TemplateView
from django.template.exceptions import TemplateDoesNotExist

# Serve React App
# class ReactAppView(TemplateView):
#     template_name = "index.html"

#     def get(self, request, *args, **kwargs):
#         try:
#             return render(request, self.template_name)
#         except TemplateDoesNotExist:
#             return HttpResponse("React build not found. Check the build folder location.", status=501)

class ReactAppView(TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        try:
            # Locate the `index.html` in the React build directory
            build_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend/build/')
            with open(os.path.join(build_dir, self.template_name)) as file:
                return HttpResponse(file.read())
        except FileNotFoundError:
            return HttpResponse("React build not found. Check the build folder location.", status=501)
# from django.views.decorators.csrf import csrf_exempt
# import uuid

# @csrf_exempt
# def get_session_id(request):
#     # Generate or fetch a session ID
#     session_id = str(uuid.uuid4())  # You can use UUID or any other method to generate the session ID
#     return JsonResponse({'sessionId': session_id})
  # Assuming a model for session data
import uuid

# def get_session_id(request):
#     # Check for a session ID in the cookies
#     session_id = request.COOKIES.get('sessionId')

#     if not session_id:
#         # If no session ID in cookies, check for an existing session in the DB
#         # Example: Match the user or context with an existing session
#         user = request.user if request.user.is_authenticated else None
#         existing_session = Session.objects.filter(host=user).first() if user else None

#         if existing_session:
#             session_id = str(existing_session.id)
#         else:
#             # If no session is found, return an error
#             return JsonResponse({'error': 'No session found for this user or context'}, status=404)

#     # If a session is found, return it
#     response = JsonResponse({'sessionId': session_id})
#     response.set_cookie('sessionId', session_id)
#     return response


# def get_session_id(request):
#     if request.user.is_authenticated:
#         try:
#             # Retrieve the session where the user is the host
#             session = Session.objects.get(host=request.user)
#             return JsonResponse({
#                 'sessionId': str(session.id),
#                 'name': session.name,
#                 'date': session.date,
#                 'documentUrl': session.document.url if session.document else None,  # Add more fields if needed
#             })
#         except Session.DoesNotExist:
#             return JsonResponse({'error': 'No session found for this user'}, status=404)
#     else:
#         return JsonResponse({'error': 'User not authenticated'}, status=401)

@login_required
def get_session_id(request):
    user = request.user  # Currently authenticated user.

    # Filter for active sessions the user has joined, ensuring they haven't expired.
    current_sessions = Session.objects.filter(
        users_joined=user,
        date__lte=now()  # Session date is not in the future.
    ).exclude(
        date__lt=now() - timedelta(hours=3)  # Exclude expired sessions based on `has_expired`.
    ).order_by('-date')  # Sort by the most recent session.

    if not current_sessions.exists():
        return JsonResponse({"error": "No active sessions for the user"}, status=404)

    # Assume only one active session is required (e.g., the most recent one).
    active_session = current_sessions.first()

    # Prepare session data for the response.
    session_data = {
        "id": str(active_session.id),  # Convert UUID to string for JSON serialization.
        "name": active_session.name,
        "date": active_session.date,
        "host": active_session.host.username,  # Host's username.
        "current_user": request.user.username,
        "quiz_id": active_session.quiz.id if active_session.quiz else None,
        "document": active_session.document.url if active_session.document else None,
        "has_expired": active_session.has_expired()
    }

    return JsonResponse(session_data)
# def session_data(request, session_id):
#     session = Session.objects.filter(id=session_id).first()
#     if not session:
#         raise Http404("No Session matches the given query.")
    
#     data = {
#         'documentUrl': session.document.url if session.document else '',
#         'sessionId': str(session.id),
#     }
#     return JsonResponse(data)

def session_data(request, session_id):
    try:
        # Validate session_id as a UUID
        uuid_obj = uuid.UUID(session_id)
    except ValueError:
        raise Http404("Invalid UUID format.")

    # Fetch the session
    session = Session.objects.filter(id=session_id).first()
    if not session:
        raise Http404("No Session matches the given query.")
    
    data = {
        'documentUrl': session.document.url if session.document else '',
        'sessionId': str(session.id),
    }
    return JsonResponse(data)
