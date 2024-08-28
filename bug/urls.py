from django.urls import path

from bug.views import (BugCreateView, BugListView, 
    UserBugsListView, AdminBugUpdateView, BugUpdateView)

urlpatterns = [
    path('bugs/create/', BugCreateView.as_view(), name='bug-create'),
    path('bugs/', BugListView.as_view(), name='bug-list'),
    path('bugs/open/', BugListView.as_view(), {'status': 'open'}, name='admin-open-bugs'),
    path('bugs/closed/', BugListView.as_view(), {'status': 'closed'}, name='admin-closed-bugs'),
    path('bugs/in_progress/', BugListView.as_view(), {'status': 'in-progress'}, name='admin-in_progress-bugs'),
    path('bugs/user/', UserBugsListView.as_view(), name='user-bugs'),
    path('bugs/user/open/', UserBugsListView.as_view(), {'status': 'open'}, name='user-open-bugs'),
    path('bugs/user/closed/', UserBugsListView.as_view(), {'status': 'closed'}, name='user-closed-bugs'),
    path('bugs/user/in_progress/', UserBugsListView.as_view(), {'status': 'in-progress'}, name='user-in_progress-bugs'),
    path('bugs/admin/<int:pk>/', AdminBugUpdateView.as_view(), name='admin-bug-update'),
    path('bugs/user/<int:pk>/', BugUpdateView.as_view(), name='user-bug-update'),
]
