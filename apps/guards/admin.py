# -*- coding: utf-8 -*-
"""
Módulo de Configuração do Django Admin para o App 'guards'.

Este módulo customiza a forma como o modelo Role é exibido e
gerenciado no painel de administração do Django.

Author: Dzaion
Version: 0.2.0
"""
from django.contrib import admin
from .models import Role

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo Role.
    """
    list_display = ('name', 'tenant', 'is_admin_role')
    list_filter = ('tenant', 'is_admin_role')
    search_fields = ('name', 'tenant__name')
    
    # Melhora a interface para campos ManyToMany, conforme solicitado na documentação.
    filter_horizontal = ('permissions', 'dzaion_actions')

