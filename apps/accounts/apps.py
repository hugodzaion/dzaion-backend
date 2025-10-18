from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Contas de Usuário'

    def ready(self):
        # Méto global de limpeza de arquivos
        from apps.core.utils import file_cleanup