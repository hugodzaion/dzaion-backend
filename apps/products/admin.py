# -*- coding: utf-8 -*-
"""
Módulo de Configuração do Django Admin para o App 'products'.

Este módulo customiza a forma como os modelos do catálogo de produtos
são exibidos e gerenciados no painel de administração do Django.

Author: Dzaion
Version: 0.2.0
"""
from django.contrib import admin
from .models import ProductType, Product, BillingCycle, ProductPlan, ProductImage

class ProductImageInline(admin.TabularInline):
    """
    Permite a edição da galeria de imagens diretamente na página do Produto.
    """
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'order', 'is_main', 'code')

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    """Admin para o modelo ProductType."""
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin para o modelo Product (Módulo)."""
    inlines = [ProductImageInline]
    list_display = ('name', 'slug', 'product_type', 'status')
    list_filter = ('status', 'product_type')
    search_fields = ('name', 'slug')
    
    filter_horizontal = ('suggested_modules', 'granted_permissions')
    
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BillingCycle)
class BillingCycleAdmin(admin.ModelAdmin):
    """Admin para o modelo BillingCycle."""
    list_display = ('name', 'period', 'discount_percentage')
    list_filter = ('period',)

@admin.register(ProductPlan)
class ProductPlanAdmin(admin.ModelAdmin):
    """Admin para o modelo ProductPlan."""
    list_display = ('name', 'product', 'price', 'billing_cycle', 'status')
    list_filter = ('status', 'product', 'billing_cycle')
    search_fields = ('name', 'product__name')
    raw_id_fields = ('product', 'billing_cycle')

