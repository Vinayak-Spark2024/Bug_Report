from django.contrib import admin
from .models import Bug

class BugAdmin(admin.ModelAdmin):
    list_display = ('bug_type', 'status', 'bug_priority', 'bug_severity', 'created_by', 'assigned_to', 'project', 'is_current_project')
    list_filter = ('bug_type', 'status', 'bug_priority', 'bug_severity', 'project')
    search_fields = ('bug_description', 'created_by__username', 'assigned_to__username', 'project__project_name')
    ordering = ('-report_date',)
    readonly_fields = ('report_date', 'updated_date')

    fieldsets = (
        (None, {
            'fields': ('bug_type', 'bug_description', 'url_bug', 'image', 'project', 'bug_priority', 'bug_severity', 'status', 'is_current_project')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Dates', {
            'fields': ('report_date', 'updated_date')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Bug, BugAdmin)
