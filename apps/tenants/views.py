# -*- coding: utf-8 -*-
"""
Módulo de Views (Controladores) para o App 'tenants'.

Author: Dzaion
Version: 0.7.0
"""
from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from accounts.models import User
from accounts.permissions import IsActiveUser
from guards.permissions import HasTenantPermission
from .models import Tenant, TenantContact, TenantMembership, TenantLinkRequest
from .serializers import (
    TenantSerializer, TenantCreateSerializer, TenantUpdateSerializer,
    TenantContactSerializer, TenantContactCreateUpdateSerializer,
    TenantMembershipSerializer, TenantMembershipInviteSerializer,
    TenantLinkRequestSerializer
)
from .services import TenantService

@extend_schema(summary="Listar e Criar Inquilinos (Tenants)", tags=["Tenants"])
class TenantListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    
    def get_serializer_class(self):
        return TenantCreateSerializer if self.request.method == 'POST' else TenantSerializer

    def get_queryset(self):
        return Tenant.objects.filter(members__user=self.request.user).distinct()

    def perform_create(self, serializer):
        return TenantService.create_tenant(owner=self.request.user, **serializer.validated_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant = self.perform_create(serializer)
        response_serializer = TenantSerializer(tenant, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(response_serializer.data))

@extend_schema(summary="Ver, Atualizar e Deletar um Tenant", tags=["Tenants"])
class TenantRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser, HasTenantPermission]
    
    def get_serializer_class(self):
        return TenantUpdateSerializer if self.request.method in ['PUT', 'PATCH'] else TenantSerializer

    def get_queryset(self):
        return Tenant.objects.filter(members__user=self.request.user)

    def get_required_permission(self):
        if self.request.method == 'DELETE':
            return 'tenants.delete_tenant'
        return 'tenants.change_tenant'

@extend_schema(summary="Listar e Adicionar Contatos de uma Empresa", tags=["Tenants"])
class TenantContactListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser, HasTenantPermission]
    required_permission = 'tenants.add_tenantcontact'

    def get_serializer_class(self):
        return TenantContactCreateUpdateSerializer if self.request.method == 'POST' else TenantContactSerializer

    def get_queryset(self):
        return TenantContact.objects.filter(tenant_id=self.kwargs['tenant_pk'])

    def perform_create(self, serializer):
        tenant = get_object_or_404(Tenant, pk=self.kwargs['tenant_pk'])
        serializer.save(tenant=tenant)

@extend_schema(summary="Ver, Atualizar e Deletar um Contato de Empresa", tags=["Tenants"])
class TenantContactRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser, HasTenantPermission]
    required_permission = 'tenants.change_tenantcontact'
    
    def get_serializer_class(self):
        return TenantContactCreateUpdateSerializer if self.request.method in ['PUT', 'PATCH'] else TenantContactSerializer

    def get_queryset(self):
        return TenantContact.objects.filter(tenant_id=self.kwargs['tenant_pk'])

@extend_schema(summary="Listar Membros de um Tenant", tags=["Tenants"])
class TenantMembershipListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser, HasTenantPermission]
    required_permission = 'tenants.view_tenantmembership'
    serializer_class = TenantMembershipSerializer

    def get_queryset(self):
        return TenantMembership.objects.filter(tenant_id=self.kwargs['tenant_pk'])

@extend_schema(summary="Convidar Novo Membro para um Tenant", tags=["Tenants"])
class TenantMembershipInviteAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser, HasTenantPermission]
    required_permission = 'tenants.add_tenantmembership'
    serializer_class = TenantMembershipInviteSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant = get_object_or_404(Tenant, pk=self.kwargs['tenant_pk'])
        email = serializer.validated_data['email']
        role = serializer.validated_data['role_id']
        
        user_to_invite, created = User.objects.get_or_create(email=email, defaults={'name': 'Usuário Convidado'})
        
        membership, created = TenantMembership.objects.get_or_create(
            user=user_to_invite,
            tenant=tenant,
            defaults={'role': role, 'invited_by': request.user}
        )
        
        if not created:
            return Response({"error": "Este usuário já é membro ou foi convidado."}, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Disparar e-mail/notificação de convite aqui
        
        return Response(TenantMembershipSerializer(membership).data, status=status.HTTP_201_CREATED)

@extend_schema(summary="Atualizar Papel ou Remover um Membro", tags=["Tenants"])
class TenantMembershipUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser, HasTenantPermission]
    serializer_class = TenantMembershipSerializer

    def get_queryset(self):
        return TenantMembership.objects.filter(tenant_id=self.kwargs['tenant_pk'])
    
    def get_required_permission(self):
        if self.request.method == 'DELETE':
            return 'tenants.delete_tenantmembership'
        return 'tenants.change_tenantmembership'

@extend_schema(summary="Criar Solicitação de Vínculo com Matriz", tags=["Tenants"])
class TenantLinkRequestCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser, HasTenantPermission]
    required_permission = 'tenants.add_tenantlinkrequest'
    serializer_class = TenantLinkRequestSerializer

    def perform_create(self, serializer):
        tenant = get_object_or_404(Tenant, pk=self.kwargs['tenant_pk'])
        serializer.save(requesting_tenant=tenant)

