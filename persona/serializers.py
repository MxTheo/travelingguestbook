from rest_framework import serializers
from .models import Persona, Problem, Reaction

class PersonaSerializer(serializers.ModelSerializer):
    """Serializer to convert Persona instance to JSON"""
    class Meta:
        model = Persona
        fields = '__all__'

class ProblemSerializer(serializers.ModelSerializer):
    """Serializer to convert Problem instance to JSON"""
    class Meta:
        model = Problem
        fields = '__all__'

class ReactionSerializer(serializers.ModelSerializer):
    """Serializer to convert Reaction instance to JSON"""
    class Meta:
        model = Reaction
        fields = '__all__'