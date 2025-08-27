from django.contrib import admin
from .models import Registration

admin.site.register(Registration)

class RegistrationAdmin(admin.ModelAdmin):
    '''Admin interface for the Registration model.'''
    list_display = ('number', 'name', 'email', 'date_created', 'hasCanceled')
    search_fields = ('name', 'email')
    list_filter = ('hasCanceled', 'date_created')
    ordering = ('-date_created',)