# -*- coding: utf-8 -*-
"""
Módulo de Receivers (Ouvintes de Sinais) para o App 'entitlements'.

Este arquivo conecta o app a eventos de mudança no modelo Subscription
para automatizar a concessão e revogação de permissões.

Author: Dzaion
Version: 0.1.0
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from guards.models import Role
from .models import Subscription

# Configura um logger para este módulo
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Subscription)
def handle_subscription_status_change(sender, instance: Subscription, **kwargs):
    """
    Atualiza dinamicamente as permissões dos papéis de administrador de um Tenant
    com base no status de suas assinaturas (Subscriptions).

    Esta é a peça central que conecta a compra de um módulo (Product) às
    permissões reais que ele concede (Permissions).
    """
    try:
        tenant = instance.tenant
        product = instance.plan.product
        permissions_to_manage = product.granted_permissions.all()

        if not permissions_to_manage.exists():
            return  # Módulo não concede nenhuma permissão, nada a fazer.

        # Encontra todos os papéis de administrador do Tenant.
        admin_roles = Role.objects.filter(tenant=tenant, is_admin_role=True)

        if not admin_roles.exists():
            logger.warning(f"Nenhum papel de administrador encontrado para o Tenant '{tenant.name}' ao processar a assinatura do módulo '{product.name}'.")
            return

        # Lógica para ADICIONAR ou REMOVER permissões.
        if instance.status in [Subscription.SubscriptionStatus.ACTIVE, Subscription.SubscriptionStatus.TRIAL]:
            # Assinatura está ativa ou em teste: concede as permissões.
            logger.info(f"Concedendo permissões do módulo '{product.name}' para os administradores do Tenant '{tenant.name}'.")
            for role in admin_roles:
                role.permissions.add(*permissions_to_manage)
        else:
            # Assinatura está inativa (CANCELED, PENDING, etc.): revoga as permissões.
            logger.info(f"Revogando permissões do módulo '{product.name}' para os administradores do Tenant '{tenant.name}'.")
            for role in admin_roles:
                role.permissions.remove(*permissions_to_manage)

    except Exception as e:
        logger.error(
            f"Erro ao processar o sinal de mudança de assinatura para a Subscription ID {instance.id}: {e}",
            exc_info=True
        )
