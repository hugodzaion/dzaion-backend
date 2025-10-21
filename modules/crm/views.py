# -*- coding: utf-8 -*-
"""
Módulo de Views para o App 'crm'.

Contém os endpoints da API para o gerenciamento de Contatos,
incluindo a lógica inteligente de sugestão de vínculo com Usuários.

Author: Dzaion
Version: 0.1.0
"""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from accounts.models import User
from guards.permissions import HasTenantPermission
from tenants.models import Tenant
from .models import Contact
from .serializers import ContactSerializer, ContactCreateSerializer, LinkUserToContactSerializer

@extend_schema(summary="Listar e Criar Contatos de um Tenant", tags=["CRM"])
class ContactListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, HasTenantPermission]
    required_permission = 'crm.add_contact'

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ContactCreateSerializer
        return ContactSerializer
    
    def get_queryset(self):
        return Contact.objects.filter(tenant_id=self.kwargs['tenant_pk'])

    def perform_create(self, serializer):
        tenant = get_object_or_404(Tenant, pk=self.kwargs['tenant_pk'])
        return serializer.save(tenant=tenant)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = self.perform_create(serializer)

        # --- Lógica de Sugestão de Vínculo ---
        filters = Q()
        if contact.email:
            filters |= Q(email__iexact=contact.email)
        if contact.whatsapp:
            filters |= Q(whatsapp=contact.whatsapp)
        if contact.cpf:
            filters |= Q(cpf=contact.cpf)

        suggested_user = User.objects.filter(filters).first() if filters else None

        if suggested_user:
            # Cenário B: Correspondência encontrada! Retorna 202 com a sugestão.
            response_data = {
                "status": "pending_link_confirmation",
                "message": "Encontramos um usuário Dzaion que pode corresponder a este contato. Deseja vinculá-los?",
                "contact": ContactSerializer(contact).data,
                "suggested_user": {
                    "id": suggested_user.id,
                    "name": suggested_user.name,
                }
            }
            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        
        # Cenário A: Nenhuma correspondência. Retorna 201 com o contato criado.
        return Response(ContactSerializer(contact).data, status=status.HTTP_201_CREATED)


@extend_schema(summary="Vincular um Contato a um Usuário Dzaion", tags=["CRM"])
class LinkUserToContactAPIView(views.APIView):
    permission_classes = [IsAuthenticated, HasTenantPermission]
    required_permission = 'crm.change_contact'

    def post(self, request, tenant_pk, pk):
        contact = get_object_or_404(Contact, pk=pk, tenant_id=tenant_pk)
        
        serializer = LinkUserToContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data['user_id']
        
        user_to_link = get_object_or_404(User, pk=user_id)
        
        # Realiza o vínculo
        contact.user = user_to_link
        contact.save()
        
        return Response(ContactSerializer(contact).data, status=status.HTTP_200_OK)
