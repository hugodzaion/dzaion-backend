# -*- coding: utf-8 -*-
"""
Módulo de Configuração do Django Admin para o App 'contacts'.

Este módulo customiza a forma como os modelos de contato, como
o ChannelContacts, são exibidos e gerenciados no painel de administração.

Author: Dzaion
Version: 0.1.0
"""
from django.contrib import admin
from .models import ChannelContacts

@admin.register(ChannelContacts)
class ChannelContactsAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo ChannelContacts.
    """
    list_display = ('name', 'icon')
    search_fields = ('name',)
