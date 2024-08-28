# accounts/serializers.py

from rest_framework import serializers
from projects.models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'project_name', 'project_duration', 'status', 'users']
        read_only_fields = ['id', 'status']

    def validate_project_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Project name must be at least 3 characters long.")
        return value

    def validate_project_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Project duration must be a positive integer.")
        return value

    def validate_status(self, value):
        if value not in dict(Project.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status value.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request and request.method == 'POST':
            if not request.user.is_staff:
                raise serializers.ValidationError("Only staff members can create projects.")
        return data
