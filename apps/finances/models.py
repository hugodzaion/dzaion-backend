# -*- coding: utf-8 -*-
"""
Módulo de Modelos para o App 'finances'.

Este módulo gerencia todas as entidades e processos financeiros,
incluindo carteiras (Wallets), faturas (Invoices) e o registro
imutável de movimentações (Transactions).

Author: Dzaion
Version: 0.1.0
"""
from django.conf import settings
from django.db import models
from django.db.models import Q

from core.models import BaseModel
from tenants.models import Tenant


class Wallet(BaseModel):
    """
    A "Conta Corrente" onde os créditos (saldo) são armazenados.
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='wallet',
        verbose_name='Inquilino (Proprietário)'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='wallet',
        verbose_name='Usuário (Proprietário)'
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name='Saldo'
    )

    class Meta:
        verbose_name = 'Carteira de Créditos'
        verbose_name_plural = 'Carteiras de Créditos'
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(tenant__isnull=False, user__isnull=True) |
                    Q(tenant__isnull=True, user__isnull=False)
                ),
                name='exclusive_owner_for_wallet'
            )
        ]

    def __str__(self):
        owner = self.tenant or self.user
        return f"Carteira de {owner}"


class TransactionType(BaseModel):
    """
    Modelo auxiliar para categorizar cada transação financeira.
    """
    name = models.CharField(max_length=100, verbose_name='Nome Legível')
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código Interno',
        help_text='Ex: INVOICE_PAYMENT, IA_USAGE_DEBIT'
    )
    is_debit = models.BooleanField(
        default=True,
        verbose_name='É um Débito?',
        help_text='Define se a operação representa uma saída (débito) de fundos.'
    )

    class Meta:
        verbose_name = 'Tipo de Transação'
        verbose_name_plural = 'Tipos de Transações'
        ordering = ['name']

    def __str__(self):
        return self.name


class Invoice(BaseModel):
    """
    A cobrança formal enviada a um Tenant, consolidando um ou mais itens a serem pagos.
    """
    class InvoiceStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Rascunho'
        OPEN = 'OPEN', 'Aberta'
        PAID = 'PAID', 'Paga'
        CANCELED = 'CANCELED', 'Cancelada'
        UNCOLLECTIBLE = 'UNCOLLECTIBLE', 'Inadimplente'

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name='Devedor (Inquilino)'
    )
    status = models.CharField(
        max_length=15,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        verbose_name='Status da Fatura'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor Total'
    )
    due_date = models.DateField(verbose_name='Data de Vencimento')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='Data de Pagamento')
    billing_details_snapshot = models.JSONField(
        null=True, blank=True,
        verbose_name='Dados de Faturamento (Snapshot)',
        help_text='Snapshot dos dados do Tenant no momento da emissão.'
    )

    class Meta:
        verbose_name = 'Fatura'
        verbose_name_plural = 'Faturas'
        ordering = ['-due_date']

    def __str__(self):
        return f"Fatura #{self.id.hex[:8]} para {self.tenant.name}"


class Transaction(BaseModel):
    """
    O registro imutável de cada movimentação financeira (o "extrato").
    """
    class TransactionStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendente'
        COMPLETED = 'COMPLETED', 'Concluída'
        FAILED = 'FAILED', 'Falhou'

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name='Carteira'
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='transactions',
        verbose_name='Fatura Relacionada'
    )
    type = models.ForeignKey(
        TransactionType,
        on_delete=models.PROTECT,
        verbose_name='Tipo da Transação'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor',
        help_text='Valores positivos para créditos (entradas) e negativos para débitos (saídas).'
    )
    status = models.CharField(
        max_length=15,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
        verbose_name='Status da Transação'
    )
    gateway_transaction_id = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name='ID da Transação no Gateway'
    )
    gateway_response = models.JSONField(
        null=True, blank=True,
        verbose_name='Resposta do Gateway'
    )
    processed_at = models.DateTimeField(
        verbose_name='Processada em'
    )

    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        ordering = ['-processed_at']

    def __str__(self):
        return f"Transação de {self.amount} para {self.wallet}"


class InvoiceItem(BaseModel):
    """
    Representa uma única linha em uma Invoice.
    """
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Fatura'
    )
    description = models.CharField(
        max_length=255,
        verbose_name='Descrição do Item'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor do Item'
    )
    source_id = models.UUIDField(
        verbose_name='ID da Origem da Cobrança',
        help_text='O ID do objeto que gerou esta cobrança (ex: uma Assinatura).'
    )
    source_type = models.CharField(
        max_length=100,
        verbose_name='Tipo da Origem',
        help_text='Identifica o tipo do objeto de origem (ex: "subscription").'
    )

    class Meta:
        verbose_name = 'Item da Fatura'
        verbose_name_plural = 'Itens da Fatura'
        ordering = ['created_at']

    def __str__(self):
        return self.description
