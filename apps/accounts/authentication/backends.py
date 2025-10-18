# -*- coding: utf-8 -*-
"""
Módulo de Backend de Autenticação Customizado.

Author: Dzaion
Version: 0.3.0
"""
from __future__ import annotations
import re
import phonenumbers
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from accounts.models import User

class EmailOrWhatsAppBackend(ModelBackend):
    def authenticate(self, request, username: str | None = None, password: str | None = None, **kwargs) -> User | None:
        """
        Autentica um usuário usando e-mail ou número de WhatsApp.
        Sua única responsabilidade é validar as credenciais. A verificação de status
        do usuário é delegada para as camadas superiores (serializers).
        """
        login_identifier = kwargs.get(User.USERNAME_FIELD) or username
        
        if not login_identifier or not password:
            return None

        normalized_identifier = login_identifier
        
        if any(char.isdigit() for char in login_identifier) and '@' not in login_identifier:
            try:
                cleaned_phone = re.sub(r'[^\d+]', '', login_identifier)
                if not cleaned_phone.startswith('+'):
                    cleaned_phone = f"+55{cleaned_phone}"

                parsed_phone = phonenumbers.parse(cleaned_phone, None)
                if phonenumbers.is_valid_number(parsed_phone):
                    normalized_identifier = phonenumbers.format_number(
                        parsed_phone, phonenumbers.PhoneNumberFormat.E164
                    )
            except phonenumbers.phonenumberutil.NumberParseException:
                pass
        
        try:
            user = User.objects.get(
                Q(email__iexact=normalized_identifier) | Q(whatsapp=normalized_identifier)
            )
            
            # Retorna o usuário se a senha estiver correta, mesmo que ele esteja inativo.
            if user.check_password(password):
                return user
                
        except User.DoesNotExist:
            return None
            
        # Retorna None se a senha estiver incorreta.
        return None

