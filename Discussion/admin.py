from django.contrib import admin
from .models import Session,  UserRoleInSession, Quiz, Question, Answer, QuizRecord
# Register your models here.
admin.site.register(Session)
admin.site.register(UserRoleInSession)
admin.site.register( Quiz)
admin.site.register( Question)
admin.site.register( Answer)
admin.site.register( QuizRecord)