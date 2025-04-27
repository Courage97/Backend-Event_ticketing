from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'start_date', 'is_published', 'is_paid')
    list_filter = ('is_published', 'is_paid')
    search_fields = ('title', 'organizer__username')
