# -*- coding: utf-8 -*-
"""
Módulo de Views para o App 'guards'.

Contém os endpoints da API para o gerenciamento de Papéis (Roles).

Author: Dzaion
Version: 0.1.0
"""
from rest_framework import generics
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated

from .models import Role
from .serializers import RoleSerializer
from .permissions import HasTenantPermission

@extend_schema(summary="Listar Papéis (Roles) de um Tenant", tags=["Guards (Permissões)"])
class TenantRoleListView(generics.ListAPIView):
    """
    Endpoint para listar os papéis disponíveis dentro do contexto de um Tenant.
    Utilizado para popular seletores ao convidar ou editar membros.
    """
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, HasTenantPermission]
    required_permission = 'guards.view_role'

    def get_queryset(self):
        """
        Retorna apenas os papéis que pertencem ao Tenant especificado na URL.
        """
        return Role.objects.filter(tenant_id=self.kwargs['tenant_pk'])
