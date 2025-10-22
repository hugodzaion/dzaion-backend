# -*- coding: utf-8 -*-
"""
Módulo de Tarefas Assíncronas (Celery) para o App 'dzaion'.

Author: Dzaion
Version: 0.2.0
"""
import logging
from celery import shared_task
from .orchestrators import DzaionOrchestrator

logger = logging.getLogger(__name__)

@shared_task(name="dzaion.dzaion_mission_handler")
def dzaion_mission_handler(mission_data: dict):
    """
    A "Torre de Controle": ponto de entrada único para todas as missões da IA.

    Sua única responsabilidade é receber a missão e delegá-la ao Orquestrador.
    """
    logger.info(f"Dzaion Mission Handler recebeu uma nova missão: {mission_data}")
    try:
        DzaionOrchestrator.run(mission_data=mission_data)
    except Exception as e:
        logger.error(f"Erro ao executar a missão no DzaionOrchestrator: {e}", exc_info=True)

