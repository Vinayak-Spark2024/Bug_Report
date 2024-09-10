from rest_framework import serializers

from bug.models import Bug

from django.contrib.auth import get_user_model

User = get_user_model()
class BugSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bug
        fields = '__all__'
        read_only_fields = ['created_by', 'report_date', 'updated_date', 'is_current_project']

    def update(self, instance, validated_data):
        # Handle project assignment explicitly
        project = validated_data.get('project', None)
        if project is not None:
            instance.project = project
        return super().update(instance, validated_data)

    def validate_assigned_to(self, value):
        project = self.instance.project if self.instance else self.initial_data.get('project') 
        if project and not User.objects.filter(id=value.id, projects__id=project.id).exists():
            raise serializers.ValidationError("Assigned user must be part of the project.")
        
        return value