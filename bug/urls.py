from django.urls import path

from bug.views import (BugCreateView, BugListView, 
    UserBugsListView, AdminBugUpdateView, BugUpdateView)

urlpatterns = [
    path('bugs/create/', BugCreateView.as_view(), name='bug-create'),
    path('bugs/', BugListView.as_view(), name='bug-list'),
    path('bugs/status/<str:status>/', BugListView.as_view(), name='admin-status-bugs'),
    path('bugs/user/', UserBugsListView.as_view(), name='user-bugs'),
    path('bugs/user/status/<str:status>/', UserBugsListView.as_view(), name='user-status-bugs'),
    path('bugs/admin/<int:pk>/', AdminBugUpdateView.as_view(), name='admin-bug-update'),
    path('bugs/user/<int:pk>/', BugUpdateView.as_view(), name='user-bug-update'),
]
