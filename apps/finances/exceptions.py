# -*- coding: utf-8 -*-
"""
Módulo de Exceções Customizadas para o App 'finances'.

Estas exceções são usadas para sinalizar erros de negócio específicos
dentro da camada de serviço financeira, permitindo um tratamento de
erros mais claro e explícito nas camadas superiores (views).

Author: Dzaion
Version: 0.2.0
"""

class FinanceError(Exception):
    """Classe base para todas as exceções do app de finanças."""
    pass

class InsufficientFundsError(FinanceError):
    """Lançada quando uma operação de débito falha por falta de saldo."""
    pass

class WalletAlreadyExistsError(FinanceError):
    """Lançada ao tentar criar uma carteira para um proprietário que já possui uma."""
    pass

class InvalidTransactionAmountError(FinanceError):
    """Lançada quando o valor de uma transação é inválido (ex: negativo ou zero)."""
    pass

# DZAION-FIX: Adicionando as exceções que estavam faltando.
class InvoiceAlreadyPaidError(FinanceError):
    """Lançada ao tentar pagar uma fatura que já está com o status 'Paga'."""
    pass

class InvoiceStatusError(FinanceError):
    """Lançada ao tentar realizar uma operação em uma fatura com status inválido (ex: pagar uma fatura cancelada)."""
    pass

