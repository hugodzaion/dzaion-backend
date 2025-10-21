# -*- coding: utf-8 -*-
"""
Módulo de Views para o App 'entitlements'.

Contém os endpoints da API para que os Tenants possam gerenciar
suas assinaturas de módulos (Subscriptions).

Author: Dzaion
Version: 0.1.0
"""
from datetime import date
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from guards.permissions import HasTenantPermission
from tenants.models import Tenant
from .models import Subscription
from .serializers import SubscriptionSerializer, SubscriptionCreateSerializer

@extend_schema(summary="Listar e Assinar Módulos para um Tenant", tags=["Assinaturas (Entitlements)"])
class SubscriptionListCreateAPIView(generics.ListCreateAPIView):
    """
    Endpoint para listar as assinaturas de um Tenant e para
    criar uma nova assinatura (comprar um módulo).
    """
    permission_classes = [IsAuthenticated, HasTenantPermission]
    
    def get_queryset(self):
        return Subscription.objects.filter(tenant_id=self.kwargs['tenant_pk'])

    def get_serializer_class(self):
        if self.request.method == 'POST':
            self.required_permission = 'entitlements.add_subscription'
            return SubscriptionCreateSerializer
        self.required_permission = 'entitlements.view_subscription'
        return SubscriptionSerializer

    def perform_create(self, serializer):
        tenant = get_object_or_404(Tenant, pk=self.kwargs['tenant_pk'])
        plan = serializer.validated_data['plan_id']
        today = date.today()
        
        # Lógica para calcular a próxima data de cobrança
        # (simplificado, pode ser expandido com a lógica de 'period' do billing_cycle)
        next_billing = today + relativedelta(months=1)

        # Cria a Subscription com os "snapshots" de dados do plano
        subscription = Subscription.objects.create(
            tenant=tenant,
            plan=plan,
            price=plan.price, # Snapshot do preço
            billing_cycle_details={ # Snapshot do ciclo
                "period": plan.billing_cycle.period,
                "discount": plan.billing_cycle.discount_percentage
            },
            features_snapshot=plan.features, # Snapshot das features
            status=Subscription.SubscriptionStatus.ACTIVE,
            start_date=today,
            next_billing_date=next_billing
        )
        return subscription
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = self.perform_create(serializer)
        response_serializer = SubscriptionSerializer(subscription)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
