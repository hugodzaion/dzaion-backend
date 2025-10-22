# -*- coding: utf-8 -*-
"""
Módulo do Cliente da API da OpenAI.

Author: Dzaion
Version: 0.3.3
"""
import logging
import json
from openai import OpenAI, APIError, AuthenticationError
from decouple import config

from .exceptions import AIAuthenticationError, AIAPIError

logger = logging.getLogger('dzaion_client')

class OpenAIClient:
    """
    Um cliente centralizado para interagir com a API da OpenAI.
    """
    def __init__(self):
        self.api_key = config('OPENAI_API_KEY', default=None)
        if not self.api_key:
            logger.error("A chave da API da OpenAI (OPENAI_API_KEY) não foi encontrada no ambiente.")
            raise AIAuthenticationError("A chave da API da OpenAI não está configurada.")
        
        self.client = OpenAI(api_key=self.api_key)

    def generate_response(self, model: str, messages: list, tools: list | None = None, service_tier: str = 'auto') -> dict:
        """
        Gera uma resposta da IA, lidando tanto com texto simples quanto com Tool Calling.
        """
        request_payload = {
            "model": model,
            "messages": messages,
            "service_tier": service_tier,
        }
        if tools:
            request_payload["tools"] = tools
            request_payload["tool_choice"] = "auto"
        
        # Converte o payload para JSON para logar (removendo objetos não serializáveis se houver)
        try:
            loggable_payload = json.dumps(request_payload, indent=2, default=str)
            logger.debug(f"Enviando requisição para a OpenAI com o modelo {model}. Payload:\n{loggable_payload}")
        except Exception:
            logger.debug(f"Enviando requisição para a OpenAI com o modelo {model}.")

        try:
            # Usando a API de Chat Completions, que é a base para o Tool Calling
            response = self.client.chat.completions.create(**request_payload)
            
            response_message = response.choices[0].message
            
            logger.debug(f"Objeto 'usage' recebido da OpenAI: {response.usage}")
            
            usage_data = {
                'input_tokens': response.usage.prompt_tokens if response.usage else 0,
                'output_tokens': response.usage.completion_tokens if response.usage else 0,
                'total_tokens': response.usage.total_tokens if response.usage else 0,
            }

            logger.debug(f"Resposta da OpenAI recebida. Mensagem: {response_message}")
            
            return {
                'message': response_message,
                'usage': usage_data
            }

        except AuthenticationError as e:
            logger.error(f"Erro de autenticação com a API da OpenAI: {e}")
            raise AIAuthenticationError(f"Erro de autenticação com a OpenAI: {e}")
        except APIError as e:
            logger.error(f"Erro na API da OpenAI: {e.status_code} - {e.response}")
            raise AIAPIError(f"A API da OpenAI retornou um erro: {getattr(e, 'message', str(e))}")
        except Exception as e:
            logger.error(f"Erro inesperado ao chamar a API da OpenAI: {e}", exc_info=True)
            raise AIAPIError("Um erro inesperado ocorreu ao se comunicar com a OpenAI.")

