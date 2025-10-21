# -*- coding: utf-8 -*-
"""
Módulo de URLs para o App 'tenants'.

Author: Dzaion
Version: 0.7.0
"""
from django.urls import path
from .views import (
    TenantListCreateAPIView,
    TenantRetrieveUpdateDestroyAPIView,
    TenantContactListCreateAPIView,
    TenantContactRetrieveUpdateDestroyAPIView,
    TenantMembershipListAPIView,
    TenantMembershipInviteAPIView,
    TenantMembershipUpdateDestroyAPIView,
    TenantLinkRequestCreateAPIView,
)
# DZAION-GUARDS: Importando a view de listagem de papéis.
from guards.views import TenantRoleListView

urlpatterns = [
    # Rotas para Tenants
    path('', TenantListCreateAPIView.as_view(), name='tenant-list-create'),
    path('<uuid:pk>/', TenantRetrieveUpdateDestroyAPIView.as_view(), name='tenant-detail'),

    # Rotas para Contatos da Empresa
    path('<uuid:tenant_pk>/company-contacts/', TenantContactListCreateAPIView.as_view(), name='tenant-contact-list-create'),
    path('<uuid:tenant_pk>/company-contacts/<uuid:pk>/', TenantContactRetrieveUpdateDestroyAPIView.as_view(), name='tenant-contact-detail'),

    # Rotas para Membros do Tenant
    path('<uuid:tenant_pk>/members/', TenantMembershipListAPIView.as_view(), name='tenant-member-list'),
    path('<uuid:tenant_pk>/members/invite/', TenantMembershipInviteAPIView.as_view(), name='tenant-member-invite'),
    path('<uuid:tenant_pk>/members/<uuid:pk>/', TenantMembershipUpdateDestroyAPIView.as_view(), name='tenant-member-detail'),
    
    # Rota para Vínculo Matriz-Filial
    path('<uuid:tenant_pk>/link-requests/', TenantLinkRequestCreateAPIView.as_view(), name='tenant-link-request-create'),
    
    # DZAION-GUARDS: Rota para listar os papéis de um Tenant.
    path('<uuid:tenant_pk>/roles/', TenantRoleListView.as_view(), name='tenant-role-list'),
]

