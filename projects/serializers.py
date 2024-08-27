# accounts/serializers.py

from rest_framework import serializers
from projects.models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'project_name', 'project_duration', 'status', 'users']
        read_only_fields = ['id', 'status']

    def validate(self, data):
        request = self.context.get('request')
        if request and request.method == 'POST':
            if not request.user.is_staff:
                raise serializers.ValidationError("Only staff members can create projects.")
        return data
