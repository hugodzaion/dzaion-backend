# -*- coding: utf-8 -*-
"""
Registro Central de Ferramentas (Tools) da IA.

Este arquivo mapeia os `verb_codes` das DzaionActions para os métodos
de serviço reais que os executam. É a "ponte" entre a decisão da IA
e a execução no nosso backend.

Author: Dzaion
Version: 0.2.0
"""
from accounts.services import AccountService

# O Orquestrador usará este dicionário para saber qual função chamar
# com base no 'name' do tool_call retornado pela OpenAI.
TOOL_REGISTRY = {
    'activate_user': AccountService.activate_user,
    # Exemplo futuro:
    # 'send_invoice_reminder': FinanceService.send_invoice_reminder,
}

