# -*- coding: utf-8 -*-
"""
Módulo de URLs para o App 'crm'.

Author: Dzaion
Version: 0.1.0
"""
from django.urls import path
from .views import ContactListCreateAPIView, LinkUserToContactAPIView

urlpatterns = [
    path('', ContactListCreateAPIView.as_view(), name='contact-list-create'),
    path('<uuid:pk>/link-user/', LinkUserToContactAPIView.as_view(), name='contact-link-user'),
]
