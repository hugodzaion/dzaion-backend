# -*- coding: utf-8 -*-
"""
Módulo de Serializers para o App 'guards'.

Author: Dzaion
Version: 0.1.0
"""
from rest_framework import serializers
from .models import Role

class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer para listar os Papéis (Roles) de um Tenant.
    """
    class Meta:
        model = Role
        fields = ['id', 'name', 'is_admin_role']
