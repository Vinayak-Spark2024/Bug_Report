from rest_framework import serializers

from bug.models import Bug

class BugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bug
        fields = '__all__'
        read_only_fields = ['created_by', 'report_date', 'updated_date', 'is_current_project']
