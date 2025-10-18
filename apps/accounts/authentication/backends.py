# DZAION-REVIEW: Adicionado re e phonenumbers para normalização
import re
import phonenumbers
from django.contrib.auth.backends import ModelBackend
# DZAION-REVIEW: Alterado para importação direta para melhor suporte da IDE.
# from django.contrib.auth import get_user_model
from django.db.models import Q
from accounts.models import User

# User = get_user_model()

class EmailOrWhatsAppBackend(ModelBackend):
    # DZAION-REVIEW: Type hint corrigido com a importação direta.
    def authenticate(self, request, username: str | None = None, password: str | None = None, **kwargs) -> User | None:
        """
        Autentica um usuário usando e-mail ou número de WhatsApp.

        Normaliza o `username` se ele se parece com um número de telefone para
        garantir consistência com o formato E.164 armazenado no banco de dados.
        """
        if username is None:
            return None

        # DZAION-REVIEW: Lógica de normalização do WhatsApp adicionada, espelhando o model.
        # Se o `username` contém dígitos e pode ser um telefone, normaliza-o.
        if any(char.isdigit() for char in username) and not '@' in username:
            try:
                cleaned_whatsapp = re.sub(r'[^\d+]', '', username)
                if not cleaned_whatsapp.startswith('+'):
                    cleaned_whatsapp = f"+55{cleaned_whatsapp}"

                parsed_phone = phonenumbers.parse(cleaned_whatsapp, None)
                if phonenumbers.is_valid_number(parsed_phone):
                    username = phonenumbers.format_number(
                        parsed_phone, phonenumbers.PhoneNumberFormat.E164
                    )
            except phonenumbers.phonenumberutil.NumberParseException:
                # Se a normalização falhar, prossegue com o valor original.
                pass
        
        # DZAION-REVIEW: Bloco try/except corrigido para envolver toda a lógica e evitar UnboundLocalError.
        try:
            user = User.objects.get(Q(email__iexact=username) | Q(whatsapp=username))
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            # Retorna None para indicar falha na autenticação, como esperado pelo Django.
            return None
        return None

