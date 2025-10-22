# -*- coding: utf-8 -*-
"""
Módulo de Configuração do Django Admin para o App 'dzaion'.

Author: Dzaion
Version: 0.2.0
"""
from django.contrib import admin
from .models import AIModel, DzaionAction, Conversation, Message, TokenUsageLog, AIThoughtProcess

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'identifier', 'usage_mode')
    search_fields = ('name', 'identifier')

@admin.register(DzaionAction)
class DzaionActionAdmin(admin.ModelAdmin):
    list_display = ('name', 'verb_code', 'cost_bearer', 'is_active')
    list_filter = ('cost_bearer', 'is_active')
    search_fields = ('name', 'verb_code')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'initial_action', 'status', 'created_at')
    list_filter = ('status', 'initial_action')
    search_fields = ('user__email', 'tenant__name')
    readonly_fields = ('created_at', 'updated_at')
    
    def owner(self, obj):
        return obj.user or obj.tenant
    owner.short_description = 'Proprietário'

# DZAION-CONVO: Adicionando o modelo Message ao admin
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'direction', 'content_snippet', 'status', 'created_at')
    list_filter = ('direction', 'status')
    search_fields = ('conversation__id', 'content')
    readonly_fields = ('created_at', 'updated_at')

    def content_snippet(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_snippet.short_description = 'Conteúdo'

@admin.register(TokenUsageLog)
class TokenUsageLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'payer', 'dzaion_action', 'total_tokens', 'is_billed', 'created_at')
    list_filter = ('is_billed', 'dzaion_action', 'ai_model')
    search_fields = ('payer_user__email', 'payer_tenant__name')
    readonly_fields = ('created_at', 'updated_at')
    
    def payer(self, obj):
        return obj.payer_user or obj.payer_tenant
    payer.short_description = 'Pagador'

    def total_tokens(self, obj):
        return obj.input_tokens + obj.output_tokens
    total_tokens.short_description = 'Total de Tokens'

@admin.register(AIThoughtProcess)
class AIThoughtProcessAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'status', 'expires_at', 'finished_at')
    list_filter = ('status', 'action')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')

