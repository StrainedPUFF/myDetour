from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
import json
# from .models import Quiz, Question, Answer
# from .forms import QuestionForm, AnswerForm
from django.shortcuts import render, get_object_or_404, redirect
# from Coordinator.models import QuizRecord
from django.contrib.auth.decorators import login_required
# Create your views here.
def discussion_view(request):
    return render(request, 'discussion/index.html')


