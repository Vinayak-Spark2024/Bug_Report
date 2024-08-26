# accounts/views.py

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Project
from .serializers import ProjectSerializer

class ProjectCreateView(generics.CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        # Ensure that only staff members can create projects
        if self.request.user.is_staff:
            serializer.save()
        else:
            raise PermissionError("Only staff members can create projects.")

class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get_queryset(self):
        # If the user is a staff member, return all projects
        if self.request.user.is_staff:
            return Project.objects.all()
        # Otherwise, return only the projects the user is associated with
        return Project.objects.filter(users=self.request.user)

class ProjectUpdateView(generics.UpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure users can only update projects they are a part of
        return Project.objects.filter(users=self.request.user)
