# -*- coding: utf-8 -*-
"""
Módulo da Camada de Serviço para o App 'tenants'.

Este arquivo contém a classe TenantService, o único ponto de entrada para
operações de negócio complexas, como a criação de um novo Tenant,
garantindo a consistência entre os apps (tenants, guards, etc.).

Author: Dzaion
Version: 0.5.1
"""
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import Permission

from accounts.models import User
from guards.models import Role
from .models import Tenant, TenantMembership

class TenantService:
    """
    Serviço que centraliza a lógica de negócio para o gerenciamento de Tenants.
    """

    @staticmethod
    @transaction.atomic
    def create_tenant(owner: User, **tenant_data) -> Tenant:
        """
        Orquestra a criação completa de um novo Tenant e seus componentes essenciais.
        """
        # 1. Cria a entidade de negócio (O Inquilino)
        tenant = Tenant.objects.create(
            owner=owner,
            **tenant_data
        )

        # 2. Cria o papel de "superusuário" para este Tenant específico.
        admin_role = Role.objects.create(
            tenant=tenant,
            name=f"Administrador - {tenant.name}",
            is_admin_role=True
        )
        
        # DZAION-REFACTOR: O CRM não é mais um módulo base. As permissões
        # concedidas na criação são apenas as essenciais para a gestão do Tenant.
        # As permissões do CRM serão adicionadas dinamicamente quando o Tenant
        # assinar o produto correspondente.
        base_apps = ['tenants', 'guards', 'contacts', 'locations']
        base_permissions = Permission.objects.filter(
            content_type__app_label__in=base_apps
        )
        admin_role.permissions.set(base_permissions)

        # 3. Cria o vínculo de membro para o proprietário.
        #    Isso torna o criador do Tenant o seu primeiro administrador.
        TenantMembership.objects.create(
            user=owner,
            tenant=tenant,
            role=admin_role,
            status=TenantMembership.MembershipStatus.ACTIVE,
            joined_at=timezone.now()
        )

        return tenant

