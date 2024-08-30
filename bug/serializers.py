from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

from bug.models import Bug

class BugSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bug
        fields = '__all__'
        read_only_fields = ['created_by', 'report_date', 'updated_date', 'is_current_project']

    def validate_assigned_to(self, value):
        project = self.instance.project if self.instance else self.initial_data.get('project') 
        if project and not User.objects.filter(id=value.id, projects__id=project).exists():
            raise serializers.ValidationError("Assigned user must be part of the project.")
        
        return value