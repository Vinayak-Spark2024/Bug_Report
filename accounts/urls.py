# accounts/urls.py

from django.urls import path

from accounts.views import (RegisterView, LoginView, LogoutView, 
                            DepartmentListCreateView,RoleListCreateView,
                            DepartmentRetrieveUpdateDestroyView, 
                            RoleRetrieveUpdateDestroyView, CustomUserListView, 
                            CustomUserDetailView, UserProfileView)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('departments/', DepartmentListCreateView.as_view(), name='department-list-create'),
    path('departments/<int:pk>/', DepartmentRetrieveUpdateDestroyView.as_view(), name='department-retrieve-update-destroy'),
    path('role/', RoleListCreateView.as_view(), name='role-list-create'),
    path('role/<int:pk>/', RoleRetrieveUpdateDestroyView.as_view(), name='role-retrieve-update-destroy'),
    path('users/', CustomUserListView.as_view(), name='user-list'),
    path('user/<int:pk>/', CustomUserDetailView.as_view(), name='user-detail'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),

]
