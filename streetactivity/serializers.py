from rest_framework import serializers
from .models import StreetActivity, Moment

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