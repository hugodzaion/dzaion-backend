# -*- coding: utf-8 -*-
"""
Módulo de Serializers para o App 'accounts'.

Este módulo define os "contratos de dados" (schemas) para a API de contas,
controlando como os dados são validados, convertidos e representados em JSON.

Author: Dzaion
Version: 1.1.0
"""
from datetime import timedelta

from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer de autenticação customizado.
    """

    def validate(self, attrs):
        """
        Valida as credenciais e customiza o tempo de vida do token.
        """
        remember_me = self.context['request'].data.get('rememberMe', False)
        data = super().validate(attrs)

        if not self.user.is_active:
            raise AuthenticationFailed("Esta conta está desativada. Contate o administrador.")

        refresh = RefreshToken.for_user(self.user)
        if remember_me:
            refresh.set_exp(lifetime=timedelta(days=180))
        else:
            refresh.set_exp(lifetime=api_settings.REFRESH_TOKEN_LIFETIME)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para o registro de novos usuários no sistema.
    """
    email = serializers.EmailField(
        help_text="Endereço de e-mail único. Será usado para login."
    )
    name = serializers.CharField(
        help_text="Nome completo do usuário (nome e sobrenome)."
    )
    whatsapp = serializers.CharField(
        help_text="Número de WhatsApp no formato internacional E.164 (ex: +5538999998888)."
    )
    cpf = serializers.CharField(
        help_text="CPF do usuário, apenas números."
    )
    password = serializers.CharField(
        label="Senha",
        write_only=True,
        help_text="Senha de acesso. Mínimo de 8 caracteres."
    )
    confirm_password = serializers.CharField(
        label="Confirmação de Senha",
        write_only=True,
        required=True,
        help_text="Repita a senha para confirmação."
    )

    class Meta:
        model = User
        fields = [
            'id', 'name', 'gender', 'date_birth', 'email', 'whatsapp',
            'cpf', 'password', 'confirm_password'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {'confirm_password': 'As senhas não coincidem.'}
            )
        password_validation.validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserPhotoSerializer(serializers.ModelSerializer):
    """Serializer específico para o upload da foto de perfil do usuário."""
    class Meta:
        model = User
        fields = ['photo']
        extra_kwargs = {
            'photo': {'help_text': 'Arquivo de imagem para o perfil do usuário.'}
        }


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para o processo de alteração de senha de um usuário autenticado.
    """
    current_password = serializers.CharField(
        label="Senha Atual",
        required=True,
        write_only=True,
        help_text="A senha atual do usuário para verificação."
    )
    new_password = serializers.CharField(
        label="Nova Senha",
        required=True,
        write_only=True,
        min_length=8,
        help_text="A nova senha desejada."
    )
    confirm_password = serializers.CharField(
        label="Confirmação da Nova Senha",
        required=True,
        write_only=True,
        help_text="Repita a nova senha para confirmação."
    )

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("A senha atual está incorreta.")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {'confirm_password': "A nova senha e a confirmação não coincidem."}
            )
        password_validation.validate_password(data['new_password'])
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para exibir os detalhes de um usuário.
    """
    photo_url = serializers.SerializerMethodField(
        help_text="URL completa da foto de perfil do usuário."
    )
    age = serializers.IntegerField(
        read_only=True,
        help_text="Idade atual do usuário em anos."
    )

    class Meta:
        model = User
        # DZAION-REVIEW: Adicionado 'gender' e 'date_birth' para um perfil mais completo.
        fields = [
            'id', 'name', 'nickname', 'email', 'whatsapp', 'age', 'gender',
            'date_birth', 'photo_url', 'is_superuser'
        ]
        read_only_fields = fields

    def get_photo_url(self, user):
        request = self.context.get('request')
        if user.photo and request:
            return request.build_absolute_uri(user.photo.url)
        return None
