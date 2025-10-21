# -*- coding: utf-8 -*-
"""
Módulo de Views para o App 'contacts'.

Author: Dzaion
Version: 0.1.0
"""
from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import ChannelContacts
from .serializers import ChannelContactsSerializer

@extend_schema(
    summary="Listar todos os Canais de Contato disponíveis",
    tags=["Contatos"],
)
class ChannelContactsListView(generics.ListAPIView):
    queryset = ChannelContacts.objects.all()
    serializer_class = ChannelContactsSerializer
