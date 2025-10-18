# -*- coding: utf-8 -*-
"""
Configuração do App 'activities'.

Author: Dzaion
Version: 1.0.0
"""
from django.apps import AppConfig


class ActivitiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'activities'
    verbose_name = 'Gestão de Atividades'

    def ready(self):
        """
        Importa os signal receivers quando a aplicação está pronta.

        Este método é a forma recomendada pelo Django para garantir que
        os módulos contendo os decoradores @receiver sejam carregados e,
        consequentemente, os sinais sejam conectados.
        """
        # A importação faz com que os receivers sejam registrados.
        import activities.receivers
