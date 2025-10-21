# -*- coding: utf-8 -*-
"""
Módulo de Views para o App 'products'.

Contém os endpoints da API para o gerenciamento do catálogo de
Produtos (Módulos), Planos e para a funcionalidade de sugestão de módulos.

Author: Dzaion
Version: 0.2.0
"""
from django.shortcuts import get_object_or_404
from rest_framework import generics
from drf_spectacular.utils import extend_schema

from tenants.models import Tenant
from entitlements.models import Subscription
from .models import Product, ProductPlan, ProductType, BillingCycle
from .serializers import (
    ProductSerializer, ProductCreateUpdateSerializer,
    ProductPlanSerializer, ProductPlanCreateUpdateSerializer,
    ProductTypeSerializer, BillingCycleSerializer
)
from .permissions import IsAdminOrSuperuser

# --- Views para Entidades de Apoio ---

@extend_schema(tags=["Produtos (Admin)"])
class ProductTypeListCreateAPIView(generics.ListCreateAPIView):
    """Endpoint para listar e criar Tipos de Produto."""
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    permission_classes = [IsAdminOrSuperuser]

@extend_schema(tags=["Produtos (Admin)"])
class ProductTypeRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Endpoint para ver, atualizar e deletar um Tipo de Produto."""
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    permission_classes = [IsAdminOrSuperuser]

@extend_schema(tags=["Produtos (Admin)"])
class BillingCycleListCreateAPIView(generics.ListCreateAPIView):
    """Endpoint para listar e criar Ciclos de Faturamento."""
    queryset = BillingCycle.objects.all()
    serializer_class = BillingCycleSerializer
    permission_classes = [IsAdminOrSuperuser]

@extend_schema(tags=["Produtos (Admin)"])
class BillingCycleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Endpoint para ver, atualizar e deletar um Ciclo de Faturamento."""
    queryset = BillingCycle.objects.all()
    serializer_class = BillingCycleSerializer
    permission_classes = [IsAdminOrSuperuser]

# --- Views para Administração do Catálogo ---

@extend_schema(tags=["Produtos (Admin)"])
class ProductListCreateAPIView(generics.ListCreateAPIView):
    """Endpoint para listar e criar Produtos (Módulos)."""
    queryset = Product.objects.all()
    permission_classes = [IsAdminOrSuperuser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateUpdateSerializer
        return ProductSerializer

@extend_schema(tags=["Produtos (Admin)"])
class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Endpoint para ver, atualizar e deletar um Produto."""
    queryset = Product.objects.all()
    permission_classes = [IsAdminOrSuperuser]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductCreateUpdateSerializer
        return ProductSerializer

@extend_schema(tags=["Produtos (Admin)"])
class ProductPlanListCreateAPIView(generics.ListCreateAPIView):
    """Endpoint para listar e criar Planos."""
    queryset = ProductPlan.objects.all()
    permission_classes = [IsAdminOrSuperuser]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductPlanCreateUpdateSerializer
        return ProductPlanSerializer

@extend_schema(tags=["Produtos (Admin)"])
class ProductPlanRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Endpoint para ver, atualizar e deletar um Plano."""
    queryset = ProductPlan.objects.all()
    permission_classes = [IsAdminOrSuperuser]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductPlanCreateUpdateSerializer
        return ProductPlanSerializer

# --- View para a Funcionalidade de Sugestão de Módulos ---

@extend_schema(
    summary="Listar Módulos Sugeridos para um Tenant",
    description="Retorna uma lista de módulos que o Tenant ainda não assina, com base nos módulos que ele já possui.",
    tags=["Tenants"]
)
class ModuleSuggestionListView(generics.ListAPIView):
    """
    Endpoint que implementa a lógica de cross-selling de módulos.
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        tenant_pk = self.kwargs.get('tenant_pk')
        tenant = get_object_or_404(Tenant, pk=tenant_pk)

        current_product_ids = Subscription.objects.filter(
            tenant=tenant, status__in=['ACTIVE', 'TRIAL']
        ).values_list('plan__product_id', flat=True)

        current_products = Product.objects.filter(id__in=current_product_ids)

        suggested_module_ids = current_products.values_list('suggested_modules', flat=True)

        suggested_modules = Product.objects.filter(
            id__in=suggested_module_ids
        ).exclude(
            id__in=current_product_ids
        ).distinct()
        
        return suggested_modules

