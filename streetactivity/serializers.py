from rest_framework import serializers
from .models import StreetActivity, Reflection

class StreetActivitySerializer(serializers.ModelSerializer):
    """Serializer to convert Street Activity instance to JSON"""
    class Meta:
        model = StreetActivity
        fields = "__all__"

class ReflectionSerializer(serializers.ModelSerializer):
    """Serializer to convert Reflection instance to JSON"""
    class Meta:
        model = Reflection
        fields = "__all__"
