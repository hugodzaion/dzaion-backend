# -*- coding: utf-8 -*-
"""
Módulo de Configuração do Django Admin para o App 'tenants'.

Author: Dzaion
Version: 0.3.0
"""
from django.contrib import admin
from .models import Tenant, TenantContact, TenantMembership, TenantLinkRequest

class TenantContactInline(admin.TabularInline):
    """
    Permite a edição de contatos diretamente na página do Tenant.
    """
    model = TenantContact
    extra = 1

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo Tenant.
    """
    inlines = [TenantContactInline]
    list_display = ('name', 'owner', 'parent', 'type', 'status', 'document')
    list_filter = ('type', 'status')
    search_fields = ('name', 'legal_name', 'document', 'owner__name')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('owner', 'financial_contact', 'parent', 'location')
    
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'logo')}),
        ('Propriedade e Vínculo', {'fields': ('owner', 'parent', 'financial_contact')}),
        ('Dados Fiscais e de Faturamento', {'fields': ('legal_name', 'document', 'type', 'billing_day')}),
        ('Endereço', {'fields': ('street', 'number', 'complement', 'neighborhood', 'postal_code', 'location')}),
        ('Contato e Status', {'fields': ('contact_email', 'status')}),
    )

@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant', 'role', 'status')
    list_filter = ('status', 'tenant', 'role')
    search_fields = ('user__name', 'user__email', 'tenant__name')
    raw_id_fields = ('user', 'tenant', 'role', 'invited_by')

@admin.register(TenantContact)
class TenantContactAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'channel', 'value')
    search_fields = ('tenant__name', 'value')
    raw_id_fields = ('tenant',)

@admin.register(TenantLinkRequest)
class TenantLinkRequestAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo TenantLinkRequest.
    """
    list_display = ('requesting_tenant', 'parent_document', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('requesting_tenant__name', 'parent_document')
    readonly_fields = ('created_at', 'processed_at', 'approved_by')
    raw_id_fields = ('requesting_tenant',)

