# accounts/serializers.py

from rest_framework import serializers
from .models import CustomUser, Department, Role
from django.contrib.auth.hashers import make_password

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields =  ['name']

class CustomUserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    role = RoleSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'department', 'role', 'profile_pic', 'is_staff']

    def update(self, instance, validated_data):
        # Check if 'is_staff' is in validated_data and the current user is trying to change it
        if 'is_staff' in validated_data:
            # Only allow changing 'is_staff' if the user is already staff
            if not self.context['request'].user.is_staff:
                raise serializers.ValidationError("You do not have permission to change the 'is_staff' status.")
        
        return super().update(instance, validated_data)
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'department', 'role', 'profile_pic', 'is_staff']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        user = super(RegisterSerializer, self).create(validated_data)
        user.save()  # This will trigger the custom save logic in CustomUser
        return user
