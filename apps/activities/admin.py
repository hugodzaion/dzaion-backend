# -*- coding: utf-8 -*-
"""
Módulo de Configuração do Django Admin para o App 'activities'.

Este módulo customiza a forma como o modelo UserActivity é exibido e
gerenciado no painel de administração do Django.

Author: Dzaion
Version: 1.0.0
"""
from django.contrib import admin
from .models import UserActivity

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo UserActivity.
    
    Otimizado para leitura e para lidar corretamente com os GenericForeignKeys.
    """

    # Campos a serem exibidos na lista de atividades
    list_display = (
        'id',
        'user',
        'verb',
        'display_actor',  # Usa nosso método customizado
        'display_target', # Usa nosso método customizado
        'timestamp',
    )

    # Adiciona filtros úteis na barra lateral
    list_filter = ('event_type', 'priority', 'timestamp')

    # Define todos os campos como somente leitura, pois atividades não devem ser editadas
    readonly_fields = [field.name for field in UserActivity._meta.fields]

    # --- MÉTODOS CUSTOMIZADOS PARA EXIBIR GFKs ---

    @admin.display(description='Ator')
    def display_actor(self, obj):
        """Retorna a representação em string do objeto 'ator'."""
        return str(obj.actor)

    @admin.display(description='Alvo')
    def display_target(self, obj):
        """Retorna a representação em string do objeto 'alvo'."""
        if obj.target:
            return str(obj.target)
        return "N/A"

    def has_add_permission(self, request):
        """Desativa o botão 'Adicionar' no admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Desativa a edição de atividades existentes."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Permite a exclusão por superusuários, se necessário."""
        return request.user.is_superuser
