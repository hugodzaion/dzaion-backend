# -*- coding: utf-8 -*-
"""
Módulo de URLs para o App 'activities'.

Mapeia as URLs para as views correspondentes.

Author: Dzaion
Version: 1.0.0
"""
from django.urls import path
from .views import UserActivityListView

urlpatterns = [
    # A rota raiz (/v1/activities/) listará as atividades do usuário.
    path('', UserActivityListView.as_view(), name='user-activity-list'),
]
