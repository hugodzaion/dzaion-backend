# -*- coding: utf-8 -*-
"""
Módulo de Modelos para o App 'guards'.

Author: Dzaion
Version: 0.3.0
"""
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import Permission

from core.models import BaseModel
# DZAION-FIX: Removidas as importações diretas para quebrar o ciclo de importação.
# from dzaion.models import DzaionAction
# from tenants.models import Tenant


class Role(BaseModel):
    """
    Representa um Papel (Role) no sistema, que é um conjunto de permissões.
    """
    name = models.CharField(
        verbose_name='Nome do Papel',
        max_length=100,
        help_text='O nome legível para o papel (ex: "Administrador", "Membro").'
    )
    # DZAION-FIX: Usando referência em string.
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Inquilino (Tenant)',
        help_text='O Tenant ao qual este papel pertence. Se nulo, é um papel global.'
    )
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name='Permissões do Sistema',
        help_text='Permissões do Django que este papel concede.'
    )
    # DZAION-FIX: Usando referência em string.
    dzaion_actions = models.ManyToManyField(
        'dzaion.DzaionAction',
        blank=True,
        verbose_name='Ações da IA',
        help_text='Ações específicas da Dzaion IA que este papel pode executar.'
    )
    is_admin_role = models.BooleanField(
        default=False,
        verbose_name='É um Papel de Administrador?',
        help_text='Se marcado, concede acesso administrativo total no contexto do seu Tenant.'
    )

    class Meta:
        verbose_name = 'Papel (Role)'
        verbose_name_plural = 'Papéis (Roles)'
        ordering = ['tenant__name', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'name'],
                name='unique_tenant_role_name'
            ),
            models.UniqueConstraint(
                fields=['name'],
                condition=Q(tenant__isnull=True),
                name='unique_global_role_name'
            )
        ]

    def __str__(self):
        if self.tenant:
            return f"{self.name} ({self.tenant.name})"
        return f"{self.name} (Global)"

