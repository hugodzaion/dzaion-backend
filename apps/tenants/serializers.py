# -*- coding: utf-8 -*-
"""
Módulo de Serializers para o App 'tenants'.

Author: Dzaion
Version: 1.1.0
"""
from rest_framework import serializers
from .models import Tenant, TenantContact, TenantMembership, TenantLinkRequest
from accounts.models import User
from accounts.serializers import UserDetailSerializer
from locations.models import Location
from contacts.serializers import ChannelContactsSerializer
from contacts.models import ChannelContacts
from guards.models import Role
from finances.serializers import WalletSummarySerializer


# --- Serializers para Leitura (GET) ---

class TenantContactSerializer(serializers.ModelSerializer):
    """Serializer para exibir os detalhes de um contato da empresa."""
    channel = ChannelContactsSerializer(read_only=True)
    class Meta:
        model = TenantContact
        fields = ['id', 'channel', 'value']

class TenantDetailForUserSerializer(serializers.ModelSerializer):
    """Serializer para a representação de um Tenant dentro do objeto User."""
    permissions = serializers.SerializerMethodField()
    wallet = serializers.SerializerMethodField()
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'legal_name', 'slug', 'logo', 'status', 'permissions', 'wallet']
        read_only_fields = fields

    def get_permissions(self, tenant_obj: Tenant) -> list[str]:
        user = self.context.get('user')
        if not user: return []
        try:
            membership = user.memberships.get(tenant=tenant_obj, status='ACTIVE')
            permissions_qs = membership.role.permissions.select_related('content_type')
            return sorted([f"{p.content_type.app_label}.{p.codename}" for p in permissions_qs])
        except TenantMembership.DoesNotExist:
            return []

    def get_wallet(self, tenant_obj: Tenant) -> dict | None:
        wallet = tenant_obj.wallet.first()
        return WalletSummarySerializer(wallet).data if wallet else None

class TenantSerializer(serializers.ModelSerializer):
    """Serializer para representar os dados detalhados de um Tenant."""
    owner = UserDetailSerializer(read_only=True)
    company_contacts = TenantContactSerializer(many=True, read_only=True)
    location_city = serializers.CharField(source='location.city', read_only=True)
    location_state = serializers.CharField(source='location.state.name', read_only=True)
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'legal_name', 'slug', 'type', 'document', 'status', 'owner', 
            'billing_day', 'contact_email', 'company_contacts', 'parent', 'street', 
            'number', 'complement', 'neighborhood', 'postal_code', 'location_city', 'location_state', 'logo'
        ]
        read_only_fields = fields

class TenantMembershipSerializer(serializers.ModelSerializer):
    """Serializer para listar os membros de um Tenant."""
    user = UserDetailSerializer(read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    class Meta:
        model = TenantMembership
        fields = ['id', 'user', 'role', 'role_name', 'status', 'joined_at']
        read_only_fields = ['id', 'user', 'role_name', 'joined_at']


# --- Serializers para Escrita (POST, PATCH) ---

class TenantCreateSerializer(serializers.ModelSerializer):
    """Serializer para a criação de um novo Tenant."""
    location_id = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(), source='location', write_only=True)
    class Meta:
        model = Tenant
        fields = ['legal_name', 'name', 'document', 'type', 'street', 'number', 'complement', 'neighborhood', 'postal_code', 'location_id']
        extra_kwargs = {'name': {'required': False, 'allow_blank': True}}

class TenantUpdateSerializer(serializers.ModelSerializer):
    """Serializer para a atualização de dados de um Tenant."""
    financial_contact_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='financial_contact', write_only=True, required=False)
    location_id = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(), source='location', write_only=True, required=False)
    class Meta:
        model = Tenant
        fields = ['name', 'legal_name', 'logo', 'contact_email', 'billing_day', 'street', 'number', 'complement', 'neighborhood', 'postal_code', 'location_id', 'financial_contact_id']

class TenantContactCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para criar e atualizar os contatos da empresa."""
    channel_id = serializers.PrimaryKeyRelatedField(queryset=ChannelContacts.objects.all(), source='channel', write_only=True)
    class Meta:
        model = TenantContact
        fields = ['channel_id', 'value']

class TenantMembershipInviteSerializer(serializers.Serializer):
    """Serializer para convidar um novo membro."""
    email = serializers.EmailField(write_only=True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), write_only=True)

class TenantLinkRequestSerializer(serializers.ModelSerializer):
    """Serializer para criar uma solicitação de vínculo de matriz."""
    class Meta:
        model = TenantLinkRequest
        fields = ['parent_document']

