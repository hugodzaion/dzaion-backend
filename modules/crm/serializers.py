# -*- coding: utf-8 -*-
"""
Módulo de Serializers para o App 'crm'.

Author: Dzaion
Version: 0.1.0
"""
from rest_framework import serializers
from .models import Contact
from accounts.serializers import UserDetailSerializer

class ContactSerializer(serializers.ModelSerializer):
    """Serializer para exibir os detalhes de um Contato."""
    user = UserDetailSerializer(read_only=True)
    class Meta:
        model = Contact
        fields = '__all__'

class ContactCreateSerializer(serializers.ModelSerializer):
    """Serializer para a criação de um novo Contato."""
    class Meta:
        model = Contact
        fields = ['name', 'email', 'whatsapp', 'cpf', 'custom_data']
        extra_kwargs = {
            'email': {'required': False, 'allow_null': True},
            'whatsapp': {'required': False, 'allow_null': True},
            'cpf': {'required': False, 'allow_null': True},
            'custom_data': {'required': False},
        }

class LinkUserToContactSerializer(serializers.Serializer):
    """Serializer para validar o ID do usuário no momento do vínculo."""
    user_id = serializers.UUIDField(required=True)
