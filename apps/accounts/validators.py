from validate_docbr import CPF
from django.core.exceptions import ValidationError

# validados de CPF
def validate_cpf(value):
    cpf = CPF()
    if not cpf.validate(value):
        raise ValidationError({"cpf":"CPF inválido. Insira um CPF válido com 11 dígitos."})