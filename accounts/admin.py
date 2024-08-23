from django.contrib import admin
from accounts.models import Department, Role
from django.contrib.auth import get_user_model

User = get_user_model()

admin.site.register(Department)
admin.site.register(Role)
admin.site.register(User)


