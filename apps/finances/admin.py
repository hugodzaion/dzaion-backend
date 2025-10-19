# -*- coding: utf-8 -*-
"""
Módulo de Configuração do Django Admin para o App 'finances'.

Este módulo customiza a forma como os modelos financeiros são exibidos
e gerenciados no painel de administração, com foco em auditoria e
segurança (somente leitura para dados imutáveis).

Author: Dzaion
Version: 0.1.0
"""
from django.contrib import admin
from .models import Wallet, TransactionType, Transaction, Invoice, InvoiceItem

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo Wallet.
    """
    list_display = ('id', 'owner', 'balance')
    search_fields = ('user__email', 'tenant__name')
    # O saldo só pode ser alterado via transações, nunca manualmente.
    readonly_fields = ('balance',)
    
    def owner(self, obj):
        return obj.tenant or obj.user
    owner.short_description = 'Proprietário'

@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo TransactionType.
    """
    list_display = ('name', 'code', 'is_debit')
    list_filter = ('is_debit',)

class TransactionInline(admin.TabularInline):
    """
    Permite visualizar as transações diretamente na página da Fatura ou Carteira.
    Configurado como somente leitura.
    """
    model = Transaction
    extra = 0
    readonly_fields = [field.name for field in Transaction._meta.fields]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo Transaction.
    Totalmente somente leitura, pois é um registro imutável.
    """
    list_display = ('id', 'wallet', 'type', 'amount', 'status', 'processed_at')
    list_filter = ('status', 'type')
    search_fields = ('wallet__user__email', 'wallet__tenant__name', 'gateway_transaction_id')
    
    # Transações são registros imutáveis e nunca devem ser alteradas.
    readonly_fields = [field.name for field in Transaction._meta.fields]

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Permite a exclusão apenas por superusuários para correções emergenciais.
        return request.user.is_superuser

class InvoiceItemInline(admin.TabularInline):
    """
    Permite a edição dos itens diretamente na página da Fatura.
    """
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo Invoice.
    """
    inlines = [InvoiceItemInline]
    list_display = ('id', 'tenant', 'status', 'amount', 'due_date', 'paid_at')
    list_filter = ('status', 'due_date')
    search_fields = ('tenant__name', 'id')
    readonly_fields = ('paid_at',)
