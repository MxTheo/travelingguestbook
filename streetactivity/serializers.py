from rest_framework import serializers
from .models import StreetActivity, Moment, Experience

class StreetActivitySerializer(serializers.ModelSerializer):
    """Serializer to convert Street Activity instance to JSON"""
    class Meta:
        model = StreetActivity
        fields = "__all__"

class MomentSerializer(serializers.ModelSerializer):
    """Serializer to convert Moment instance to JSON"""
    class Meta:
        model = Moment
        fields = "__all__"

class ExperienceSerializer(serializers.ModelSerializer):
    """Serializer to convert Experience instance to JSON"""
    class Meta:
        model = Experience
        fields = "__all__"