# -*- coding: utf-8 -*-
"""
Módulo de Classes de Permissão Customizadas para o App 'guards'.

Estas classes são usadas nas Views do DRF para proteger os endpoints
utilizando a lógica centralizada no GuardService.

Author: Dzaion
Version: 0.1.0
"""
from rest_framework.permissions import BasePermission
from tenants.models import Tenant
from .services import GuardService


class HasTenantPermission(BasePermission):
    """
    Permissão do DRF que verifica se um usuário possui um código de permissão
    específico, seja em um contexto global ou de tenant.

    A view que utiliza esta permissão DEVE definir um atributo de classe:
    `required_permission = 'app_label.codename'`
    """
    message = "Você não tem permissão para realizar esta ação."

    def has_permission(self, request, view):
        """
        Verifica a permissão usando o GuardService.
        """
        user = request.user
        if not user or not user.is_authenticated:
            return False
            
        # Pega o código da permissão que a view declarou como necessária.
        permission_code = getattr(view, 'required_permission', None)
        if not permission_code:
            # Erro de configuração do desenvolvedor: esqueceu de definir a permissão na view.
            # Por segurança, negamos o acesso.
            return False

        tenant = None
        # Tenta extrair o 'tenant_id' dos parâmetros da URL (kwargs da view).
        # Isso permite proteger URLs como /api/tenants/<tenant_id>/invoices/
        tenant_id = view.kwargs.get('tenant_id') or view.kwargs.get('tenant_pk')
        if tenant_id:
            try:
                # Busca o objeto Tenant para passar como contexto ao GuardService.
                tenant = Tenant.objects.get(pk=tenant_id)
            except Tenant.DoesNotExist:
                # Se o tenant da URL não existe, nega o acesso.
                return False

        # Delega a verificação final para o nosso serviço centralizado.
        return GuardService.user_has_permission(
            user=user,
            permission_code=permission_code,
            tenant=tenant
        )
