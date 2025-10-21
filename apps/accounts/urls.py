# -*- coding: utf-8 -*-
"""
Módulo de URLs para o App 'accounts'.

Mapeia as URLs para as views correspondentes de autenticação
e gerenciamento de contas.

Author: Dzaion
Version: 0.2.0
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    MeView,
    RegisterView,
    ChangePasswordView
)

urlpatterns = [
    # Rotas de Autenticação
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Rota de Registro
    path('register/', RegisterView.as_view(), name='user-register'),
    
    # Rotas de Gerenciamento de Perfil ('/me/')
    path('me/', MeView.as_view(), name='user-me'),
    
    # DZAION-FIX: Adicionando a rota que estava faltando para alteração de senha.
    path('me/change-password/', ChangePasswordView.as_view(), name='user-change-password'),
]
