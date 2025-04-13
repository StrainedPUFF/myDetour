from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from Discussion.models import Session,Quiz, Question, Answer,QuizRecord
from django.utils import timezone
from .forms import SessionForm
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from .forms import QuestionForm, AnswerForm, QuizForm
from datetime import timedelta
from django.http import HttpResponse, HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.views.decorators.cache import cache_control
from .forms import DocumentForm
from django.http import JsonResponse, Http404
from django.utils.timezone import now
from django.urls import reverse
from django.views.generic import TemplateView
from .forms import CustomUserCreationForm
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
import uuid
import os



def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Use your CustomUserCreationForm
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after successful signup
            return redirect('Coordinator:dashboard')  # Redirect to the dashboard or any desired page
        else:
            errors = form.errors
    else:
        form = CustomUserCreationForm()
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





@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard_view(request):
    # Restrict access if a session creation flow is incomplete
    if request.session.get('progress') == 'session_created':
        messages.warning(request, "Please complete the document upload for your current session.")
        return redirect('Coordinator:upload_document', session_id=request.session.get('session_id'))
    elif request.session.get('progress') == 'document_uploaded':
        messages.warning(request, "Please complete the question setup for your current session.")
        quiz_id = Session.objects.get(id=request.session.get('session_id')).quiz.id
        return redirect('Coordinator:add_question_and_answers', quiz_id=quiz_id)
    
    user = request.user
    joined_sessions = user.joined_sessions.filter(date__gte=timezone.now() - timedelta(hours=3)).distinct()
    upcoming_sessions = Session.objects.get_upcoming_for_user(user)
    # quiz_records = user.quiz_records.all()
    quiz_records = user.quiz_records.all().order_by('-date')[:5]  # Fetch the last five quiz records based on date
    print(upcoming_sessions.query)
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            try:
                # Check for duplicate session name
                session_name = form.cleaned_data['name']
                if Session.objects.filter(name=session_name).exists():
                    messages.error(request, f"A session with the name '{session_name}' already exists. Please choose a different name.")
                else:
                    with transaction.atomic():
                        # Create and save session
                        new_session = form.save(commit=False)
                        new_session.host = user
                        new_session.save()
                        new_session.users_joined.add(user)

                        # Delegate quiz creation
                        quiz_data = request.POST.copy()
                        quiz_data['title'] = new_session.name  # Ensure title matches the QuizForm field
                        success, result = create_quiz_for_session(new_session, quiz_data)

                        if success:
                            # Redirect to the document upload page
                            messages.success(request, f"Session '{new_session.name}' created and joined successfully!")
                            request.session['progress'] = 'session_created'  # Mark progress
                            request.session['session_id'] = str(new_session.id)
                            return redirect('Coordinator:upload_document', session_id=new_session.id)
                        else:
                            messages.error(request, f"Quiz creation failed: {result}")
            except Exception as e:
                messages.error(request, f"Error creating session: {e}")
        else:
            # Handle session form errors
            messages.error(request, "Session form is not valid. Please correct the errors.")
    else:
        form = SessionForm()
        storage = get_messages(request)
        for _ in storage:
            pass  # Iterate through messages to mark them as read

    # Render the dashboard
    return render(request, 'coordinator/dashboard.html', {
        'user': user,
        'joined_sessions': joined_sessions,
        'upcoming_sessions': upcoming_sessions,
        'quiz_records': quiz_records,
        'form': form
    })

def create_quiz_for_session(session, quiz_data):
    try:
        session.refresh_from_db()  # Reload session from the database

    # Check if the title should have a unique identifier
        unique_title = quiz_data.get('title')
        if 'append_session_id' in quiz_data and quiz_data['append_session_id']:
            unique_title = f"{unique_title} ({session.id})"
        quiz_data['title'] = unique_title

        quiz_form = QuizForm(quiz_data)
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.session = session  # Associate the quiz with the session
            quiz.save()
            session.quiz = quiz  # Link the quiz back to the session
            session.save()
            return True, quiz
        else:
            return False, quiz_form.errors
    except Exception as e:
        return False, str(e)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def upload_document(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if request.session.get('progress') != 'session_created':
        messages.error(request, "Please follow the session creation process.")
        return redirect('coordinator:dashboard')

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            session.document = form.cleaned_data['document']
            session.save()
            request.session['progress'] = 'document_uploaded'  # Update progress marker
            messages.success(request, "Document uploaded successfully!")
            return redirect('Coordinator:add_question_and_answers', quiz_id=session.quiz.id)
        else:
            messages.error(request, "Invalid file upload. Please try again.")
    else:
        form = DocumentForm()

    return render(request, 'coordinator/upload.html', {'form': form, 'session': session})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_question_and_answers(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    # Validate progress
    if request.session.get('progress') != 'document_uploaded':
        messages.error(request, "You need to upload a document before adding questions.")
        return redirect('coordinator:upload_document', session_id=quiz.session.id)
    question_form = QuestionForm()  # Initialize the form here

    if request.method == 'POST':
        print(request.POST)  # Debugging: Print POST data
        try:
            with transaction.atomic():
                question_index = 0
                question_count = 0
                valid_answers_count = 0

                while f'question_{question_index}_text' in request.POST:
                    question_text = request.POST.get(f'question_{question_index}_text')
                    if question_text.strip():  # Skip empty questions
                        question_form = QuestionForm(data={'text': question_text})
                        if question_form.is_valid():
                            question = question_form.save(commit=False)
                            question.quiz = quiz
                            question.save()
                            question_count += 1  # Increment question count

                            answer_index = 1  # Start answer index from 1
                            answer_count = 0  # Reset answer count for this question
                            while f'answer_{question_index}_{answer_index}_text' in request.POST:
                                answer_text = request.POST.get(f'answer_{question_index}_{answer_index}_text')
                                is_correct = request.POST.get(f'answer_{question_index}_{answer_index}_is_correct') == 'on'
                                print(f"Creating answer for question {question_index}: {answer_text}, correct: {is_correct}")  # Debugging: Print answer data
                                
                                if answer_text.strip():  # Skip empty answers
                                    answer_form = AnswerForm(data={'text': answer_text, 'is_correct': is_correct})
                                    if answer_form.is_valid():
                                        answer = answer_form.save(commit=False)
                                        answer.question = question
                                        answer.save()
                                        answer_count += 1  # Increment answer count
                                answer_index += 1

                            # Check if at least two answers were added for this question
                            if answer_count < 2:
                                messages.error(request, "Each question must have at least two answers.")
                                return render(request, 'coordinator/add_question.html', {'quiz': quiz, 'question_form': question_form})

                    question_index += 1

                # Check if at least one question was added
                if question_count < 1:
                    messages.error(request, "You must add at least one question.")
                    return render(request, 'coordinator/add_question.html', {'quiz': quiz, 'question_form': question_form})

                messages.success(request, "Questions and answers added successfully.")
                request.session['progress'] = 'questions_added'  # Update progress marker
                return redirect('coordinator:quiz_detail', quiz_id=quiz.id)
        except Exception as e:
            messages.error(request, f"Error adding questions and answers: {str(e)}")
    else:
        # Initialize an empty form for rendering
        question_form = QuestionForm()
    return render(request, 'coordinator/add_question.html', {'quiz': quiz, 'question_form': question_form})


@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    questions = quiz.questions.all()
    return render(request, 'coordinator/quiz_detail.html', {'quiz': quiz, 'questions': questions})




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


class ReactAppView(TemplateView):
     
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        
        try:
    
            # Locate the `index.html` in the React build directory
            build_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend/build/')
            with open(os.path.join(build_dir, self.template_name)) as file:
                request.session['progress'] = 'session_attended'
                return HttpResponse(file.read())
        except FileNotFoundError:
            return HttpResponse("React build not found. Check the build folder location.", status=501)



@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def attempt_quiz(request, quiz_id):
    if request.session.get('progress') != 'session_attended':
        messages.error(request, "Please join the session before attempting the quiz.")
        return redirect('react/')
    quiz = get_object_or_404(Quiz, id=quiz_id)
    session = get_object_or_404(Session, id=quiz.session.id)  # Get the session associated with the quiz

    # Check if the user is part of the session
    if request.user not in session.users_joined.all():
        return HttpResponseForbidden()  # Return 403 if the user is not part of the session

    # Check if the user has already attempted the quiz
    if QuizRecord.objects.filter(quiz=quiz, user=request.user).exists():
        return redirect('Coordinator:attempt_once')  # Redirect if already attempted

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
            return redirect('Coordinator:attempt_once')  # Handle duplicate record case
        except Exception as e:
            print(f"Error saving quiz record: {e}")
            messages.error(request, f"Error saving quiz record: {e}")
        
        return redirect('Coordinator:quiz_result', quiz_id=quiz.id)
    
    return render(request, 'coordinator/attempt_quiz.html', {
        'quiz': quiz
    })




@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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
        request.session['progress'] = 'quiz_submitted'
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

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def quiz_result(request, quiz_record_id):
    quiz_record = get_object_or_404(QuizRecord, id=quiz_record_id)
    return render(request, 'coordinator/quiz_result.html', {'score': quiz_record.score})


def attempt_once(request):

    return render(request, 'coordinator/attempt_once.html')



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

def logout_view(request):
    logout(request)
    return redirect('Coordinator:login')
