# -*- coding: utf-8 -*-
"""
Módulo de Permissões Customizadas para o App 'products'.

Author: Dzaion
Version: 0.1.0
"""
from rest_framework.permissions import BasePermission

class IsAdminOrSuperuser(BasePermission):
    """
    Permite acesso apenas a usuários que são staff (podem acessar o Django Admin)
    ou superusuários. Ideal para proteger endpoints de administração do sistema.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
        )
