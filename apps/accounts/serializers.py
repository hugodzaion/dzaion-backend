# -*- coding: utf-8 -*-
"""
Módulo de Serializers para o App 'accounts'.

Author: Dzaion
Version: 0.5.0
"""
from datetime import timedelta
from django.contrib.auth import authenticate
from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer de autenticação que assume controle total do fluxo de login
    para fornecer mensagens de erro precisas e estruturadas.
    """
    def validate(self, attrs):
        email_or_whatsapp = attrs.get(self.username_field)
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email_or_whatsapp,
            password=password
        )

        if user is None:
            # DZAION-UPDATE: Padronizando a resposta de erro genérica.
            error_detail = {
                "error_code": "invalid_credentials",
                "message": "Usuário e/ou senha incorreto(s)"
            }
            raise AuthenticationFailed(error_detail)

        if not user.is_active:
            # DZAION-UPDATE: Implementando a resposta de erro estruturada e profissional.
            error_detail = {
                "error_code": "account_not_active",
                "message": "Esta conta está desativada. Por favor, realize a ativação.",
                "context": {
                    "email": user.email
                }
            }
            raise AuthenticationFailed(error_detail)
        
        self.user = user
        
        remember_me = self.context['request'].data.get('rememberMe', False)
        refresh = RefreshToken.for_user(self.user)
        if remember_me:
            refresh.set_exp(lifetime=timedelta(days=180))
        else:
            refresh.set_exp(lifetime=api_settings.REFRESH_TOKEN_LIFETIME)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        return data


# ... (o resto do arquivo permanece o mesmo) ...

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para o registro de novos usuários no sistema.
    """
    email = serializers.EmailField(help_text="Endereço de e-mail único. Será usado para login.")
    name = serializers.CharField(help_text="Nome completo do usuário (nome e sobrenome).")
    whatsapp = serializers.CharField(help_text="Número de WhatsApp no formato internacional E.164.")
    cpf = serializers.CharField(help_text="CPF do usuário, apenas números.")
    password = serializers.CharField(label="Senha", write_only=True, help_text="Senha de acesso.")
    confirm_password = serializers.CharField(label="Confirmação de Senha", write_only=True, required=True, help_text="Repita a senha.")

    class Meta:
        model = User
        fields = ['id', 'name', 'gender', 'date_birth', 'email', 'whatsapp', 'cpf', 'password', 'confirm_password']
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'As senhas não coincidem.'})
        password_validation.validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.full_clean()
        user.save()
        return user


class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['photo']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'nickname', 'gender', 'date_birth']


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("A senha atual está incorreta.")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': "A nova senha e a confirmação não coincidem."})
        password_validation.validate_password(data['new_password'])
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'nickname', 'email', 'whatsapp', 'age', 'gender', 'date_birth', 'photo_url', 'is_superuser']
        read_only_fields = fields

    def get_photo_url(self, user):
        request = self.context.get('request')
        if user.photo and request:
            return request.build_absolute_uri(user.photo.url)
        return None

