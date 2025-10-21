# -*- coding: utf-8 -*-
"""
Módulo de URLs para o App 'finances'.

Author: Dzaion
Version: 0.2.0
"""
from django.urls import path
from .views import (
    MyWalletView, MyTransactionListView,
    TenantWalletView, TenantTransactionListView,
    TenantInvoiceListView, TenantInvoiceRetrieveView, TenantInvoicePayView
)

# URLs para finanças pessoais do usuário logado
personal_patterns = [
    path('my-wallet/', MyWalletView.as_view(), name='my-wallet'),
    path('my-transactions/', MyTransactionListView.as_view(), name='my-transactions'),
]

# URLs para finanças de um Tenant específico (aninhadas)
tenant_patterns = [
    path('wallet/', TenantWalletView.as_view(), name='tenant-wallet'),
    path('transactions/', TenantTransactionListView.as_view(), name='tenant-transactions'),
    path('invoices/', TenantInvoiceListView.as_view(), name='tenant-invoices'),
    path('invoices/<uuid:pk>/', TenantInvoiceRetrieveView.as_view(), name='tenant-invoice-detail'),
    path('invoices/<uuid:pk>/pay/', TenantInvoicePayView.as_view(), name='tenant-invoice-pay'),
]

urlpatterns = personal_patterns

