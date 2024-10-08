# accounts/serializers.py

from rest_framework import serializers

from accounts.models import CustomUser, Department, Role

from django.contrib.auth.hashers import make_password

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields =  ['id', 'name']
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)                                                                                                                                      
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'department', 'role', 'profile_pic', 'is_staff']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        user = super(RegisterSerializer, self).create(validated_data)
        user.save() 
        return user

