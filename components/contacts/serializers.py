# -*- coding: utf-8 -*-
"""
Módulo de Serializers para o App 'contacts'.

Author: Dzaion
Version: 0.1.0
"""
from rest_framework import serializers
from .models import ChannelContacts

class ChannelContactsSerializer(serializers.ModelSerializer):
    """Serializer para listar os Canais de Contato."""
    class Meta:
        model = ChannelContacts
        fields = ['id', 'name', 'icon']
