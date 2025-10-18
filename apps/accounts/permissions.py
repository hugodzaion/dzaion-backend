# -*- coding: utf-8 -*-
"""
Módulo de Permissões Customizadas para o App 'accounts'.

Author: Dzaion
Version: 0.1.0
"""
from rest_framework.permissions import BasePermission

# Verificação de usuário ativo
class IsActiveUser(BasePermission):
    """
    Permissão customizada que verifica se o usuário está autenticado e ativo.
    Retorna uma mensagem de erro clara caso o usuário esteja inativo.
    """
    # DZAION-FIX: Mensagem de erro customizada que será retornada pela API
    # quando esta permissão falhar.
    message = "Sua conta está desativada. Por favor, complete o processo de ativação."

    def has_permission(self, request, view):
        """
        Retorna `True` se o usuário estiver autenticado e com a flag `is_active`.
        """
        # A permissão IsAuthenticated geralmente é executada antes, mas mantemos
        # a verificação completa aqui para garantir a robustez caso a classe
        # seja usada de forma isolada.
        return bool(request.user and request.user.is_authenticated and request.user.is_active)

    
