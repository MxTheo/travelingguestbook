from django.contrib import admin
from django.db import models

from .models import StreetActivity, Reflection

admin.site.register(StreetActivity)


@admin.register(Reflection)
class ReflectionAdmin(admin.ModelAdmin):
	formfield_overrides = {
		models.URLField: {"assume_scheme": "https"},
	}
