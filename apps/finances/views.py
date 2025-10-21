# -*- coding: utf-8 -*-
"""
Módulo de Views (Controladores) para o App 'finances'.

Author: Dzaion
Version: 0.3.0
"""
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from accounts.permissions import IsActiveUser
from guards.permissions import HasTenantPermission
from tenants.models import Tenant
from .models import Transaction, Invoice
from .serializers import (
    WalletSummarySerializer, TransactionSerializer, 
    InvoiceSerializer, InvoiceDetailSerializer
)
from .services import FinanceService
from .exceptions import FinanceError

# --- Views para Finanças Pessoais ---

@extend_schema(summary="Obter a Carteira do Usuário Logado", tags=["Finanças Pessoais"])
class MyWalletView(generics.RetrieveAPIView):
    serializer_class = WalletSummarySerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    def get_object(self): return self.request.user.wallet.first()

@extend_schema(summary="Listar Transações do Usuário (Extrato)", tags=["Finanças Pessoais"])
class MyTransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    def get_queryset(self):
        user_wallet = self.request.user.wallet.first()
        return Transaction.objects.filter(wallet=user_wallet).order_by('-processed_at') if user_wallet else Transaction.objects.none()

# --- Views para Finanças da Empresa (Tenant) ---

@extend_schema(summary="Obter a Carteira de um Tenant", tags=["Finanças do Tenant"])
class TenantWalletView(generics.RetrieveAPIView):
    serializer_class = WalletSummarySerializer
    permission_classes = [IsAuthenticated, IsActiveUser, HasTenantPermission]
    required_permission = 'finances.view_wallet'
    def get_object(self):
        tenant = get_object_or_404(Tenant, pk=self.kwargs['tenant_pk'])
        return tenant.wallet.first()

@extend_schema(summary="Listar Transações de um Tenant (Extrato)", tags=["Finanças do Tenant"])
class TenantTransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, HasTenantPermission]
    required_permission = 'finances.view_transaction'
    def get_queryset(self):
        tenant = get_object_or_404(Tenant, pk=self.kwargs['tenant_pk'])
        tenant_wallet = tenant.wallet.first()
        return Transaction.objects.filter(wallet=tenant_wallet).order_by('-processed_at') if tenant_wallet else Transaction.objects.none()

@extend_schema(summary="Listar Faturas de um Tenant", tags=["Finanças do Tenant"])
class TenantInvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, HasTenantPermission]
    required_permission = 'finances.view_invoice'
    def get_queryset(self):
        return Invoice.objects.filter(tenant_id=self.kwargs['tenant_pk']).order_by('-due_date')

@extend_schema(summary="Ver Detalhes de uma Fatura", tags=["Finanças do Tenant"])
class TenantInvoiceRetrieveView(generics.RetrieveAPIView):
    serializer_class = InvoiceDetailSerializer
    permission_classes = [IsAuthenticated, IsActiveUser, HasTenantPermission]
    required_permission = 'finances.view_invoice'
    def get_queryset(self):
        return Invoice.objects.filter(tenant_id=self.kwargs['tenant_pk'])

@extend_schema(summary="Pagar uma Fatura com Saldo da Carteira", tags=["Finanças do Tenant"])
class TenantInvoicePayView(views.APIView):
    permission_classes = [IsAuthenticated, IsActiveUser, HasTenantPermission]
    required_permission = 'finances.add_transaction' # Pagar é criar uma transação de débito

    def post(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, pk=self.kwargs['pk'], tenant_id=self.kwargs['tenant_pk'])
        try:
            transaction = FinanceService.pay_invoice_with_wallet(invoice)
            return Response(TransactionSerializer(transaction).data, status=status.HTTP_200_OK)
        except FinanceError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

