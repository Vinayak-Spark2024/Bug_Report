from rest_framework import serializers
from projects.models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'project_name', 'project_duration', 'status', 'users']
        # Removed 'status' from read_only_fields to allow updates

    def validate_project_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Project name must be at least 3 characters long.")

        if Project.objects.filter(project_name=value).exists():
            raise serializers.ValidationError("A project with this name already exists.")
        return value

    def validate_project_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Project duration must be a positive integer.")
        return value

    def validate_status(self, value):
        valid_statuses = ['open', 'closed']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status value. Valid statuses are: {', '.join(valid_statuses)}.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request and request.method == 'POST':
            if not request.user.is_staff:
                raise serializers.ValidationError("Only staff members can create projects.")
        return data
