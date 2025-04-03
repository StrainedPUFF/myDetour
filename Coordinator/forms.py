from django import forms
from .models import CustomUser
from django.core.exceptions import ValidationError
from Discussion.models import Question, Answer, Quiz, Session
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']


class SessionForm(forms.ModelForm):
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'placeholder': 'Select date and time'})
    )
    
    class Meta:
        model = Session
        fields = ['name', 'date', 'description']  # Include the description field
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter session title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter session description'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class DocumentForm(forms.Form):
    document = forms.FileField()

    def clean_document(self):
        document = self.cleaned_data.get('document')
        if document:
            # Validate that the file is a PDF
            if not document.name.endswith('.pdf'):
                raise ValidationError("Only PDF files are allowed.")
            # Optionally validate the MIME type
            if document.content_type != 'application/pdf':
                raise ValidationError("Uploaded file must be a valid PDF document.")
        return document