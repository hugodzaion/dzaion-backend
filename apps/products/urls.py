# -*- coding: utf-8 -*-
"""
Módulo de URLs para o App 'products'.

Author: Dzaion
Version: 0.2.0
"""
from django.urls import path
from .views import (
    ProductListCreateAPIView, ProductRetrieveUpdateDestroyAPIView,
    ProductPlanListCreateAPIView, ProductPlanRetrieveUpdateDestroyAPIView,
    ProductTypeListCreateAPIView, ProductTypeRetrieveUpdateDestroyAPIView,
    BillingCycleListCreateAPIView, BillingCycleRetrieveUpdateDestroyAPIView
)

urlpatterns = [
    # DZAION-FIX: Adicionando as rotas para os endpoints de apoio.
    # Rotas para Tipos de Produto
    path('types/', ProductTypeListCreateAPIView.as_view(), name='type-list-create'),
    path('types/<uuid:pk>/', ProductTypeRetrieveUpdateDestroyAPIView.as_view(), name='type-detail'),

    # Rotas para Ciclos de Faturamento
    path('billing-cycles/', BillingCycleListCreateAPIView.as_view(), name='cycle-list-create'),
    path('billing-cycles/<uuid:pk>/', BillingCycleRetrieveUpdateDestroyAPIView.as_view(), name='cycle-detail'),

    # Rotas para Produtos (Módulos)
    path('modules/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('modules/<uuid:pk>/', ProductRetrieveUpdateDestroyAPIView.as_view(), name='product-detail'),

    # Rotas para Planos
    path('plans/', ProductPlanListCreateAPIView.as_view(), name='plan-list-create'),
    path('plans/<uuid:pk>/', ProductPlanRetrieveUpdateDestroyAPIView.as_view(), name='plan-detail'),
]

