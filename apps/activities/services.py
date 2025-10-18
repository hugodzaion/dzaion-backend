# -*- coding: utf-8 -*-
"""
Módulo de Serviços para o App 'activities'.

Centraliza a lógica de negócio para manipulação de atividades, garantindo
que a criação e gestão de registros `UserActivity` seja consistente e
desacoplada dos signal receivers.

Author: Dzaion
Version: 1.0.0
"""
from __future__ import annotations
import logging
from datetime import datetime
from django.db.models import Model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

# DZAION-REVIEW: Importado o modelo User diretamente para corrigir o erro de tipo do Pylance.
from accounts.models import User
from .models import UserActivity

# Obtém uma instância de logger específica para este módulo.
logger = logging.getLogger(__name__)

def create_activity(
    # DZAION-REVIEW: Corrigido o type hint para usar a classe User importada.
    # A anotação 'Type[]' foi removida pois a função espera uma *instância* do modelo, não a classe.
    user: User,
    actor: Model,
    verb: str,
    event_type: str,
    target: Model | None = None,
    timestamp: datetime | None = None,
    data_snapshot: dict | None = None,
    priority: str = UserActivity.Priority.LOW
) -> UserActivity | None:
    """
    Cria e salva um registro de UserActivity de forma segura.

    Esta função é o único ponto de entrada para a criação de atividades,
    garantindo que todas as regras de negócio sejam aplicadas.

    :param user: A instância do usuário que é o "dono" do feed.
    :param actor: A instância do modelo que realizou a ação (o protagonista).
    :param verb: A descrição da ação (ex: 'criou a fatura').
    :param event_type: A categoria do evento (deve ser um valor de UserActivity.EventType).
    :param target: (Opcional) A instância do modelo que sofreu a ação.
    :param timestamp: (Opcional) O momento exato do evento. Se não for fornecido, usa o tempo atual.
    :param data_snapshot: (Opcional) Um dicionário JSON com dados do evento.
    :param priority: (Opcional) A prioridade do evento.
    :return: A instância de UserActivity criada ou None em caso de erro.
    """
    try:
        # Garante um timestamp, usando o tempo atual como padrão.
        if timestamp is None:
            timestamp = timezone.now()

        # Obtém o ContentType do ator dinamicamente.
        actor_content_type = ContentType.objects.get_for_model(actor)

        # Lida com o alvo opcional.
        target_content_type = None
        target_object_id = None
        if target:
            target_content_type = ContentType.objects.get_for_model(target)
            target_object_id = target.pk

        activity = UserActivity.objects.create(
            user=user,
            actor_content_type=actor_content_type,
            actor_object_id=actor.pk,
            verb=verb,
            target_content_type=target_content_type,
            target_object_id=target_object_id,
            event_type=event_type,
            timestamp=timestamp,
            data_snapshot=data_snapshot,
            priority=priority,
        )
        logger.info(f"Atividade criada com sucesso: '{activity}' para o usuário {user.email}")
        return activity

    except Exception as e:
        logger.error(f"Falha ao criar atividade para o usuário {user.email}: {e}", exc_info=True)
        return None

