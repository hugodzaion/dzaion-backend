# -*- coding: utf-8 -*-
"""
Módulo de Serializers para o App 'products'.

Author: Dzaion
Version: 0.3.0
"""
from rest_framework import serializers
from .models import Product, ProductPlan, ProductType, BillingCycle, ProductImage

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'

class BillingCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingCycle
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'order', 'is_main', 'code']

class ProductPlanSerializer(serializers.ModelSerializer):
    """Serializer para leitura de Planos de Produtos."""
    product = serializers.StringRelatedField()
    billing_cycle = serializers.StringRelatedField()
    class Meta:
        model = ProductPlan
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    """Serializer para leitura de Produtos (Módulos), incluindo seus planos."""
    product_type = serializers.StringRelatedField()
    images = ProductImageSerializer(many=True, read_only=True)
    # DZAION-PURCHASE: Aninhando os planos disponíveis dentro do produto.
    plans = ProductPlanSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para escrita (criação/atualização) de Produtos."""
    class Meta:
        model = Product
        fields = [
            'product_type', 'name', 'slug', 'description', 
            'icon', 'status', 'suggested_modules', 'granted_permissions'
        ]

class ProductPlanCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para escrita (criação/atualização) de Planos."""
    class Meta:
        model = ProductPlan
        fields = '__all__'

