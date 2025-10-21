# -*- coding: utf-8 -*-
"""
Módulo de URLs para o App 'entitlements'.

Author: Dzaion
Version: 0.1.0
"""
from django.urls import path
from .views import SubscriptionListCreateAPIView

urlpatterns = [
    path('', SubscriptionListCreateAPIView.as_view(), name='subscription-list-create'),
]
