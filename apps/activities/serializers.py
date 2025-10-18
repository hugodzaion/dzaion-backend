# -*- coding: utf-8 -*-
"""
Módulo de Serializers para o App 'activities'.

Define os schemas para a representação JSON dos registros de UserActivity.
É otimizado para leitura e para lidar com as relações genéricas de 'ator' e 'alvo'.

Author: Dzaion
Version: 1.0.0
"""
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import UserActivity

class RelatedObjectSerializer(serializers.ModelSerializer):
    """
    Um serializer genérico para representar o ator e o alvo de uma atividade.
    Retorna o ID e a representação em string do objeto relacionado.
    """
    id = serializers.UUIDField(source='pk', read_only=True)
    name = serializers.CharField(source='__str__', read_only=True)

    class Meta:
        fields = ['id', 'name']

    def __init__(self, *args, **kwargs):
        # A propriedade 'model' é definida dinamicamente
        self.Meta.model = kwargs.pop('model', None)
        super().__init__(*args, **kwargs)

class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer para listar as atividades no feed do usuário.
    """
    actor = serializers.SerializerMethodField(help_text="O objeto que realizou a ação.")
    target = serializers.SerializerMethodField(help_text="O objeto que sofreu a ação (opcional).")

    class Meta:
        model = UserActivity
        fields = [
            'id',
            'actor',
            'verb',
            'target',
            'event_type',
            'timestamp',
            'priority',
            'is_read',
        ]
        read_only_fields = fields

    def get_related_object_data(self, obj, field_name):
        """
        Função auxiliar para serializar objetos de GenericForeignKey.
        """
        related_obj = getattr(obj, field_name, None)
        if related_obj is None:
            return None
        
        # Usa o serializer genérico para representar o objeto
        serializer = RelatedObjectSerializer(related_obj, model=type(related_obj))
        return serializer.data

    def get_actor(self, obj):
        return self.get_related_object_data(obj, 'actor')

    def get_target(self, obj):
        return self.get_related_object_data(obj, 'target')
