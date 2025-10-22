# -*- coding: utf-8 -*-
"""
Módulo da Camada de Serviço para o App 'dzaion'.

Author: Dzaion
Version: 0.5.0
"""
import logging
from django.utils import timezone
from .models import AIThoughtProcess, TokenUsageLog, DzaionAction, AIModel, Conversation
from .exceptions import InsufficientFundsForAIError
from accounts.models import User
from tenants.models import Tenant

logger = logging.getLogger('dzaion_service')

class DzaionService:
    """
    Serviço que gerencia os modelos do próprio app Dzaion.
    """

    @staticmethod
    def find_active_thought_process(user: User) -> AIThoughtProcess | None:
        """
        Encontra um "ticket de conversa" ativo e não expirado para um usuário.
        Se encontrar processos ativos mas expirados, eles são invalidados.
        """
        now = timezone.now()
        
        # 1. Rotina de limpeza: Invalida qualquer processo expirado para este usuário.
        expired_processes = AIThoughtProcess.objects.filter(
            user=user,
            expires_at__lte=now
        ).exclude(status__in=[AIThoughtProcess.ProcessStatus.FINISHED, AIThoughtProcess.ProcessStatus.FAILED])
        
        if expired_processes.exists():
            count = expired_processes.update(status=AIThoughtProcess.ProcessStatus.FAILED, finished_at=now)
            logger.info(f"{count} processo(s) de pensamento expirado(s) foram marcados como FAILED para o usuário {user.email}.")

        # 2. DZAION-FIX: Busca o processo ativo mais recente (para qualquer ação)
        #    que esteja aguardando uma resposta.
        return AIThoughtProcess.objects.filter(
            user=user, 
            expires_at__gt=now
        ).exclude(
            status__in=[AIThoughtProcess.ProcessStatus.FINISHED, AIThoughtProcess.ProcessStatus.FAILED]
        ).order_by('-created_at').first()

    @staticmethod
    def create_thought_process_and_conversation(user: User, action: DzaionAction, tenant_context: Tenant | None = None) -> AIThoughtProcess:
        """
        Cria um novo processo de pensamento e a Conversa associada.
        """
        logger.info(f"Criando novo processo de pensamento e conversa para a ação '{action.verb_code}' para o usuário {user.email}.")
        
        conversation_owner = {'user': user} if not tenant_context else {'tenant': tenant_context}
        
        conversation = Conversation.objects.create(
            initial_action=action,
            **conversation_owner
        )
        
        thought_process = AIThoughtProcess.objects.create(
            user=user,
            action=action,
            tenant_context=tenant_context,
            conversation=conversation
        )
        return thought_process

    @staticmethod
    def get_or_create_usage_profile(payer):
        """
        Busca ou cria um perfil de uso de IA para um contratante (User ou Tenant).
        Usa "late import" para evitar importação circular.
        """
        from entitlements.models import DzaionUsageProfile

        if isinstance(payer, User):
            profile, created = DzaionUsageProfile.objects.get_or_create(user=payer)
            if created:
                logger.info(f"Novo perfil de uso de IA criado para o usuário {payer.email}")
        elif isinstance(payer, Tenant):
            profile, created = DzaionUsageProfile.objects.get_or_create(tenant=payer)
            if created:
                logger.info(f"Novo perfil de uso de IA criado para o Tenant {payer.name}")
        else:
            logger.error(f"Tentativa de obter perfil de uso para tipo de pagador inválido: {type(payer)}")
            raise TypeError("O pagador deve ser um objeto User ou Tenant.")
        
        return profile

    @staticmethod
    def log_token_usage(
        dzaion_action: DzaionAction,
        user: User,
        ai_model: AIModel,
        input_tokens: int,
        output_tokens: int,
        tenant_context: Tenant | None = None,
        message = None
    ):
        """
        Verifica o saldo (se aplicável) e registra o consumo de tokens.
        """
        payer_user, payer_tenant = None, None
        
        payer_entity = tenant_context or user
        if isinstance(payer_entity, User):
            payer_user = payer_entity
        else:
            payer_tenant = payer_entity

        if dzaion_action.cost_bearer == DzaionAction.CostBearer.CONTRACTOR:
            wallet = payer_entity.wallet.first()
            if not wallet or wallet.balance <= 0:
                raise InsufficientFundsForAIError("O contratante não possui saldo para esta operação.")
        
        TokenUsageLog.objects.create(
            payer_user=payer_user,
            payer_tenant=payer_tenant,
            dzaion_action=dzaion_action,
            ai_model=ai_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            message=message
        )
        logger.info(f"Log de uso de tokens criado para a ação '{dzaion_action.verb_code}'.")

