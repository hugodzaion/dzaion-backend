# -*- coding: utf-8 -*-
"""
Módulo de Serializers para o App 'locations'.

Define os schemas para a representação JSON dos modelos de localização.

Author: Dzaion
Version: 0.1.0
"""
from rest_framework import serializers
from .models import State, Location

class StateSerializer(serializers.ModelSerializer):
    """Serializer para listar os Estados."""
    class Meta:
        model = State
        fields = ['id', 'name']

class LocationSerializer(serializers.ModelSerializer):
    """Serializer para listar as Localidades (cidades)."""
    class Meta:
        model = Location
        fields = ['id', 'city']
