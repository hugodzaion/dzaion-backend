# -*- coding: utf-8 -*-
"""
Configuração do App 'finances'.
"""
from django.apps import AppConfig

class FinancesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finances'
    verbose_name = 'Finanças'

    def ready(self):
        """
        Importa os receivers (sinais) quando o app estiver pronto.
        Isso garante que os sinais sejam conectados na inicialização.
        """
        import finances.receivers
