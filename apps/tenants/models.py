# -*- coding: utf-8 -*-
"""
Módulo de Modelos para o App 'tenants'.

Author: Dzaion
Version: 0.8.0
"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.text import slugify

from core.models import BaseModel
from locations.models import Location
from contacts.models import ChannelContacts

def tenant_logo_directory_path(instance, filename):
    return f'tenants/{instance.id}/logo/{filename}'

class Tenant(BaseModel):
    """
    Representa uma entidade de negócio (Inquilino), que pode ser uma
    Matriz ou uma Filial.
    """
    class TenantType(models.TextChoices):
        PF = 'PF', 'Pessoa Física'
        PJ = 'PJ', 'Pessoa Jurídica'

    class TenantStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Ativo'
        INACTIVE = 'INACTIVE', 'Inativo'
        SUSPENDED = 'SUSPENDED', 'Suspenso'

    parent = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='branches',
        verbose_name='Matriz'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name='Proprietário Legal',
        related_name='owned_tenants'
    )
    financial_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name='Contato Financeiro',
        related_name='financial_tenants'
    )
    legal_name = models.CharField(
        max_length=255,
        verbose_name='Razão Social / Nome Completo'
    )
    name = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name='Nome Fantasia'
    )
    slug = models.SlugField(max_length=255, unique=True, verbose_name='Identificador de URL')
    document = models.CharField(max_length=14, unique=True, verbose_name='CPF/CNPJ')
    type = models.CharField(max_length=2, choices=TenantType.choices, verbose_name='Tipo de Entidade')
    logo = models.FileField(upload_to=tenant_logo_directory_path, null=True, blank=True, verbose_name='Logomarca')
    contact_email = models.EmailField(null=True, blank=True, verbose_name='E-mail Principal')
    billing_day = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        verbose_name='Melhor Dia para Pagamento'
    )
    status = models.CharField(max_length=10, choices=TenantStatus.choices, default=TenantStatus.ACTIVE, verbose_name='Status')
    street = models.CharField(max_length=255, verbose_name='Logradouro')
    number = models.CharField(max_length=20, verbose_name='Número')
    complement = models.CharField(max_length=100, null=True, blank=True, verbose_name='Complemento')
    neighborhood = models.CharField(max_length=100, verbose_name='Bairro')
    postal_code = models.CharField(max_length=9, verbose_name='CEP')
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        verbose_name='Localidade (Cidade/Estado)'
    )

    class Meta:
        verbose_name = 'Inquilino (Tenant)'
        verbose_name_plural = 'Inquilinos (Tenants)'
        ordering = ['name']

    def __str__(self):
        return self.name or self.legal_name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.legal_name
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.financial_contact_id:
            self.financial_contact = self.owner
        super().save(*args, **kwargs)

class TenantLinkRequest(BaseModel):
    class LinkStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendente'
        APPROVED = 'APPROVED', 'Aprovado'
        REJECTED = 'REJECTED', 'Rejeitado'

    requesting_tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='sent_link_requests',
        verbose_name='Inquilino Solicitante (Filial)'
    )
    parent_document = models.CharField(
        max_length=14,
        verbose_name='CNPJ da Matriz'
    )
    status = models.CharField(
        max_length=10,
        choices=LinkStatus.choices,
        default=LinkStatus.PENDING,
        verbose_name='Status da Solicitação'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Aprovado por'
    )
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='Processado em')

    class Meta:
        verbose_name = 'Solicitação de Vínculo de Matriz'
        verbose_name_plural = 'Solicitações de Vínculo de Matriz'
        ordering = ['-created_at']

    def __str__(self):
        return f"Solicitação de {self.requesting_tenant.name} para se vincular a {self.parent_document}"

class TenantContact(BaseModel):
    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE,
        related_name='company_contacts',
        verbose_name='Inquilino'
    )
    channel = models.ForeignKey(
        ChannelContacts,
        on_delete=models.PROTECT,
        verbose_name='Canal de Contato'
    )
    value = models.CharField(max_length=255, verbose_name='Contato (Valor)')

    class Meta:
        verbose_name = 'Contato da Empresa'
        verbose_name_plural = 'Contatos da Empresa'
        ordering = ['channel__name']

    def __str__(self):
        return f"{self.channel.name}: {self.value}"

class TenantMembership(BaseModel):
    class MembershipStatus(models.TextChoices):
        INVITED = 'INVITED', 'Convidado'
        ACTIVE = 'ACTIVE', 'Ativo'
        INACTIVE = 'INACTIVE', 'Inativo'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name='Usuário (Membro)'
    )
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='Inquilino'
    )
    role = models.ForeignKey(
        'guards.Role',
        on_delete=models.PROTECT,
        verbose_name='Papel (Cargo)'
    )
    status = models.CharField(
        max_length=10,
        choices=MembershipStatus.choices,
        default=MembershipStatus.INVITED,
        verbose_name='Status do Vínculo'
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sent_invitations',
        verbose_name='Convidado por'
    )
    joined_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Data de Ativação'
    )

    class Meta:
        verbose_name = 'Vínculo de Membro'
        verbose_name_plural = 'Vínculos de Membros'
        ordering = ['tenant__name', 'user__name']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'tenant'],
                name='unique_user_per_tenant'
            )
        ]

    def __str__(self):
        return f"{self.user.name} em {self.tenant.name} como {self.role.name}"

