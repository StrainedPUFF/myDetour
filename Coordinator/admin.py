from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, Role

# admin.site.site_header = "my detour"
# admin.site.site_title = "My App Admin Panel"
# admin.site.index_title = "Welcome to My App Admin Panel"

# class CustomUserAdmin(UserAdmin):
#     model = CustomUser



class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = (
        ('Personal Info', {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )




admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register( Profile)
admin.site.register( Role)

