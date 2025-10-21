# -*- coding: utf-8 -*-
"""
Módulo de Modelos para o App 'entitlements'.

Este módulo define os contratos comerciais que governam o acesso
dos Tenants e Usuários aos serviços da plataforma, como Assinaturas
de Módulos e Perfis de Uso da IA.

Author: Dzaion
Version: 0.1.0
"""
from django.conf import settings
from django.db import models
from django.db.models import Q

from core.models import BaseModel
from products.models import ProductPlan
from tenants.models import Tenant
# TODO: Descomentar a linha abaixo quando o modelo AIModel for criado.
# from dzaion.models import AIModel


class Subscription(BaseModel):
    """
    O contrato formal que concede a um Tenant o direito de usar um Módulo.
    Funciona como um "snapshot" dos termos no momento da aquisição.
    """
    class SubscriptionStatus(models.TextChoices):
        TRIAL = 'TRIAL', 'Em Teste'
        ACTIVE = 'ACTIVE', 'Ativa'
        PENDING = 'PENDING', 'Pendente'
        CANCELED = 'CANCELED', 'Cancelada'
        INCOMPLETE = 'INCOMPLETE', 'Incompleta'

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Assinante (Inquilino)'
    )
    plan = models.ForeignKey(
        ProductPlan,
        on_delete=models.PROTECT,
        verbose_name='Plano de Referência',
        help_text='Aponta para o plano que originou a assinatura (histórico).'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Preço (Snapshot)',
        help_text='O preço exato que o inquilino concordou em pagar. Imutável.'
    )
    billing_cycle_details = models.JSONField(
        verbose_name='Detalhes do Ciclo (Snapshot)',
        help_text='Cópia dos detalhes do ciclo de cobrança (ex: {"period": "MONTHLY", "discount": 10}).'
    )
    features_snapshot = models.JSONField(
        verbose_name='Funcionalidades (Snapshot)',
        help_text='A lista exata de features contratadas no momento da aquisição.'
    )
    status = models.CharField(
        max_length=15,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.INCOMPLETE,
        verbose_name='Status do Contrato'
    )
    start_date = models.DateField(
        verbose_name='Início da Vigência'
    )
    end_date = models.DateField(
        null=True, blank=True,
        verbose_name='Fim da Vigência',
        help_text='Preenchido apenas para assinaturas canceladas.'
    )
    next_billing_date = models.DateField(
        verbose_name='Próxima Cobrança'
    )
    gateway_subscription_id = models.CharField(
        max_length=255,
        null=True, blank=True,
        unique=True,
        verbose_name='ID da Assinatura no Gateway',
        help_text='O identificador da assinatura no gateway de pagamento.'
    )

    class Meta:
        verbose_name = 'Assinatura de Módulo'
        verbose_name_plural = 'Assinaturas de Módulos'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'plan'],
                condition=Q(status__in=['ACTIVE', 'TRIAL']),
                name='unique_active_subscription_per_tenant_plan'
            )
        ]

    def __str__(self):
        return f"Assinatura de {self.plan.product.name} para {self.tenant.name}"


class DzaionUsageProfile(BaseModel):
    """
    O perfil que define os termos comerciais e de configuração para o uso do Dzaion IA.
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='dzaion_usage_profile',
        verbose_name='Inquilino (Contratante)'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='dzaion_usage_profile',
        verbose_name='Usuário (Contratante)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Contrato Ativo',
        help_text='Interruptor geral para ativar ou desativar o acesso do contratante à IA.'
    )
    credit_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True, blank=True,
        verbose_name='Limite de Crédito (R$)',
        help_text='O limite de gastos. Nulo significa ilimitado.'
    )
    # TODO: Descomentar os campos abaixo quando o modelo AIModel for criado.
    # model_for_messaging = models.ForeignKey(
    #     AIModel,
    #     on_delete=models.SET_NULL,
    #     null=True, blank=True,
    #     related_name='messaging_profiles',
    #     verbose_name='Modelo de IA para Conversa'
    # )
    # model_for_services = models.ForeignKey(
    #     AIModel,
    #     on_delete=models.SET_NULL,
    #     null=True, blank=True,
    #     related_name='services_profiles',
    #     verbose_name='Modelo de IA para Tarefas'
    # )

    class Meta:
        verbose_name = 'Perfil de Uso da IA'
        verbose_name_plural = 'Perfis de Uso da IA'
        constraints = [
            # Garante que o perfil pertença a um tenant OU a um user, mas não a ambos.
            models.CheckConstraint(
                check=(
                    Q(tenant__isnull=False, user__isnull=True) |
                    Q(tenant__isnull=True, user__isnull=False)
                ),
                name='exclusive_owner_for_usage_profile'
            ),
            # Garante que um tenant só possa ter um perfil.
            models.UniqueConstraint(
                fields=['tenant'],
                condition=Q(tenant__isnull=False),
                name='unique_tenant_usage_profile'
            ),
            # Garante que um usuário só possa ter um perfil.
            models.UniqueConstraint(
                fields=['user'],
                condition=Q(user__isnull=False),
                name='unique_user_usage_profile'
            )
        ]

    def __str__(self):
        owner = self.tenant or self.user
        return f"Perfil de Uso da IA para {owner}"
