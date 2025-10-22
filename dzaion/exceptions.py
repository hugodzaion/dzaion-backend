# -*- coding: utf-8 -*-
"""
Módulo de Exceções Customizadas para o App 'dzaion'.

Author: Dzaion
Version: 0.1.0
"""

class DzaionError(Exception):
    """Classe base para todas as exceções do app dzaion."""
    pass

class InsufficientFundsForAIError(DzaionError):
    """Lançada quando um contratante não tem saldo para executar uma ação da IA."""
    pass

class ContextIdentificationError(DzaionError):
    """Lançada quando o Orquestrador não consegue identificar o usuário."""
    pass

class IntentClassificationError(DzaionError):
    """Lançada quando a intenção do usuário não pode ser classificada."""
    pass

class AIClientError(DzaionError):
    """Classe base para erros do cliente da API de IA."""
    pass

class AIAuthenticationError(AIClientError):
    """Lançada quando a chave da API da OpenAI está faltando ou é inválida."""
    pass

class AIAPIError(AIClientError):
    """Lançada quando a API da OpenAI retorna um erro de negócio."""
    pass

