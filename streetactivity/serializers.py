from rest_framework import serializers
from .models import StreetActivity

class StreetActivitySerializer(serializers.ModelSerializer):
    """Serializer to convert Street Activity instance to JSON"""
    class Meta:
        model = StreetActivity
        fields = "__all__"