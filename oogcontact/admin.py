from django.contrib import admin
from .models import Registration

class RegistrationAdmin(admin.ModelAdmin):
    '''Admin interface for the Registration model.'''
    list_display = ('number', 'name', 'email', 'date_created', 'hasCanceled')
    search_fields = ('name', 'email')
    list_filter = ('hasCanceled', 'date_created')
    ordering = ('-date_created',)
    readonly_fields = ('date_created', 'number')

admin.site.register(Registration, RegistrationAdmin)
