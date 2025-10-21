# -*- coding: utf-8 -*-
"""
Módulo de Serializers para o App 'finances'.

Author: Dzaion
Version: 0.3.0
"""
from rest_framework import serializers
from .models import Wallet, Transaction, TransactionType, Invoice, InvoiceItem

class WalletSummarySerializer(serializers.ModelSerializer):
    """Serializer para uma representação resumida da Wallet."""
    owner_id = serializers.SerializerMethodField()
    owner_type = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'owner_id', 'owner_type', 'owner_name']
    def get_owner_id(self, obj: Wallet): return (obj.tenant or obj.user).id
    def get_owner_type(self, obj: Wallet): return 'tenant' if obj.tenant else 'user'
    def get_owner_name(self, obj: Wallet): return (obj.tenant or obj.user).name

class TransactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = ['name', 'code', 'is_debit']

class TransactionSerializer(serializers.ModelSerializer):
    """Serializer para listar as transações (o "extrato") de uma carteira."""
    type = TransactionTypeSerializer(read_only=True)
    class Meta:
        model = Transaction
        fields = ['id', 'type', 'amount', 'status', 'processed_at', 'invoice']

class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer para os itens de uma fatura."""
    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'amount']

class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer para listar faturas."""
    class Meta:
        model = Invoice
        fields = ['id', 'status', 'amount', 'due_date', 'paid_at']

class InvoiceDetailSerializer(serializers.ModelSerializer):
    """Serializer para os detalhes completos de uma fatura, incluindo seus itens."""
    items = InvoiceItemSerializer(many=True, read_only=True)
    class Meta:
        model = Invoice
        fields = ['id', 'status', 'amount', 'due_date', 'paid_at', 'billing_details_snapshot', 'items']

