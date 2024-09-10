from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password

from accounts.models import Department, Role

class CustomUserAdmin(UserAdmin):

    list_display = ('username', 'email', 'department', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('department', 'role', 'profile_pic')}),
    )
    # Ensure the password is hashed when saving through the admin panel
    def save_model(self, request, obj, form, change):
        if change:  # If updating an existing user
            if 'password' in form.cleaned_data:
                password = form.cleaned_data['password']
                if not password.startswith('pbkdf2_sha256$'):  # If password is not hashed
                    obj.password = make_password(password)
        super().save_model(request, obj, form, change)

User = get_user_model()

admin.site.register(Department)
admin.site.register(Role)
admin.site.register(User, CustomUserAdmin)


