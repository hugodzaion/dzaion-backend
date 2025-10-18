class UserActivityExeption(Exception):
    """Capitura todos os erros relacionados com user activity"""
    pass

class IncompleteDataUserActivityExeption(UserActivityExeption):
    """Capituras dados inclompletos para a criação da atividade do usuário"""
    pass

class PriorityUserActivityExeption(UserActivityExeption):
    """Captura erro no campo de prioridade"""
    def __init__(self, invalid_priority_value, valid_choices):
        message = {
            f"O valor da prioridade '{invalid_priority_value}' não é válido."
            f"Os valores válidos são: {', '.join(valid_choices)}"
        }
        super().__init__(message)