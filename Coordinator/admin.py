from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, Role

class CustomUserAdmin(UserAdmin):
    model = CustomUser

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register( Profile)
admin.site.register( Role)
# admin.site.register( Quiz)
# admin.site.register( Question)
# admin.site.register( Answer)
# admin.site.register( QuizRecord)