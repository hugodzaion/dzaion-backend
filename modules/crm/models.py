# -*- coding: utf-8 -*-
"""
Módulo de Modelos para o App 'crm'.

Define a entidade central de Contato, que é a representação genérica
de qualquer pessoa com a qual um Tenant se relaciona (cliente, aluno, etc.).

Author: Dzaion
Version: 0.3.0
"""
from django.db import models
from core.models import BaseModel
from locations.models import Location

def contact_photo_directory_path(instance, filename):
    """Gera o caminho para o upload da foto do contato."""
    return f'tenants/{instance.tenant_id}/contacts/{instance.id}/photo/{filename}'

class Contact(BaseModel):
    """
    Representa um Contato de um Tenant.
    Pode ser opcionalmente vinculado a um User global do sistema.
    """
    class Gender(models.TextChoices):
        MALE = 'MALE', 'Masculino'
        FEMALE = 'FEMALE', 'Feminino'
        OTHER = 'OTHER', 'Outro'

    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='crm_contacts',
        verbose_name='Inquilino'
    )
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='contact_profile',
        verbose_name='Usuário Dzaion Vinculado'
    )
    
    # --- Dados Pessoais ---
    name = models.CharField(max_length=255, verbose_name='Nome do Contato', db_index=True)
    photo = models.ImageField(
        upload_to=contact_photo_directory_path,
        null=True, blank=True,
        verbose_name='Foto'
    )
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Data de Nascimento')
    gender = models.CharField(
        max_length=6,
        choices=Gender.choices,
        null=True, blank=True,
        verbose_name='Gênero'
    )

    # --- Documentos ---
    cpf = models.CharField(max_length=11, null=True, blank=True, verbose_name='CPF')
    document_rg = models.CharField(max_length=20, null=True, blank=True, verbose_name='RG / Documento de Identidade')

    # --- Contato Principal ---
    email = models.EmailField(null=True, blank=True, verbose_name='E-mail')
    whatsapp = models.CharField(max_length=20, null=True, blank=True, verbose_name='WhatsApp')
    
    # --- Contatos Adicionais ---
    phone_1 = models.CharField(max_length=20, null=True, blank=True, verbose_name='Telefone 1')
    phone_2 = models.CharField(max_length=20, null=True, blank=True, verbose_name='Telefone 2')

    # --- Redes Sociais ---
    social_linkedin = models.URLField(null=True, blank=True, verbose_name='LinkedIn')
    social_facebook = models.URLField(null=True, blank=True, verbose_name='Facebook')
    social_instagram = models.URLField(null=True, blank=True, verbose_name='Instagram')
    social_x = models.URLField(null=True, blank=True, verbose_name='X (Twitter)')
    
    # --- Endereço ---
    street = models.CharField(max_length=255, null=True, blank=True, verbose_name='Logradouro')
    number = models.CharField(max_length=20, null=True, blank=True, verbose_name='Número')
    complement = models.CharField(max_length=100, null=True, blank=True, verbose_name='Complemento')
    neighborhood = models.CharField(max_length=100, null=True, blank=True, verbose_name='Bairro')
    postal_code = models.CharField(max_length=9, null=True, blank=True, verbose_name='CEP')
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Localidade (Cidade/Estado)'
    )
    
    # --- Dados Customizados ---
    custom_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Dados Customizados',
        help_text='Campo para dados específicos do módulo (ex: {"turma": "Sub-10"}).'
    )
    
    class Meta:
        verbose_name = 'Contato (CRM)'
        verbose_name_plural = 'Contatos (CRM)'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'email'],
                condition=models.Q(email__isnull=False, email__gt=''),
                name='unique_contact_email_per_tenant'
            ),
            models.UniqueConstraint(
                fields=['tenant', 'cpf'],
                condition=models.Q(cpf__isnull=False, cpf__gt=''),
                name='unique_contact_cpf_per_tenant'
            )
        ]

    def __str__(self):
        return self.name

