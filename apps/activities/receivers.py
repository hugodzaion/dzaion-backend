# -*- coding: utf-8 -*-
"""
Módulo de Receivers (Ouvintes de Sinais) para o App 'activities'.

Conecta o app de atividades a eventos significativos que ocorrem em
todo o ecossistema para popular o feed do usuário em tempo real.

Author: Dzaion
Version: 0.3.0
"""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from tenants.models import TenantMembership
from finances.models import Wallet, Invoice
from .services import create_activity
from .models import UserActivity

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def handle_user_creation(sender, instance, created, **kwargs):
    """
    Registra a criação de um novo usuário no feed de atividades.
    """
    if created:
        # DZAION-FIX: Usando o valor em string para evitar erro de importação circular.
        create_activity(
            user=instance,
            actor=instance,
            verb='se cadastrou na plataforma Dzaion',
            event_type='ADMINISTRATIVO'
        )

# --- DZAION-FINANCES: Conectando o feed de atividades aos eventos financeiros ---

@receiver(post_save, sender=Wallet)
def handle_wallet_creation(sender, instance: Wallet, created, **kwargs):
    """
    Registra a criação de uma nova carteira de usuário no feed.
    """
    if created and instance.user:
        # Regra: A criação de uma carteira pessoal só aparece no feed do próprio usuário.
        create_activity(
            user=instance.user,
            actor=instance.user,
            verb='recebeu sua carteira de créditos',
            target=instance,
            # DZAION-FIX: Usando o valor em string.
            event_type='FINANCEIRO'
        )

@receiver(post_save, sender=Invoice)
def handle_invoice_creation(sender, instance: Invoice, created, **kwargs):
    """
    Registra a criação de uma nova fatura no feed dos usuários relevantes do Tenant.
    """
    if created and instance.status == Invoice.InvoiceStatus.OPEN:
        tenant = instance.tenant
        financial_contact = tenant.financial_contact
        admin_memberships = TenantMembership.objects.filter(
            tenant=tenant,
            role__is_admin_role=True,
            status=TenantMembership.MembershipStatus.ACTIVE
        ).select_related('user')
        
        admin_users = {membership.user for membership in admin_memberships}
        recipients = admin_users
        recipients.add(financial_contact)

        verb = f"A fatura #{instance.id.hex[:8]} no valor de R$ {instance.amount} foi gerada."

        for user in recipients:
            create_activity(
                user=user,
                actor=tenant,
                verb=verb,
                target=instance,
                # DZAION-FIX: Usando os valores em string.
                event_type='FINANCEIRO',
                priority='ALTA'
            )

