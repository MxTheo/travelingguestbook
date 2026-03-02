from rest_framework import serializers
from .models import StreetActivity, Word

class StreetActivitySerializer(serializers.ModelSerializer):
    """Serializer to convert Street Activity instance to JSON"""
    class Meta:
        model = StreetActivity
        fields = "__all__"

class WordSerializer(serializers.ModelSerializer):
    """Serializer to convert Word instance to JSON"""
    class Meta:
        model = Word
        fields = "__all__"
