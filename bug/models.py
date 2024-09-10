from django.db import models
from django.contrib.auth import get_user_model

from projects.models import Project

User = get_user_model()

class Bug(models.Model):
    BUG_TYPE_CHOICES = [
        ('error', 'Error'),
        ('mistake', 'Mistake'),
        ('bug', 'Bug'),
        ('issue', 'Issue'),
        ('fault', 'Fault'),
        ('defect', 'Defect'),
        ('other', 'Other')
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('in_progress', 'In Progress')
    ]

    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('normal', 'Normal'),
        ('minor', 'Minor'),
        ('trivial', 'Trivial'),
        ('enhancements', 'Enhancements/Feature Requests')
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]
    bug_type = models.CharField(max_length=20, choices=BUG_TYPE_CHOICES)
    created_by = models.ForeignKey(User, related_name='created_bugs', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, related_name='assigned_bugs', on_delete=models.SET_NULL, null=True, blank=True)
    report_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    bug_description = models.TextField()
    url_bug = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='bugs/', blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    bug_priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    bug_severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    is_current_project = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} - {self.bug_type} - {self.status}"