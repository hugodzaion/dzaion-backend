"""
file_cleanup.py
----------------
Utilitário para remover automaticamente arquivos antigos ou órfãos do sistema de arquivos
quando um novo arquivo é salvo ou quando o objeto é deletado.

Uso:
1. Importe o signal no seu AppConfig (apps.py) do app.
2. Funciona automaticamente em qualquer model com campos FileField ou ImageField.
"""

import os
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.db import models


def delete_file(path):
    """Remove arquivo físico se existir."""
    if path and os.path.isfile(path):
        os.remove(path)


@receiver(pre_save)
def auto_delete_old_file_on_change(sender, instance, **kwargs):
    """
    Antes de salvar um objeto, verifica se algum FileField foi substituído.
    Se sim, remove o arquivo antigo do disco.
    """
    if not issubclass(sender, models.Model):
        return
    if not instance.pk:
        return  # só atua em updates

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    for field in instance._meta.get_fields():
        if isinstance(field, (models.FileField, models.ImageField)):
            old_file = getattr(old_instance, field.name)
            new_file = getattr(instance, field.name)
            if old_file and old_file != new_file:
                delete_file(old_file.path)


@receiver(post_delete)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Após deletar um objeto, remove os arquivos associados do disco.
    """
    if not issubclass(sender, models.Model):
        return

    for field in instance._meta.get_fields():
        if isinstance(field, (models.FileField, models.ImageField)):
            file_field = getattr(instance, field.name)
            if file_field:
                delete_file(file_field.path)
