"""
URL configuration for VirtualLCS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from Coordinator import views
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from .settings import BASE_DIR
import os

urlpatterns = [
    path('Coordinator/', include('Coordinator.urls')),
    path('Discussion/', include('Discussion.urls')),            # Move to its own subpath
    path('admin/', admin.site.urls),
    path('api/get-session-id/', views.get_session_id, name='get-session-id'),
    path('attempt-quiz/<int:quiz_id>/react/', views.ReactAppView.as_view(), name='attempt_quiz_react'),  # Optional new pattern
    path('attempt-quiz/<int:quiz_id>/', views.attempt_quiz, name='attempt_quiz'),
    path('api/session-data/<str:session_id>/', views.session_data, name='session_data'),
    path('react/', views.ReactAppView.as_view(), name='react-app'),  # React app specific
    path('', views.ReactAppView.as_view(), name='react-root')        # Serve React for root
] + debug_toolbar_urls()


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static('/react/', document_root=os.path.join(BASE_DIR, 'frontend/build'))
