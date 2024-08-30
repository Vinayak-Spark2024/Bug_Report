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
        status = self.kwargs.get('status', None)
        queryset = Bug.objects.all()
        
        if status == 'open':
            queryset = queryset.filter(status='open')
        elif status == 'closed':
            queryset = queryset.filter(status='closed')
        else:
            queryset = queryset.filter(status='in_progress')
        
        return queryset

class UserBugsListView(generics.ListAPIView):
    serializer_class = BugSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        status = self.kwargs.get('status', None)
        queryset = Bug.objects.filter(assigned_to=self.request.user)
        
        if status == 'open':
            queryset = queryset.filter(status='open')
        elif status == 'closed':
            queryset = queryset.filter(status='closed')
        else:
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

    def get_queryset(self):
        return Bug.objects.filter(assigned_to=self.request.user)
    def update(self, request, *args, **kwargs):
        bug = self.get_object()
        if bug.assigned_to != request.user:
            unauthorized_bug_data = {
                'detail': 'You do not have permissions to perform this task.',
                'bug_id': bug.id,
                'assigned_to': bug.assigned_to.username,
            }
            return Response(unauthorized_bug_data, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)