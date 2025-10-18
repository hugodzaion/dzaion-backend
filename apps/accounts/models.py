# -*- coding: utf-8 -*-
"""
Módulo de Modelos para o App 'accounts'.

Este módulo define as estruturas de dados centrais para o gerenciamento de
usuários e autenticação no sistema. A principal entidade é o modelo `User`,
que é uma implementação customizada do usuário padrão do Django.

Models:
    UserManager: Gerenciador que provê métodos auxiliares para criação de usuários.
    User: Modelo principal que representa um usuário no ecossistema.

Author: Dzaion
Version: 0.1.0
"""
from __future__ import annotations
import re
from datetime import date

import phonenumbers
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# DZAION-REVIEW: Importado o BaseModel para padronização.
from core.models import BaseModel
from .storages import user_directory_path
from .validators import validate_cpf


class UserManager(BaseUserManager):
    """
    Gerenciador customizado para o modelo User.

    Sobrescreve os métodos padrão para garantir que a criação de usuários
    siga as regras de negócio específicas da aplicação, como a exigência
    de email, nome, CPF e WhatsApp.
    """

    # DZAION-REVIEW: Adicionado **extra_fields para flexibilidade, alinhando ao padrão do Django.
    def create_user(self, email: str, whatsapp: str, name: str, cpf: str, password: str | None = None, **extra_fields) -> "User":
        """
        Cria e salva um novo usuário padrão com as informações fornecidas.

        :param email: Endereço de e-mail do usuário (login).
        :param whatsapp: Número de WhatsApp.
        :param name: Nome completo do usuário.
        :param cpf: CPF do usuário.
        :param password: Senha do usuário.
        :param extra_fields: Campos adicionais para o modelo User.
        :return: A instância do objeto User criado.
        :raises ValueError: Se campos obrigatórios não forem fornecidos.
        """
        if not email:
            raise ValueError("O campo de email é obrigatório")
        if not whatsapp:
            raise ValueError("O campo de whatsapp é obrigatório")
        if not name:
            raise ValueError("O campo de nome é obrigatório")
        if not cpf:
            raise ValueError("O campo de cpf é obrigatório")

        email = self.normalize_email(email)
        # DZAION-REVIEW: 'is_active' agora é um extra_field com default False.
        extra_fields.setdefault('is_active', False)
        
        user = self.model(
            email=email,
            whatsapp=whatsapp,
            name=name,
            cpf=cpf,
            **extra_fields
        )
        user.set_password(password)
        user.full_clean()  # Executa todas as validações do modelo
        user.save(using=self._db)
        return user

    # DZAION-REVIEW: Simplificado usando **extra_fields.
    def create_superuser(self, email: str, name: str, cpf: str, whatsapp: str, password: str | None = None, **extra_fields) -> "User":
        """
        Cria e salva um novo superusuário com poderes de administrador.

        :return: A instância do objeto User criado como superusuário.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(
            email=email,
            name=name,
            cpf=cpf,
            whatsapp=whatsapp,
            password=password,
            **extra_fields
        )


# DZAION-REVIEW: Alterado para herdar de BaseModel.
class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Representa um usuário individual no sistema.

    Este modelo customizado substitui o usuário padrão do Django, utilizando
    o e-mail como identificador único para autenticação.
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
        help_text="Apelido ou primeiro nome. Gerado automaticamente se não for fornecido."
    )
    gender = models.CharField(
        verbose_name='Gênero',
        max_length=10,
        choices=GENDER_CHOICES,
        null=True, blank=True,
        help_text="Gênero do usuário."
    )
    cpf = models.CharField(
        verbose_name='CPF',
        max_length=11,
        unique=True,
        validators=[validate_cpf],
        help_text="Cadastro de Pessoa Física (CPF), apenas números."
    )
    date_birth = models.DateField(
        verbose_name='Data de Nascimento',
        null=True, blank=True,
        help_text="Data de nascimento no formato AAAA-MM-DD."
    )
    photo = models.ImageField(
        verbose_name='Foto de Perfil',
        upload_to=user_directory_path,
        blank=True, null=True,
        help_text="Foto de perfil do usuário. Será armazenada em um diretório único."
    )

    # --- Campos de Contato e Verificação ---
    email = models.EmailField(
        verbose_name='E-mail',
        unique=True,
        help_text="Endereço de e-mail principal. Utilizado para login e comunicação."
    )
    email_verified_at = models.DateTimeField(
        verbose_name='E-mail Verificado em',
        null=True, blank=True,
        help_text="Timestamp de quando o e-mail do usuário foi verificado/ativado."
    )
    whatsapp = models.CharField(
        verbose_name='WhatsApp (E.164)',
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Número de WhatsApp no formato internacional E.164 (ex: +5538999998888)."
    )
    whatsapp_verified_at = models.DateTimeField(
        verbose_name='Whatsapp verificado em',
        null=True, blank=True,
        help_text="Timestamp de quando o WhatsApp do usuário foi verificado."
    )

    # --- Campos de Status e Permissão ---
    is_superuser = models.BooleanField(
        verbose_name='Superusuário',
        default=False,
        help_text="Designa que este usuário tem todas as permissões sem atribuí-las explicitamente."
    )
    is_staff = models.BooleanField(
        verbose_name='Membro da Equipe',
        default=False,
        help_text="Designa se o usuário pode fazer login no site de administração."
    )
    is_active = models.BooleanField(
        verbose_name='Ativo',
        default=False,
        help_text="Designa se este usuário deve ser tratado como ativo. Desmarque em vez de excluir contas."
    )
    # DZAION-REVIEW: Removido 'date_joined' pois 'created_at' do BaseModel o substitui.
    # date_joined = models.DateTimeField(...)

    # --- Configurações do Modelo ---
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'cpf', 'whatsapp']
    objects = UserManager()

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        # DZAION-REVIEW: Ordenação atualizada para usar o campo do BaseModel.
        ordering = ['-created_at']

    # --- Métodos de Instância ---
    def save(self, *args, **kwargs):
        """Sobrescreve o método save para gerar um apelido automaticamente."""
        if self.name and not self.nickname:
            self.nickname = self.name.strip().split()[0]
        super().save(*args, **kwargs)

    def clean(self):
        """Executa a limpeza e validação dos dados antes de salvar."""
        super().clean()
        
        # Normalização do CPF
        if self.cpf:
            self.cpf = ''.join(filter(str.isdigit, self.cpf))
        
        # Validação do Nome Completo
        if self.name and len(self.name.strip().split()) < 2:
            raise ValidationError(
                {"name": "Por favor, informe o nome completo (nome e sobrenome)."}
            )
        
        # DZAION-REVIEW: Adicionada normalização e validação robusta para o WhatsApp.
        if self.whatsapp:
            try:
                # Normaliza removendo não-dígitos, exceto o '+' inicial se houver.
                cleaned_whatsapp = re.sub(r'[^\d+]', '', self.whatsapp)
                if not cleaned_whatsapp.startswith('+'):
                    # Assume DDI do Brasil se não especificado
                    cleaned_whatsapp = f"+55{cleaned_whatsapp}"

                parsed_phone = phonenumbers.parse(cleaned_whatsapp, None)
                if not phonenumbers.is_valid_number(parsed_phone):
                    raise ValidationError({"whatsapp": "O número de WhatsApp informado não é válido."})
                
                # Armazena no formato E.164
                self.whatsapp = phonenumbers.format_number(
                    parsed_phone, phonenumbers.PhoneNumberFormat.E164
                )
            except phonenumbers.phonenumberutil.NumberParseException as e:
                raise ValidationError({"whatsapp": f"Formato do número de WhatsApp inválido: {e}"})


    # --- Propriedades Computadas ---
    @property
    def parsed_phone(self) -> phonenumbers.PhoneNumber | None:
        """
        Propriedade interna para parsear o número uma única vez (cache).
        Retorna um objeto `phonenumber` ou `None`.
        """
        if not hasattr(self, '_parsed_phone'):
            try:
                self._parsed_phone = phonenumbers.parse(self.whatsapp, None)
            except phonenumbers.phonenumberutil.NumberParseException:
                self._parsed_phone = None
        return self._parsed_phone

    @property
    def formatted_whatsapp(self) -> str:
        """
        Formata o número para o padrão NACIONAL do país.
        Exemplo para o Brasil: `(38) 99926-1992`.
        """
        if self.parsed_phone and phonenumbers.is_valid_number(self.parsed_phone):
            return phonenumbers.format_number(
                self.parsed_phone, phonenumbers.PhoneNumberFormat.NATIONAL
            )
        return self.whatsapp

    @property
    def international_whatsapp(self) -> str:
        """
        Formata o número para o padrão INTERNACIONAL.
        Exemplo: `+55 38 99926-1992`.
        """
        if self.parsed_phone and phonenumbers.is_valid_number(self.parsed_phone):
            return phonenumbers.format_number(
                self.parsed_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
        return self.whatsapp
    
    @property
    def age(self) -> int | None:
        """Calcula e retorna a idade atual do usuário em anos."""
        if self.date_birth:
            return relativedelta(timezone.now().date(), self.date_birth).years
        return None

    def __str__(self) -> str:
        """Representação em string do objeto User."""
        return self.name or self.email

