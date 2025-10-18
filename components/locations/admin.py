from django.contrib import admin

from locations.models import Location, Country, State

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    search_fields = ('name',)

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('country', 'name')
    list_display_links = ('country', 'name')
    search_fields = ('country__name', 'name')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'state')
    list_display_links = ('city', 'state')
    search_fields = ('country__name', 'city', 'state__name')