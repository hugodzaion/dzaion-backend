from django.db import models

class ChannelContacts(models.Model):
    name = models.CharField('Nome do Canal', max_length=50)
    icon = models.CharField('Ícone', max_length=50)

    def __str__(self):
        return f"Canal de Contato: {self.name}"