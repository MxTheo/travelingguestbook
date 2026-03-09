from django import template
from django.core.serializers.json import DjangoJSONEncoder
import json

register = template.Library()

@register.filter
def json_script(value):
    """Convert value to JSON-safe string for embedding in script tags."""
    return json.dumps(value, cls=DjangoJSONEncoder)