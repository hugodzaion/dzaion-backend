# -*- coding: utf-8 -*-
"""
Módulo de Signal Receivers para o App 'activities'.

Este módulo contém as funções que escutam por sinais emitidos por outros
apps do sistema (ex: post_save, post_delete) e disparam a criação de
registros de UserActivity.

É a ponte entre os eventos que acontecem no sistema e o feed de atividades.

Author: Dzaion
Version: 1.0.0
"""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserActivity
from .services import create_activity


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def handle_user_creation(sender, instance, created, **kwargs):
    """
    Escuta pelo sinal de criação de um novo usuário.

    Quando um usuário é criado (`created=True`), gera uma atividade no feed
    dele informando sobre o seu próprio cadastro.
    """
    if created:
        create_activity(
            user=instance,
            actor=instance,
            verb="cadastrou-se na plataforma",
            event_type=UserActivity.EventType.ADMINISTRATIVE,
            timestamp=instance.created_at
        )
