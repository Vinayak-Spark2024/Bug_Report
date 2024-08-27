# accounts/urls.py

from django.urls import path
from projects.views import (ProjectCreateView, ProjectListView,
                    ProjectUpdateView, ProjectUserView)
urlpatterns = [
    path('projects/', ProjectListView.as_view(), name='project-list'),  # View user's projects
    path('projects/user/', ProjectUserView.as_view(), name='project-user-view'),  # View user's projects
    path('projects/create/', ProjectCreateView.as_view(), name='project-create'),  # Create a new project
    path('projects/<int:pk>/', ProjectUpdateView.as_view(), name='project-update'),  # Update project status
]
