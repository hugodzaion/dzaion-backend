# -*- coding: utf-8 -*-
"""
Configuração do App 'entitlements'.
"""
from django.apps import AppConfig

class EntitlementsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'entitlements'
    verbose_name = 'Direitos de Acesso (Entitlements)'

    def ready(self):
        """
        Importa os receivers (sinais) quando o app estiver pronto.
        """
        import entitlements.receivers
