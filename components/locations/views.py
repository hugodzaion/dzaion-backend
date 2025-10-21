# -*- coding: utf-8 -*-
"""
Módulo de Views para o App 'locations'.

Contém os endpoints da API para listar estados e cidades.

Author: Dzaion
Version: 0.1.0
"""
from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import State, Location
from .serializers import StateSerializer, LocationSerializer

@extend_schema(
    summary="Listar todos os Estados",
    tags=["Localidades"],
)
class StateListView(generics.ListAPIView):
    queryset = State.objects.all().order_by('name')
    serializer_class = StateSerializer

@extend_schema(
    summary="Listar Cidades de um Estado",
    tags=["Localidades"],
)
class CityListView(generics.ListAPIView):
    serializer_class = LocationSerializer

    def get_queryset(self):
        """Filtra as cidades pelo ID do estado fornecido na URL."""
        state_id = self.kwargs.get('state_id')
        return Location.objects.filter(state_id=state_id).order_by('city')
