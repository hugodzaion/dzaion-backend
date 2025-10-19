# -*- coding: utf-8 -*-
"""
Módulo de Receivers (Ouvintes de Sinais) para o App 'finances'.

Este arquivo conecta o app de finanças a eventos que ocorrem em
outras partes do sistema, como a criação de novos usuários e tenants,
para automatizar a criação de suas respectivas carteiras (Wallets).

Author: Dzaion
Version: 0.1.0
"""
import logging
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from tenants.models import Tenant
from .services import FinanceService
from .exceptions import WalletAlreadyExistsError

# Configura um logger para este módulo
logger = logging.getLogger(__name__)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def handle_user_creation(sender, instance, created, **kwargs):
    """
    Cria uma Wallet automaticamente para cada novo User.
    """
    if created:
        try:
            FinanceService.create_wallet(owner=instance)
            logger.info(f"Carteira criada com sucesso para o usuário: {instance.email}")
        except WalletAlreadyExistsError:
            # Esta exceção não deve acontecer no fluxo normal 'if created',
            # mas é uma boa prática de segurança registrá-la caso ocorra.
            logger.warning(f"Tentativa de criar uma carteira duplicada para o usuário: {instance.email}")
        except Exception as e:
            logger.error(f"Erro ao criar carteira para o usuário {instance.email}: {e}", exc_info=True)


@receiver(post_save, sender=Tenant)
def handle_tenant_creation(sender, instance, created, **kwargs):
    """
    Cria uma Wallet automaticamente para cada novo Tenant.
    """
    if created:
        try:
            FinanceService.create_wallet(owner=instance)
            logger.info(f"Carteira criada com sucesso para o tenant: {instance.name}")
        except WalletAlreadyExistsError:
            logger.warning(f"Tentativa de criar uma carteira duplicada para o tenant: {instance.name}")
        except Exception as e:
            logger.error(f"Erro ao criar carteira para o tenant {instance.name}: {e}", exc_info=True)
