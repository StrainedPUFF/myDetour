from django.urls import path
from . import views
from django.urls import path
# from .views import add_question, attempt_quiz

# urlpatterns = [
#     path('quiz/<int:quiz_id>/add-question/', add_question, name='add_question'),
#     path('quiz/<int:quiz_id>/attempt/', attempt_quiz, name='attempt_quiz'),
# ]

app_name = 'Discussion'
urlpatterns = [
    path('index/', views.discussion_view, name ="index" ),
    # path('quiz/<int:quiz_id>/add_question/', add_question, name = 'add_question'),
    # path('quiz/<int:quiz_id>/attempt_quiz/', attempt_quiz, name = 'attempt_quiz')
]