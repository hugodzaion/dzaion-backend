from django.contrib import admin

from accounts.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'whatsapp', 'is_superuser', 'is_active')
    list_display_links = ("id", "name")
    search_fields = ("name",)
