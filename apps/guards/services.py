# -*- coding: utf-8 -*-
"""
Módulo da Camada de Serviço para o App 'guards'.

Este arquivo contém a classe GuardService, que é o único ponto de entrada
para toda a lógica de verificação de permissões no ecossistema.
Ele abstrai a complexidade de consolidar papéis globais e de tenant.

Author: Dzaion
Version: 0.2.0
"""
from django.contrib.auth.models import Permission
from django.db.models import QuerySet, Q

from accounts.models import User
from dzaion.models import DzaionAction
from tenants.models import Tenant, TenantMembership


class GuardService:
    """
    Serviço que centraliza toda a lógica de Controle de Acesso Baseado em Papéis (RBAC).
    """

    @staticmethod
    def get_user_permissions(user: User, tenant: Tenant | None = None) -> QuerySet[Permission]:
        """
        Consolida e retorna um queryset de todas as permissões de Módulos (Permission)
        que um usuário possui, combinando seus papéis globais e de tenant.
        """
        role_ids = set(user.roles.filter(tenant__isnull=True).values_list('id', flat=True))

        if tenant:
            try:
                membership = TenantMembership.objects.get(user=user, tenant=tenant, status='ACTIVE')
                role_ids.add(membership.role.id)
            except TenantMembership.DoesNotExist:
                pass
        
        if not role_ids:
            return Permission.objects.none()
        
        # DZAION-FIX: Corrigida a consulta para usar a relação reversa 'role_set'.
        return Permission.objects.filter(role__id__in=list(role_ids)).distinct()

    @staticmethod
    def get_user_dzaion_actions(user: User, tenant: Tenant | None = None) -> QuerySet[DzaionAction]:
        """
        Consolida e retorna um queryset de todas as capacidades da IA (DzaionAction)
        que um usuário possui.
        """
        role_ids = set(user.roles.filter(tenant__isnull=True).values_list('id', flat=True))

        if tenant:
            try:
                membership = TenantMembership.objects.get(user=user, tenant=tenant, status='ACTIVE')
                role_ids.add(membership.role.id)
            except TenantMembership.DoesNotExist:
                pass

        if not role_ids:
            return DzaionAction.objects.none()

        # DZAION-FIX: Corrigida a consulta para usar a relação reversa 'role_set'.
        return DzaionAction.objects.filter(role__id__in=list(role_ids)).distinct()

    @staticmethod
    def user_has_permission(user: User, permission_code: str, tenant: Tenant | None = None) -> bool:
        """
        Verifica de forma rápida e eficiente se um usuário possui uma permissão específica.
        """
        try:
            app_label, codename = permission_code.split('.')
        except (ValueError, AttributeError):
            return False

        # Agora esta chamada utiliza a lógica corrigida.
        user_permissions = GuardService.get_user_permissions(user, tenant)
        
        return user_permissions.filter(
            content_type__app_label=app_label,
            codename=codename
        ).exists()

