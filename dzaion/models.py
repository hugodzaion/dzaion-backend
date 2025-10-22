# -*- coding: utf-8 -*-
"""
Módulo de Modelos para o App 'dzaion' (O "Cérebro").

Este módulo define o centro de inteligência e ação do ecossistema,
gerenciando o catálogo de modelos de IA, suas capacidades, o histórico
de interações e o registro de consumo de recursos.

Author: Dzaion
Version: 1.0.0
"""
from datetime import timedelta
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from core.models import BaseModel

class AIModel(BaseModel):
    """
    Um registro dos modelos de linguagem (LLMs) que o Dzaion pode utilizar.
    """
    class UsageMode(models.TextChoices):
        REAL_TIME = 'REAL_TIME', 'Tempo Real'
        BATCH = 'BATCH', 'Em Lote (Batch)'

    name = models.CharField(max_length=100, verbose_name='Nome Legível')
    identifier = models.CharField(
        max_length=100, unique=True,
        verbose_name='Identificador de API',
        help_text='O nome técnico exato do modelo para as chamadas de API (ex: gpt-4o).'
    )
    usage_mode = models.CharField(
        max_length=15,
        choices=UsageMode.choices,
        verbose_name='Modo de Operação'
    )
    description = models.TextField(verbose_name='Descrição')

    class Meta:
        verbose_name = 'Modelo de IA'
        verbose_name_plural = 'Modelos de IA'
        ordering = ['name']

    def __str__(self):
        return self.name


class DzaionAction(BaseModel):
    """
    A fonte da verdade para todas as capacidades da IA ("verbos").
    """
    class CostBearer(models.TextChoices):
        SYSTEM = 'SYSTEM', 'Sistema (Gratuito)'
        CONTRACTOR = 'CONTRACTOR', 'Contratante (Pago)'

    name = models.CharField(max_length=100, verbose_name='Nome da Ação')
    verb_code = models.CharField(
        max_length=100, unique=True,
        verbose_name='Verbo (Código Interno)',
        help_text='O código interno usado pelo sistema (ex: activate_account).'
    )
    default_model = models.ForeignKey(
        AIModel,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Modelo de IA Padrão'
    )
    cost_bearer = models.CharField(
        max_length=15,
        choices=CostBearer.choices,
        default=CostBearer.CONTRACTOR,
        verbose_name='Responsável pelo Custo'
    )
    default_expiration_seconds = models.PositiveIntegerField(
        default=3600, # Padrão de 1 hora
        verbose_name='Prazo Padrão (segundos)',
        help_text='Tempo para expirar um AIThoughtProcess. 0 significa que nunca expira.'
    )
    is_active = models.BooleanField(default=True, verbose_name='Ativa')

    # DZAION-REFACTOR: Campos para a integração com a IA.
    instructions = models.TextField(
        blank=True,
        verbose_name='Instruções para a IA',
        help_text='O prompt de sistema (instrução) específico para esta ação.'
    )
    parameters_schema = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Schema de Parâmetros (Tool Calling)',
        help_text='A definição em JSON Schema dos parâmetros que esta ação requer.'
    )

    class Meta:
        verbose_name = 'Ação da IA (Verbo)'
        verbose_name_plural = 'Ações da IA (Verbos)'
        ordering = ['name']

    def __str__(self):
        return self.name


class Conversation(BaseModel):
    """
    Um container que agrupa uma sequência de mensagens com a IA.
    """
    class ConversationStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Ativa'
        FINISHED = 'FINISHED', 'Finalizada'
        ARCHIVED = 'ARCHIVED', 'Arquivada'

    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='conversations',
        verbose_name='Inquilino (Proprietário)'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='conversations',
        verbose_name='Usuário (Proprietário)'
    )
    initial_action = models.ForeignKey(
        DzaionAction,
        on_delete=models.PROTECT,
        verbose_name='Ação Inicial'
    )
    status = models.CharField(
        max_length=15,
        choices=ConversationStatus.choices,
        default=ConversationStatus.ACTIVE,
        verbose_name='Status da Conversa'
    )

    class Meta:
        verbose_name = 'Conversa com IA'
        verbose_name_plural = 'Conversas com IA'
        ordering = ['-updated_at']
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(tenant__isnull=False, user__isnull=True) |
                    Q(tenant__isnull=True, user__isnull=False)
                ),
                name='exclusive_owner_for_conversation'
            )
        ]

    def __str__(self):
        owner = self.tenant or self.user
        return f"Conversa de {owner} sobre {self.initial_action.name}"


class Message(BaseModel):
    """
    O registro de uma única troca de informação dentro de uma Conversation.
    """
    class Direction(models.TextChoices):
        INBOUND = 'INBOUND', 'Entrada (Usuário -> IA)'
        OUTBOUND = 'OUTBOUND', 'Saída (IA -> Usuário)'

    class MessageStatus(models.TextChoices):
        SENT = 'SENT', 'Enviada'
        DELIVERED = 'DELIVERED', 'Entregue'
        READ = 'READ', 'Lida'
        FAILED = 'FAILED', 'Falhou'

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Conversa'
    )
    direction = models.CharField(
        max_length=10,
        choices=Direction.choices,
        verbose_name='Direção'
    )
    content = models.TextField(verbose_name='Conteúdo')
    status = models.CharField(
        max_length=10,
        choices=MessageStatus.choices,
        default=MessageStatus.SENT,
        verbose_name='Status da Entrega'
    )

    class Meta:
        verbose_name = 'Mensagem de Conversa'
        verbose_name_plural = 'Mensagens de Conversa'
        ordering = ['created_at']

    def __str__(self):
        return f"Mensagem {self.id.hex[:8]} na conversa {self.conversation.id.hex[:8]}"


class TokenUsageLog(BaseModel):
    """
    O registro financeiro imutável de cada chamada à API da IA.
    """
    payer_tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='token_usage_logs',
        verbose_name='Inquilino (Pagador)'
    )
    payer_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='token_usage_logs',
        verbose_name='Usuário (Pagador)'
    )
    message = models.OneToOneField(
        Message,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Mensagem de Origem'
    )
    dzaion_action = models.ForeignKey(
        DzaionAction,
        on_delete=models.PROTECT,
        verbose_name='Ação (Motivo)'
    )
    ai_model = models.ForeignKey(
        AIModel,
        on_delete=models.PROTECT,
        verbose_name='Modelo de IA Utilizado'
    )
    input_tokens = models.PositiveIntegerField(verbose_name='Tokens de Entrada')
    output_tokens = models.PositiveIntegerField(verbose_name='Tokens de Saída')
    is_billed = models.BooleanField(default=False, verbose_name='Faturado?', db_index=True)

    class Meta:
        verbose_name = 'Log de Uso de Tokens'
        verbose_name_plural = 'Logs de Uso de Tokens'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(payer_tenant__isnull=False, payer_user__isnull=True) |
                    Q(payer_tenant__isnull=True, payer_user__isnull=False)
                ),
                name='exclusive_payer_for_token_log'
            )
        ]

    def __str__(self):
        return f"Uso de {self.input_tokens + self.output_tokens} tokens"


class AIThoughtProcess(BaseModel):
    """
    O "ticket de trabalho" interno da IA, representando uma tarefa ou intenção.
    """
    class ProcessStatus(models.TextChoices):
        PENDING_EXECUTION = 'PENDING_EXECUTION', 'Pendente de Execução'
        PENDING_USER_RESPONSE = 'PENDING_USER_RESPONSE', 'Aguardando Usuário'
        PROCESSING = 'PROCESSING', 'Em Processamento'
        FINISHED = 'FINISHED', 'Finalizado'
        FAILED = 'FAILED', 'Falhou'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='thought_processes',
        verbose_name='Interlocutor'
    )
    tenant_context = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name='Contexto do Inquilino'
    )
    action = models.ForeignKey(
        DzaionAction,
        on_delete=models.PROTECT,
        verbose_name='Ação (Missão)'
    )
    conversation = models.OneToOneField(
        Conversation,
        on_delete=models.PROTECT,
        related_name='thought_process',
        verbose_name='Conversa Associada'
    )
    status = models.CharField(
        max_length=25,
        choices=ProcessStatus.choices,
        default=ProcessStatus.PENDING_EXECUTION,
        verbose_name='Progresso da Tarefa'
    )
    expires_at = models.DateTimeField(
        verbose_name='Prazo de Validade'
    )
    finished_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Data de Conclusão'
    )

    class Meta:
        verbose_name = 'Processo de Pensamento da IA'
        verbose_name_plural = 'Processos de Pensamento da IA'
        ordering = ['-expires_at']

    def save(self, *args, **kwargs):
        """
        Calcula ou atualiza o 'expires_at' a cada interação.
        """
        if self.action and self.action.default_expiration_seconds > 0:
            self.expires_at = timezone.now() + timedelta(
                seconds=self.action.default_expiration_seconds
            )
        elif not self.pk: # Se for a primeira vez e a ação não tiver expiração
            self.expires_at = timezone.now() + timedelta(days=365*100)
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Processo para '{self.action.name}' com {self.user.name}"

