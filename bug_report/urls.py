# myproject/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')), 
    path('api/', include('projects.urls')), 
    path('api/', include('bug.urls')),
]