# -*- coding: utf-8 -*-
"""
Módulo de Views (Controladores) para o App 'finances'.

Contém os endpoints da API para consulta de dados financeiros, como
saldo de carteira e histórico de transações. As views delegam
operações de escrita para o FinanceService.

Author: Dzaion
Version: 0.1.0
"""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsActiveUser
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer

class MyWalletView(generics.RetrieveAPIView):
    """
    Endpoint para obter a carteira (Wallet) do usuário logado.
    """
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_object(self):
        """
        Retorna a carteira associada ao usuário que fez a requisição.
        O sistema garante (via sinais) que cada usuário tenha uma carteira.
        """
        # Acessa a carteira através da relação reversa definida no modelo Wallet.
        # O related_name='wallet' nos permite fazer isso.
        return self.request.user.wallet.first()


class MyTransactionListView(generics.ListAPIView):
    """
    Endpoint para listar o histórico de transações (extrato)
    da carteira do usuário logado.
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get_queryset(self):
        """
        Filtra as transações para retornar apenas aquelas pertencentes
        à carteira do usuário que fez a requisição.
        """
        user_wallet = self.request.user.wallet.first()
        if user_wallet:
            return Transaction.objects.filter(wallet=user_wallet).order_by('-processed_at')
        
        # Se, por algum motivo, o usuário não tiver uma carteira, retorna um queryset vazio.
        return Transaction.objects.none()
