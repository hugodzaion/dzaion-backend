import uuid
from django.db import models

class TimestampedModel(models.Model):
    """
    Um modelo abstrato que fornece campos de data de criação e atualização.
    `auto_now_add`: Define o timestamp na criação do objeto.
    `auto_now`: Atualiza o timestamp toda vez que o objeto é salvo.
    """
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        abstract = True

class BaseModel(TimestampedModel):
    """
    Modelo base para todos os outros modelos do projeto.
    Herda os timestamps e adiciona um UUID como chave primária.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
        