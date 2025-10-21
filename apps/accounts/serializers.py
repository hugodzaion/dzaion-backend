# -*- coding: utf-8 -*-
"""
Módulo de Serializers para o App 'accounts'.

Author: Dzaion
Version: 1.4.0
"""
from datetime import timedelta
from django.contrib.auth import authenticate
from django.contrib.auth import password_validation
from django.contrib.auth.models import Permission
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from finances.models import Wallet
from guards.services import GuardService
from finances.serializers import WalletSummarySerializer


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para exibir os detalhes de um usuário com informações contextuais.
    """
    photo_url = serializers.SerializerMethodField()
    age = serializers.IntegerField(read_only=True)
    
    global_permissions = serializers.SerializerMethodField()
    personal_wallet = serializers.SerializerMethodField()
    tenants = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'nickname', 'email', 'whatsapp', 'age', 'gender',
            'date_birth', 'photo_url', 'is_staff', 
            'global_permissions', 'personal_wallet', 'tenants'
        ]
        read_only_fields = fields

    def get_photo_url(self, user):
        request = self.context.get('request')
        if user.photo and request:
            return request.build_absolute_uri(user.photo.url)
        return None

    def get_global_permissions(self, user: User) -> list[str]:
        """
        Retorna apenas as permissões que o usuário possui em um contexto global.
        """
        if user.is_superuser:
            return sorted([
                f"{p.content_type.app_label}.{p.codename}"
                for p in Permission.objects.all()
            ])

        global_roles = user.roles.filter(tenant__isnull=True)
        permissions_from_roles = Permission.objects.filter(role__in=global_roles)
        direct_permissions = user.user_permissions.all()
        
        all_perms = (permissions_from_roles | direct_permissions).distinct().select_related('content_type')
        
        return sorted([f"{p.content_type.app_label}.{p.codename}" for p in all_perms])

    def get_personal_wallet(self, user: User) -> dict | None:
        """Retorna a carteira pessoal do usuário."""
        wallet = user.wallet.first()
        if wallet:
            return WalletSummarySerializer(wallet).data
        return None

    def get_tenants(self, user: User) -> list[dict]:
        """
        Retorna uma lista dos Tenants aos quais o usuário é membro, incluindo
        as permissões e carteiras contextuais de cada um.
        """
        from tenants.serializers import TenantDetailForUserSerializer
        from tenants.models import Tenant

        tenant_ids = user.memberships.filter(status='ACTIVE').values_list('tenant_id', flat=True)
        tenants_qs = Tenant.objects.filter(id__in=list(tenant_ids))

        context = self.context.copy()
        context['user'] = user
        
        return TenantDetailForUserSerializer(tenants_qs, many=True, context=context).data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer de autenticação que retorna o objeto completo do usuário.
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
            error_detail = {
                "error_code": "invalid_credentials",
                "message": "Usuário e/ou senha incorreto(s)"
            }
            raise AuthenticationFailed(error_detail)

        if not user.is_active:
            error_detail = {
                "error_code": "account_not_active",
                "message": "Esta conta está desativada. Por favor, realize a ativação.",
                "context": { "email": user.email }
            }
            raise AuthenticationFailed(error_detail)
        
        self.user = user
        
        remember_me = self.context['request'].data.get('rememberMe', False)
        refresh = RefreshToken.for_user(self.user)
        if remember_me:
            refresh.set_exp(lifetime=timedelta(days=180))
        else:
            refresh.set_exp(lifetime=api_settings.REFRESH_TOKEN_LIFETIME)

        user_data = UserDetailSerializer(self.user, context=self.context).data
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data
        }
        
        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer para o registro de novos usuários."""
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

    # DZAION-UX: Adicionando validações de unicidade com mensagens claras.
    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Já existe uma conta cadastrada com este e-mail.")
        return value

    def validate_whatsapp(self, value):
        # A normalização do WhatsApp acontece no método `clean` do modelo.
        # Aqui, apenas verificamos a existência.
        if User.objects.filter(whatsapp=value).exists():
            raise serializers.ValidationError("Já existe uma conta cadastrada com este número de WhatsApp.")
        return value

    def validate_cpf(self, value):
        if User.objects.filter(cpf=value).exists():
            raise serializers.ValidationError("Já existe uma conta cadastrada com este CPF.")
        return value

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
        # O método full_clean irá executar as normalizações (ex: whatsapp) antes de salvar.
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

