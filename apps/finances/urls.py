# -*- coding: utf-8 -*-
"""
Módulo de URLs para o App 'finances'.

Mapeia as URLs para as views correspondentes da API financeira.

Author: Dzaion
Version: 0.1.0
"""
from django.urls import path
from .views import MyWalletView, MyTransactionListView

urlpatterns = [
    # Rota para a carteira do usuário logado: GET /v1/finances/my-wallet/
    path('my-wallet/', MyWalletView.as_view(), name='my-wallet'),
    
    # Rota para o extrato do usuário logado: GET /v1/finances/my-transactions/
    path('my-transactions/', MyTransactionListView.as_view(), name='my-transactions'),
]
