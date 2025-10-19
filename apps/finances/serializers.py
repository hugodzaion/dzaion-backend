# -*- coding: utf-8 -*-
"""
Módulo de Serializers para o App 'finances'.

Define os schemas para a representação JSON dos modelos financeiros,
garantindo que os dados sejam expostos de forma segura e estruturada.

Author: Dzaion
Version: 0.1.0
"""
from rest_framework import serializers
from .models import Wallet, Transaction, TransactionType

class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Wallet. Expõe o saldo da carteira.
    """
    class Meta:
        model = Wallet
        fields = ['id', 'balance']
        read_only_fields = fields


class TransactionTypeSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo TransactionType. Usado de forma aninhada.
    """
    class Meta:
        model = TransactionType
        fields = ['name', 'code', 'is_debit']


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer para listar as transações (o "extrato") de uma carteira.
    """
    type = TransactionTypeSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id',
            'type',
            'amount',
            'status',
            'processed_at',
            'invoice' # Expondo o ID da fatura, se houver
        ]
        read_only_fields = fields
