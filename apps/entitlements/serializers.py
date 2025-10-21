# -*- coding: utf-8 -*-
"""
Módulo de Serializers para o App 'entitlements'.

Author: Dzaion
Version: 0.1.0
"""
from rest_framework import serializers
from .models import Subscription
from products.models import ProductPlan

class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer para exibir os detalhes de uma Subscription."""
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    product_name = serializers.CharField(source='plan.product.name', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'status', 'price', 'start_date', 'next_billing_date',
            'plan_name', 'product_name'
        ]

class SubscriptionCreateSerializer(serializers.Serializer):
    """Serializer para validar a criação de uma nova Subscription."""
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductPlan.objects.filter(status=ProductPlan.PlanStatus.ACTIVE),
        write_only=True
    )
