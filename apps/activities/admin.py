from django.contrib import admin

from activities.models import UserActivity

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'target', 'priority')
    list_display_links = ('created_at', 'user')
    list_filter = ('priority', 'target')
    search_fields = ('user__name', 'verb')