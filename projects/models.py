from django.db import models
from accounts.models import CustomUser
class Project(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed')
    ]

    project_name = models.CharField(max_length=255)
    project_duration = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    users = models.ManyToManyField(CustomUser,  related_name='projects')
    
    def __str__(self):
        return self.project_name