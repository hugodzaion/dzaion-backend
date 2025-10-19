# -*- coding: utf-8 -*-
"""
Módulo da Camada de Serviço para o App 'finances'.

Este arquivo contém a classe FinanceService, o único ponto de entrada para
todas as operações financeiras, garantindo segurança, consistência e
atomicidade através de transações de banco de dados.

Author: Dzaion
Version: 0.1.0
"""
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from .models import Wallet, Transaction, TransactionType
from .exceptions import (
    InsufficientFundsError,
    WalletAlreadyExistsError,
    InvalidTransactionAmountError
)

class FinanceService:
    """
    Serviço que centraliza toda a lógica de negócio financeira.
    """

    @staticmethod
    def _get_owner_fields(owner):
        """Método auxiliar para determinar se o proprietário é um User ou Tenant."""
        owner_type = ContentType.objects.get_for_model(owner)
        if owner_type.model == 'user':
            return {'user': owner}
        elif owner_type.model == 'tenant':
            return {'tenant': owner}
        raise TypeError("O proprietário da carteira deve ser um User ou Tenant.")

    @staticmethod
    def create_wallet(owner) -> Wallet:
        """
        Cria uma nova carteira para um proprietário (User ou Tenant).

        :param owner: A instância do User ou Tenant.
        :return: A instância da Wallet criada.
        :raises WalletAlreadyExistsError: Se o proprietário já tiver uma carteira.
        """
        owner_fields = FinanceService._get_owner_fields(owner)
        if Wallet.objects.filter(**owner_fields).exists():
            raise WalletAlreadyExistsError(f"Uma carteira já existe para {owner}.")
        
        return Wallet.objects.create(**owner_fields, balance=Decimal('0.00'))

    @staticmethod
    @transaction.atomic
    def credit(
        wallet: Wallet,
        amount: Decimal,
        transaction_type: TransactionType,
        invoice=None
    ) -> Transaction:
        """
        Adiciona crédito a uma carteira e registra a transação.

        :param wallet: A carteira a ser creditada.
        :param amount: O valor a ser adicionado (deve ser positivo).
        :param transaction_type: O tipo da transação.
        :param invoice: (Opcional) A fatura associada a esta transação.
        :return: A transação de crédito criada.
        :raises InvalidTransactionAmountError: Se o valor for menor ou igual a zero.
        """
        if amount <= 0:
            raise InvalidTransactionAmountError("O valor do crédito deve ser positivo.")

        # Atualiza o saldo da carteira de forma segura
        wallet.balance += amount
        wallet.save(update_fields=['balance'])

        # Cria o registro imutável da transação
        return Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            type=transaction_type,
            invoice=invoice,
            status=Transaction.TransactionStatus.COMPLETED,
            processed_at=timezone.now()
        )

    @staticmethod
    @transaction.atomic
    def debit(
        wallet: Wallet,
        amount: Decimal,
        transaction_type: TransactionType,
        invoice=None
    ) -> Transaction:
        """
        Remove fundos de uma carteira e registra a transação.

        :param wallet: A carteira a ser debitada.
        :param amount: O valor a ser removido (deve ser positivo).
        :param transaction_type: O tipo da transação.
        :param invoice: (Opcional) A fatura associada.
        :return: A transação de débito criada.
        :raises InvalidTransactionAmountError: Se o valor for inválido.
        :raises InsufficientFundsError: Se o saldo for insuficiente.
        """
        if amount <= 0:
            raise InvalidTransactionAmountError("O valor do débito deve ser positivo.")
        
        if wallet.balance < amount:
            raise InsufficientFundsError("Saldo insuficiente para realizar a operação.")

        # Atualiza o saldo da carteira
        wallet.balance -= amount
        wallet.save(update_fields=['balance'])

        # Cria o registro imutável da transação (valor negativo para débito)
        return Transaction.objects.create(
            wallet=wallet,
            amount=-amount,
            type=transaction_type,
            invoice=invoice,
            status=Transaction.TransactionStatus.COMPLETED,
            processed_at=timezone.now()
        )
