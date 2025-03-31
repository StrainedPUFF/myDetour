from django.urls import path
from . import views
from .views import add_question_and_answers
from django.urls import path
from .views import session_data

app_name = "Coordinator"
urlpatterns = [
    path('signup/', views.signup_view, name='signup'), # for viewing the signup page
    path('login/', views.login_view, name = 'login'), # for viewing the login page
    path('home/', views.home_view, name='home'),  # for viewing the homepage
    path('userprofile/', views.profile_view, name="userprofile"), # for viewing the user profile
    path('dashboard/', views.dashboard_view, name = "dashboard"),# for viewing the dashboard
    path('book_session/<uuid:session_id>/', views.book_session, name = "book_session"), # for booking sessions
    path('cancel_session/<int:session_id>/', views.cancel_session, name = "cancel_session"),#for cancelling created sessions
    path('cancel_booking/<uuid:session_id>/', views.cancel_booking, name = "cancel_booking"), #for cancelling booked sessions
    path('', views.home_session_view, name = 'home_session_view'),
    # path('create-session/', views.create_session, name='create_session'),
    path('quiz/<int:quiz_id>/add_question/', add_question_and_answers, name = 'add_question_and_answers'),
    path('upload-document/<uuid:session_id>/', views.upload_document, name='upload_document'),
    # path('add-question/<int:quiz_id>/', views.add_question_and_answers, name='add_question'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'), 
    path('quiz/<int:quiz_id>/attempt/', views.attempt_quiz, name='attempt_quiz'),
    path('quiz/result/<int:quiz_record_id>/', views.quiz_result, name='quiz_result'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('attempt_once/', views.attempt_once, name='attempt_once'),
    path('homepage_to_signup/', views.homepage_to_signup, name= 'homepage_to_signup'),
    path('homepage_to_login/', views.homepage_to_login, name= 'homepage_to_login'),
    path('logout/', views.logout_view, name='logout'),
    path('join_session/<uuid:session_id>/', views.join_session, name='join_session')
]