# -*- coding: utf-8 -*-
"""
Módulo de Modelos para o App 'accounts'.

Author: Dzaion
Version: 1.3.0
"""
from __future__ import annotations
import re
from typing import Self
from datetime import date

import phonenumbers
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from .storages import user_directory_path
from .validators import validate_cpf


class UserManager(BaseUserManager):
    """
    Gerenciador customizado para o modelo User.
    """

    def create_user(self, password: str | None = None, **extra_fields: any) -> Self:
        """
        Cria e salva um novo usuário padrão com as informações fornecidas.
        """
        if not extra_fields.get('email'):
            raise ValueError("O campo de email é obrigatório")

        email = self.normalize_email(extra_fields.pop('email'))
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, password: str | None = None, **extra_fields: any) -> Self:
        """
        Cria e salva um novo superusuário com poderes de administrador.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário deve ter is_superuser=True.')

        return self.create_user(password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Representa um usuário individual no sistema.
    """
    GENDER_CHOICES = [
        ('male', 'Masculino'),
        ('female', 'Feminino'),
    ]

    # --- Campos de Identificação ---
    name = models.CharField(
        verbose_name='Nome Completo',
        max_length=100,
        help_text="Nome e sobrenome do usuário."
    )
    nickname = models.CharField(
        verbose_name='Apelido',
        max_length=100,
        null=True, blank=True,
        help_text="Apelido ou primeiro nome."
    )
    gender = models.CharField(
        verbose_name='Gênero',
        max_length=10,
        choices=GENDER_CHOICES,
        null=True, blank=True
    )
    cpf = models.CharField(
        verbose_name='CPF',
        max_length=11,
        unique=True,
        validators=[validate_cpf],
        help_text="CPF, apenas números."
    )
    date_birth = models.DateField(
        verbose_name='Data de Nascimento',
        null=True, blank=True,
        help_text="Formato AAAA-MM-DD."
    )
    photo = models.ImageField(
        verbose_name='Foto de Perfil',
        upload_to=user_directory_path,
        blank=True, null=True
    )

    # --- Campos de Contato e Verificação ---
    email = models.EmailField(
        verbose_name='E-mail',
        unique=True,
        help_text="Utilizado para login e comunicação."
    )
    email_verified_at = models.DateTimeField(
        verbose_name='E-mail Verificado em',
        null=True, blank=True
    )
    whatsapp = models.CharField(
        verbose_name='WhatsApp (E.164)',
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Formato internacional E.164 (ex: +5538999998888)."
    )
    whatsapp_verified_at = models.DateTimeField(
        verbose_name='Whatsapp verificado em',
        null=True, blank=True
    )

    roles = models.ManyToManyField(
        'guards.Role',
        blank=True,
        related_name='users',
        verbose_name='Papéis Globais',
        help_text='Papéis globais atribuídos diretamente a este usuário.'
    )

    # --- Campos de Status e Permissão ---
    is_staff = models.BooleanField(
        verbose_name='Membro da Equipe',
        default=False,
        help_text="Designa se o usuário pode fazer login no site de administração."
    )
    is_active = models.BooleanField(
        verbose_name='Ativo',
        default=False,
        help_text="Designa se este usuário deve ser tratado como ativo."
    )

    # --- Configurações do Modelo ---
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'cpf', 'whatsapp']
    objects = UserManager()

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.name and not self.nickname:
            self.nickname = self.name.strip().split()[0]
        super().save(*args, **kwargs)

    def clean(self: Self):
        super().clean()
        if self.cpf:
            self.cpf = ''.join(filter(str.isdigit, self.cpf))
        if self.name and len(self.name.strip().split()) < 2:
            raise ValidationError(
                {"name": "Por favor, informe o nome completo (nome e sobrenome)."}
            )
        if self.whatsapp:
            try:
                cleaned_whatsapp = re.sub(r'[^\d+]', '', self.whatsapp)
                if not cleaned_whatsapp.startswith('+'):
                    cleaned_whatsapp = f"+55{cleaned_whatsapp}"

                parsed_phone = phonenumbers.parse(cleaned_whatsapp, None)
                if not phonenumbers.is_valid_number(parsed_phone):
                    raise ValidationError({"whatsapp": "O número de WhatsApp não é válido."})

                self.whatsapp = phonenumbers.format_number(
                    parsed_phone, phonenumbers.PhoneNumberFormat.E164
                )
            except phonenumbers.phonenumberutil.NumberParseException:
                raise ValidationError({"whatsapp": "Formato do número de WhatsApp inválido."})

    # --- Propriedades Computadas ---
    @property
    def _parsed_phone(self):
        if not hasattr(self, '__parsed_phone'):
            try:
                self.__parsed_phone = phonenumbers.parse(self.whatsapp, None)
            except phonenumbers.phonenumberutil.NumberParseException:
                self.__parsed_phone = None
        return self.__parsed_phone

    # DZAION-REFACTOR: Propriedade auxiliar para evitar código repetido.
    @property
    def _is_valid_phone(self) -> bool:
        return self._parsed_phone and phonenumbers.is_valid_number(self._parsed_phone)

    @property
    def formatted_whatsapp(self):
        """Formata o número para o padrão NACIONAL do país."""
        if self._is_valid_phone:
            return phonenumbers.format_number(
                self._parsed_phone, phonenumbers.PhoneNumberFormat.NATIONAL
            )
        return self.whatsapp

    @property
    def international_whatsapp(self):
        """Formata o número para o padrão INTERNACIONAL."""
        if self._is_valid_phone:
            return phonenumbers.format_number(
                self._parsed_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
        return self.whatsapp
    
    @property
    def age(self):
        if self.date_birth:
            return relativedelta(timezone.now().date(), self.date_birth).years
        return None

    def __str__(self):
        return self.name or self.email

