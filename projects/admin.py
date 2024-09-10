from django.contrib import admin
from projects.models import Project

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'project_duration', 'status', 'get_users')
    list_filter = ('status',)
    search_fields = ('project_name',)
    fieldsets = (
        (None, {
            'fields': ('project_name', 'project_duration', 'status', 'users')
        }),
    )
    filter_horizontal = ('users',)
    def get_users(self, obj):
        return ", ".join([user.username for user in obj.users.all()])
    get_users.short_description = 'Users'
    
admin.site.register(Project, ProjectAdmin)
