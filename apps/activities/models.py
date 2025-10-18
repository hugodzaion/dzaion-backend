# -*- coding: utf-8 -*-
"""
Módulo de Modelos para o App 'activities'.

Define o modelo `UserActivity`, a espinha dorsal do feed de atividades
unificado do sistema Dzaion. Cada registro é um evento imutável que
ocorreu no ecossistema.

Models:
    UserActivity: Armazena um único evento da vida de um usuário na plataforma.

Author: Dzaion
Version: 1.0.0
"""
from __future__ import annotations

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.models import BaseModel


class UserActivity(BaseModel):
    """
    Representa um registro imutável de um evento que ocorreu no ecossistema.

    Este modelo é o coração do feed de atividades, descrevendo uma história
    completa: quem fez, o quê, em qual objeto, e para quem isso importa.
    """

    class EventType(models.TextChoices):
        """Categorias de alto nível para os eventos, usadas para filtragem."""
        FINANCIAL = 'FINANCIAL', 'Financeiro'
        SOCIAL = 'SOCIAL', 'Social'
        ADMINISTRATIVE = 'ADMINISTRATIVE', 'Administrativo'
        SERVICE = 'SERVICE', 'Serviço'

    class Priority(models.TextChoices):
        """Níveis de urgência para destacar notificações e priorizar ações da IA."""
        HIGH = 'HIGH', 'Alta'
        MEDIUM = 'MEDIUM', 'Média'
        LOW = 'LOW', 'Baixa'

    # --- O Dono do Feed ---
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name='Dono do Feed',
        help_text='O usuário a quem esta atividade pertence e para quem ela será exibida.',
        db_index=True
    )

    # --- O Protagonista (Quem fez?) ---
    actor_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='actor_activities'
    )
    actor_object_id = models.UUIDField(db_index=True)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    # --- A Ação (O quê?) ---
    verb = models.CharField(
        max_length=255,
        verbose_name='Verbo',
        help_text='O verbo que descreve a ação (ex: criou, pagou, comentou em).'
    )

    # --- O Alvo (Em quê?) ---
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='target_activities',
        null=True, blank=True
    )
    target_object_id = models.UUIDField(null=True, blank=True, db_index=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    # --- Metadados do Evento ---
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        verbose_name='Tipo de Evento',
        help_text='A categoria do evento, para facilitar a filtragem.',
        db_index=True
    )
    data_snapshot = models.JSONField(
        verbose_name='Registro Imutável (Snapshot)',
        help_text='Dados relevantes do evento no momento em que ele ocorreu.',
        null=True, blank=True
    )
    timestamp = models.DateTimeField(
        verbose_name='Timestamp do Evento',
        help_text='O momento exato em que o evento original ocorreu no módulo de origem.',
        db_index=True
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Status de Leitura',
        help_text='True se o usuário já visualizou a atividade no feed.'
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.LOW,
        verbose_name='Prioridade',
        help_text='A urgência do evento, usada para destaques e pela IA.'
    )

    class Meta:
        verbose_name = 'Atividade do Usuário'
        verbose_name_plural = 'Atividades dos Usuários'
        ordering = ['-timestamp']

    def __str__(self):
        actor_str = f"{self.actor}" if self.actor else "Sistema"
        if self.target:
            return f'{actor_str} {self.verb} {self.target}'
        return f'{actor_str} {self.verb}'
