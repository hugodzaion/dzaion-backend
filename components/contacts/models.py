# -*- coding: utf-8 -*-
"""
Módulo de Modelos para o App 'contacts'.

Define os modelos para componentes de contato reutilizáveis,
como os canais de contato disponíveis no sistema.

Author: Dzaion
Version: 0.1.0
"""
from django.db import models
from core.models import BaseModel

class ChannelContacts(BaseModel):
    """
    Representa um tipo de canal de contato disponível no sistema.
    Ex: Telefone, WhatsApp, Instagram.
    """
    name = models.CharField('Nome do Canal', max_length=50, unique=True)
    icon = models.CharField('Ícone', max_length=50, blank=True,
                            help_text="Classe do ícone para o frontend (ex: 'fab fa-whatsapp').")

    class Meta:
        verbose_name = 'Canal de Contato'
        verbose_name_plural = 'Canais de Contato'
        ordering = ['name']

    def __str__(self):
        return self.name
