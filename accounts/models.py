from django.contrib.auth.models import AbstractUser
from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.name = "_".join(self.name.lower().split())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.name = "_".join(self.name.lower().split())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    is_staff = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.role and self.role.name == 'manager':
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
