from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response


from bug.models import Bug
from bug.serializers import BugSerializer

class BugCreateView(generics.CreateAPIView):
    queryset = Bug.objects.all()
    serializer_class = BugSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class BugListView(generics.ListAPIView):
    queryset = Bug.objects.all()
    serializer_class = BugSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        status_filter = self.kwargs.get('status', None)
        queryset = Bug.objects.all()

        if status_filter == 'open':
            queryset = queryset.filter(status='open')
        elif status_filter == 'closed':
            queryset = queryset.filter(status='closed')
        elif status_filter == 'in_progress':
            queryset = queryset.filter(status='in_progress')

        return queryset

class UserBugsListView(generics.ListAPIView):
    serializer_class = BugSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        status_filter = self.kwargs.get('status', None)
        queryset = Bug.objects.filter(assigned_to=self.request.user)

        if status_filter == 'open':
            queryset = queryset.filter(status='open')
        elif status_filter == 'closed':
            queryset = queryset.filter(status='closed')
        elif status_filter == 'in_progress':
            queryset = queryset.filter(status='in_progress')

        return queryset

class AdminBugUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Bug.objects.all()
    serializer_class = BugSerializer
    permission_classes = [permissions.IsAdminUser]

    
class BugUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Bug.objects.all()
    serializer_class = BugSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        bug = super().get_object()
        if bug.assigned_to != self.request.user:
            raise PermissionDenied(detail="You do not have permission to update this bug.")
        return bug

    def update(self, request, *args, **kwargs):
        # Ensure project is included in validated_data during the update
        return super().update(request, *args, **kwargs)

