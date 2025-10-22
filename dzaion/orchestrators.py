# -*- coding: utf-8 -*-
"""
Módulo do Orquestrador da IA Dzaion.

Author: Dzaion
Version: 0.6.2
"""
import logging
import json

from django.template.loader import render_to_string
from django.utils import timezone

from accounts.models import User
from accounts.services import AccountService
from guards.services import GuardService
from dispatchers.services import get_dispather_service
from .models import DzaionAction, AIThoughtProcess, Conversation, Message, AIModel
from .services import DzaionService
from .tool_registry import TOOL_REGISTRY
from .exceptions import ContextIdentificationError, IntentClassificationError, AIAPIError, InsufficientFundsForAIError
from .clients import OpenAIClient

logger = logging.getLogger('dzaion_orchestrator')

class DzaionOrchestrator:
    """
    Orquestra o ciclo de vida de uma única missão da IA Dzaion.
    """
    def __init__(self, mission_data: dict):
        self.mission_data = mission_data
        self.mission_type = mission_data.get('mission_type')
        self.trigger_info = mission_data.get('trigger_info', {})
        
        self.user = None
        self.tenant_context = None
        self.thought_process = None
        self.dzaion_action = None
        self.conversation = None 
        self.client = OpenAIClient()
        self.total_usage = {'input_tokens': 0, 'output_tokens': 0}
        self.service_tier = 'auto'
        self.ai_model = None

    @classmethod
    def run(cls, mission_data: dict):
        orchestrator = cls(mission_data)
        orchestrator._execute_mission()

    def _execute_mission(self):
        try:
            self._identify_context_and_intent()
            self._check_financial_viability()
            interaction_result = self._execute_llm_interaction()
            response_text = interaction_result.get('text', "Não consegui processar sua solicitação no momento.")
            self._log_token_usage()
            self._dispatch_response(response_text)
            
        except (ContextIdentificationError, IntentClassificationError, InsufficientFundsForAIError) as e:
            logger.warning(f"Missão encerrada prematuramente: {e}")
            if self.user:
                self._dispatch_response(str(e))
        except Exception as e:
            logger.error(f"Erro crítico na missão: {e}", exc_info=True)
            if self.user:
                self._dispatch_response("Desculpe, encontrei um erro e não consigo continuar no momento.")

    def _identify_context_and_intent(self):
        """
        Fase 1 e 2: Identifica o usuário e classifica a intenção.
        Esta é a nova lógica de roteamento.
        """
        logger.info(f"Fase 1: Identificando contexto da missão '{self.mission_type}'.")
        
        # 1. Identificar o Usuário
        user_model = User
        if self.mission_type == 'REACTIVE':
            whatsapp_number = self.trigger_info.get('whatsapp_number')
            self.user = AccountService.find_user_by_whatsapp(whatsapp_number)
        elif self.mission_type == 'PROACTIVE':
            user_id = self.trigger_info.get('user_id')
            self.user = user_model.objects.get(id=user_id)

        if not self.user:
            raise ContextIdentificationError("Usuário não pôde ser identificado.")
        
        logger.info(f"Usuário identificado: {self.user.email}")
        
        logger.info("Fase 2: Classificando intenção.")
        
        # 2. Verificar Processos Ativos (Memória de Curto Prazo)
        # DZAION-FIX: A checagem de processo ativo vem ANTES do roteador.
        self.thought_process = DzaionService.find_active_thought_process(self.user)
        
        if self.thought_process:
            # Se um processo foi encontrado, a intenção já está definida.
            self.dzaion_action = self.thought_process.action
            self.tenant_context = self.thought_process.tenant_context
            self.conversation = self.thought_process.conversation
            logger.info(f"Processo de pensamento ativo encontrado: {self.dzaion_action.verb_code}")
        
        # 3. Classificar Nova Intenção (Roteador ou Proativo)
        else:
            action_verb = None
            if self.mission_type == 'PROACTIVE':
                action_verb = self.trigger_info.get('action_verb')
                logger.info(f"Intenção proativa recebida: '{action_verb}'")
            elif self.mission_type == 'REACTIVE':
                action_verb = self._route_reactive_intent() # Chama o Roteador Universal
                logger.info(f"Intenção reativa classificada pelo Roteador: '{action_verb}'")
            
            if not action_verb:
                raise IntentClassificationError("Não foi possível classificar a intenção do usuário.")
            
            # 4. Criar Novo Processo de Pensamento
            self.dzaion_action = DzaionAction.objects.get(verb_code=action_verb)
            self.thought_process = DzaionService.create_thought_process_and_conversation(
                user=self.user, 
                action=self.dzaion_action
                # TODO: Lógica para tenant_context em missões reativas
            )
            self.conversation = self.thought_process.conversation
            logger.info(f"Nenhum processo ativo. Criando novo processo para '{action_verb}'.")

        # 5. Definir Nível de Serviço
        self._set_service_tier()


    def _route_reactive_intent(self) -> str:
        """
        Usa um modelo de IA barato para classificar a intenção do usuário
        com base nas ações permitidas.
        """
        logger.debug("Iniciando Roteador Universal de Intenções.")
        user_actions = GuardService.get_user_dzaion_actions(self.user, self.tenant_context)
        if not user_actions.exists():
            return 'general_chat'

        tools_menu = [f"- '{action.verb_code}': {action.name}" for action in user_actions]
        tools_list = "\n".join(tools_menu)
        
        # Histórico de conversas gerais (não específico de um processo)
        general_history = self._load_conversation_history(limit=5) 
        
        instructions = (
            "Você é um roteador de intenções. Analise a última mensagem do usuário e o histórico. "
            "Sua única tarefa é retornar o 'verb_code' exato da ação que o usuário deseja executar, "
            "com base no cardápio de ações permitidas. Se nenhuma ação corresponder, "
            "retorne 'general_chat'."
            f"\n\nCARDÁPIO DE AÇÕES PERMITIDAS:\n{tools_list}"
        )
        
        try:
            router_model = AIModel.objects.filter(identifier__icontains='nano').first()
            if not router_model:
                router_model = self.dzaion_action.default_model if self.dzaion_action else AIModel.objects.first()

            messages = general_history + [{"role": "user", "content": self.trigger_info.get('message_body', '')}]
            
            response_data = self.client.generate_response(
                model=router_model.identifier,
                instructions=instructions,
                messages=messages
            )
            self._update_total_usage(response_data['usage'])
            
            classified_verb = response_data['message'].content.strip().replace("'", "").replace('"', '')
            
            if user_actions.filter(verb_code=classified_verb).exists():
                return classified_verb
            else:
                return 'general_chat'
                
        except Exception as e:
            logger.error(f"Erro no roteador de intenções: {e}", exc_info=True)
            raise IntentClassificationError("Falha ao classificar a intenção com a IA.")

    def _set_service_tier(self):
        """
        Define o modelo e o nível de serviço com base no perfil do contratante.
        """
        payer = self.tenant_context or self.user
        usage_profile = DzaionService.get_or_create_usage_profile(payer)
        
        self.service_tier = usage_profile.service_tier
        
        if self.mission_type == 'REACTIVE' and usage_profile.model_for_messaging:
            self.ai_model = usage_profile.model_for_messaging
        else:
            self.ai_model = self.dzaion_action.default_model
        
        if not self.ai_model:
            # Fallback de segurança se nenhum modelo for definido
            self.ai_model = AIModel.objects.first()
            
        logger.info(f"Modelo de IA definido: {self.ai_model.identifier}. Nível de serviço: {self.service_tier}.")

    def _check_financial_viability(self):
        """
        Fase de Checagem de Saldo.
        """
        logger.info("Fase 3: Verificando viabilidade financeira.")
        if not self.dzaion_action:
            raise IntentClassificationError("Ação não definida para checagem financeira.")
            
        if self.dzaion_action.cost_bearer == DzaionAction.CostBearer.CONTRACTOR:
            payer = self.tenant_context or self.user
            wallet = payer.wallet.first()
            if not wallet or wallet.balance <= 0:
                logger.warning(f"Usuário {self.user.email} sem saldo para a ação paga '{self.dzaion_action.verb_code}'.")
                raise InsufficientFundsForAIError(f"Saldo insuficiente para executar a ação: {self.dzaion_action.name}.")
        logger.debug("Verificação de saldo OK.")

    def _execute_llm_interaction(self) -> dict:
        logger.info(f"Fase 4: Executando interação com LLM (Missão: {self.mission_type}).")
        
        system_prompt = self._build_system_prompt()
        conversation_history = self._load_conversation_history() # Carrega histórico específico
        messages = [{"role": "system", "content": system_prompt}] + conversation_history

        if self.mission_type == 'REACTIVE':
            user_message = self.trigger_info.get('message_body')
            self._save_message(user_message, 'INBOUND')
            messages.append({"role": "user", "content": user_message})

        tools = self._build_tools()

        logger.debug(f"Iniciando 1ª chamada à IA. Missão: {self.mission_type}.")
        response_data = self.client.generate_response(
            model=self.ai_model.identifier,
            messages=messages,
            tools=tools,
            service_tier=self.service_tier
        )
        self._update_total_usage(response_data['usage'])
        response_message = response_data['message']
        messages.append(response_message.model_dump()) 

        final_text = response_message.content or "" 

        if response_message.tool_calls:
            logger.info("IA solicitou a execução de ferramentas.")
            tool_execution_status = "success"

            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_function = TOOL_REGISTRY.get(tool_name)
                
                if tool_function:
                    tool_args = json.loads(tool_call.function.arguments)
                    logger.info(f"Ferramenta '{tool_name}' solicitada com argumentos: {tool_args}")
                    
                    try:
                        service_args = tool_args.copy()
                        service_args['user_id'] = str(self.user.id)
                        
                        tool_result = tool_function(**service_args)
                        
                        if tool_result.get("status") == "error":
                            tool_execution_status = "error"
                            
                        result_content = json.dumps(tool_result)
                        logger.info(f"Ferramenta '{tool_name}' executada. Resultado: {result_content}")
                    except Exception as e:
                        logger.error(f"Erro ao executar a ferramenta '{tool_name}': {e}", exc_info=True)
                        tool_execution_status = "error"
                        result_content = json.dumps({"status": "error", "message": f"Erro interno: {str(e)}"})
                    
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": tool_name, "content": result_content})

            logger.debug("Iniciando 2ª chamada à IA (com resultados da ferramenta).")
            final_response_data = self.client.generate_response(
                model=self.ai_model.identifier, 
                messages=messages, 
                service_tier=self.service_tier
            )
            self._update_total_usage(final_response_data['usage'])
            final_text = final_response_data['message'].content
            
            if tool_execution_status == "success":
                logger.info("Ferramenta executada com sucesso. Finalizando processo.")
                self.thought_process.status = AIThoughtProcess.ProcessStatus.FINISHED
                self.conversation.status = Conversation.ConversationStatus.FINISHED
            else:
                logger.info("Ferramenta falhou. Solicitando nova resposta do usuário.")
                self.thought_process.status = AIThoughtProcess.ProcessStatus.PENDING_USER_RESPONSE
        else:
            logger.debug("IA não solicitou ferramentas. Resposta de texto direto.")
            if self.mission_type == 'PROACTIVE':
                self.thought_process.status = AIThoughtProcess.ProcessStatus.PENDING_USER_RESPONSE
        
        self.thought_process.save()
        self.conversation.save()
        self._save_message(final_text, 'OUTBOUND')
        return {'text': final_text, 'usage': self.total_usage}

    def _build_system_prompt(self) -> str:
        general_instructions = render_to_string('prompts/general.txt')
        user_context = render_to_string('prompts/user_context.txt', {'user': self.user})
        return f"{general_instructions}\n\n{user_context}\n\n{self.dzaion_action.instructions}"

    def _build_tools(self) -> list:
        if self.dzaion_action and self.dzaion_action.parameters_schema:
            return [{"type": "function", "function": {"name": self.dzaion_action.verb_code, "description": self.dzaion_action.name, "parameters": self.dzaion_action.parameters_schema}}]
        return []

    def _load_conversation_history(self, limit: int = None) -> list:
        if not self.conversation: return []
        
        messages_qs = self.conversation.messages.all().order_by('-created_at')
        if limit:
            messages_qs = messages_qs[:limit]
            
        history = []
        for msg in reversed(messages_qs):
            role = "user" if msg.direction == 'INBOUND' else "assistant"
            history.append({"role": role, "content": msg.content})
        
        logger.info(f"Carregado {len(history)} mensagens do histórico da conversa {self.conversation.id}.")
        return history

    def _save_message(self, content: str, direction: str, status: str = 'SENT'):
        if not content: return
        Message.objects.create(
            conversation=self.conversation,
            direction=direction,
            content=content,
            status=status
        )
        logger.info(f"Mensagem '{direction}' salva na conversa {self.conversation.id}.")

    def _update_total_usage(self, usage_data: dict):
        self.total_usage['input_tokens'] += usage_data.get('input_tokens', 0)
        self.total_usage['output_tokens'] += usage_data.get('output_tokens', 0)

    def _log_token_usage(self):
        if not self.dzaion_action: return
        logger.info(f"Fase 5: Registrando uso de tokens: {self.total_usage}")
        try:
            DzaionService.log_token_usage(
                dzaion_action=self.dzaion_action, user=self.user, ai_model=self.ai_model,
                input_tokens=self.total_usage.get('input_tokens', 0), output_tokens=self.total_usage.get('output_tokens', 0),
                tenant_context=self.tenant_context,
            )
        except Exception as e:
            logger.error(f"Falha ao registrar o uso de tokens: {e}", exc_info=True)

    def _dispatch_response(self, response_text: str):
        logger.info(f"Fase 6: Enviando resposta: '{response_text}'")
        if not response_text: 
            logger.warning("Nenhum texto de resposta para enviar.")
            return
        try:
            dispatcher = get_dispather_service()
            dispatcher.send_text_message(to_number=self.user.whatsapp, message=response_text)
            logger.info("Resposta enviada com sucesso.")
        except Exception as e:
            logger.error(f"Falha ao enviar resposta via dispatcher: {e}", exc_info=True)

