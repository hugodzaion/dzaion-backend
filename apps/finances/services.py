# -*- coding: utf-8 -*-
"""
Módulo da Camada de Serviço para o App 'finances'.

Este arquivo contém a classe FinanceService, o único ponto de entrada para
todas as operações financeiras, garantindo segurança, consistência e
atomicidade através de transações de banco de dados.

Author: Dzaion
Version: 0.2.0
"""
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from .models import Wallet, Transaction, TransactionType, Invoice
from .exceptions import (
    InsufficientFundsError,
    WalletAlreadyExistsError,
    InvalidTransactionAmountError,
    InvoiceAlreadyPaidError,
    InvoiceStatusError,
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
        """
        owner_fields = FinanceService._get_owner_fields(owner)
        if Wallet.objects.filter(**owner_fields).exists():
            raise WalletAlreadyExistsError(f"Uma carteira já existe para {owner}.")
        
        return Wallet.objects.create(**owner_fields, balance=Decimal('0.00'))

    @staticmethod
    @transaction.atomic
    def credit(wallet: Wallet, amount: Decimal, transaction_type_code: str, invoice=None) -> Transaction:
        """ Adiciona crédito a uma carteira e registra a transação. """
        if amount <= 0:
            raise InvalidTransactionAmountError("O valor do crédito deve ser positivo.")

        transaction_type = TransactionType.objects.get(code=transaction_type_code)
        wallet.balance += amount
        wallet.save(update_fields=['balance'])

        return Transaction.objects.create(
            wallet=wallet, amount=amount, type=transaction_type, invoice=invoice,
            status=Transaction.TransactionStatus.COMPLETED, processed_at=timezone.now()
        )

    @staticmethod
    @transaction.atomic
    def debit(wallet: Wallet, amount: Decimal, transaction_type_code: str, invoice=None) -> Transaction:
        """ Remove fundos de uma carteira e registra a transação. """
        if amount <= 0:
            raise InvalidTransactionAmountError("O valor do débito deve ser positivo.")
        if wallet.balance < amount:
            raise InsufficientFundsError("Saldo insuficiente para realizar a operação.")

        transaction_type = TransactionType.objects.get(code=transaction_type_code)
        wallet.balance -= amount
        wallet.save(update_fields=['balance'])

        return Transaction.objects.create(
            wallet=wallet, amount=-amount, type=transaction_type, invoice=invoice,
            status=Transaction.TransactionStatus.COMPLETED, processed_at=timezone.now()
        )

    @staticmethod
    @transaction.atomic
    def pay_invoice_with_wallet(invoice: Invoice) -> Transaction:
        """
        Realiza o pagamento de uma fatura usando o saldo da carteira do Tenant.
        """
        if invoice.status == Invoice.InvoiceStatus.PAID:
            raise InvoiceAlreadyPaidError("Esta fatura já foi paga.")
        if invoice.status != Invoice.InvoiceStatus.OPEN:
            raise InvoiceStatusError("Apenas faturas abertas podem ser pagas.")

        tenant = invoice.tenant
        wallet = tenant.wallet.first()

        if not wallet:
            raise InsufficientFundsError("O Tenant não possui uma carteira para realizar o pagamento.")
        
        # O método 'debit' já verifica o saldo e levanta InsufficientFundsError se necessário.
        transaction = FinanceService.debit(
            wallet=wallet,
            amount=invoice.amount,
            transaction_type_code='INVOICE_PAYMENT',
            invoice=invoice
        )

        # Se o débito foi bem-sucedido, atualiza a fatura.
        invoice.status = Invoice.InvoiceStatus.PAID
        invoice.paid_at = timezone.now()
        invoice.save(update_fields=['status', 'paid_at'])

        return transaction

