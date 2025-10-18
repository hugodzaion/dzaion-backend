# -*- coding: utf-8 -*-
"""
Módulo de Views (Controladores) para o App 'accounts'.

Author: Dzaion
Version: 1.1.0
"""
from django.db import transaction
from drf_spectacular.utils import (extend_schema, extend_schema_view,
                                   OpenApiExample, OpenApiResponse)
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsActiveUser
from .serializers import (ChangePasswordSerializer,
                          CustomTokenObtainPairSerializer,
                          UserDetailSerializer, UserPhotoSerializer,
                          UserRegisterSerializer)

# -----------------------------------------------------------------------------
# Bloco de Autenticação
# -----------------------------------------------------------------------------

@extend_schema(
    summary="Obter Tokens de Acesso e Atualização (Login)",
    description="""
    Autentica um usuário a partir do `email` ou `whatsapp` e `password` e retorna os tokens JWT.

    - **Funcionalidade "Lembre-se de mim"**: Envie `"rememberMe": true` no corpo da requisição 
      para que o token `refresh` tenha uma validade estendida de 180 dias.
    - **Validação de Conta Ativa**: O endpoint retornará um erro de autenticação (`401 Unauthorized`) 
      se a conta do usuário estiver marcada como inativa (`is_active=False`).
    """,
    tags=["Contas e Autenticação"],
    responses={
        200: CustomTokenObtainPairSerializer,
        401: OpenApiResponse(description="Credenciais inválidas ou conta desativada."),
    }
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """View de login que utiliza o serializer customizado para a lógica de 'rememberMe'."""
    serializer_class = CustomTokenObtainPairSerializer

# -----------------------------------------------------------------------------
# Bloco de Gerenciamento de Conta
# -----------------------------------------------------------------------------

@extend_schema(
    summary="Registrar um Novo Usuário",
    description="Cria uma nova conta de usuário. O usuário é criado como inativo (`is_active=False`) por padrão, aguardando um fluxo de ativação.",
    tags=["Contas e Autenticação"],
    request=UserRegisterSerializer,
    responses={
        201: OpenApiResponse(
            description="Usuário registrado com sucesso. O ID do novo usuário é retornado.",
            examples=[OpenApiExample('Exemplo de Resposta', value={'context': {'user_id': 123}})]
        ),
        400: OpenApiResponse(description="Erro de validação (ex: e-mail já existe, senhas não coincidem, CPF inválido)."),
    }
)
class RegisterView(generics.CreateAPIView):
    """Endpoint para o registro de novos usuários."""
    serializer_class = UserRegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        context = {'user_id': user.id}
        return Response(
            {'context': context},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

@extend_schema_view(
    get=extend_schema(
        summary="Obter Dados do Usuário Logado ('/me')",
        description="Retorna as informações detalhadas e públicas do usuário autenticado.",
        tags=["Contas e Autenticação"],
        responses={200: UserDetailSerializer}
    ),
    put=extend_schema(
        summary="Atualizar Foto de Perfil",
        description="Atualiza a foto de perfil do usuário. A requisição deve ser `multipart/form-data`.",
        tags=["Contas e Autenticação"],
        request=UserPhotoSerializer,
        responses={200: UserPhotoSerializer}
    ),
    patch=extend_schema(exclude=True), # Oculta o PATCH, já que PUT é suficiente para a foto.
    delete=extend_schema(
        summary="Remover Foto de Perfil",
        description="Remove a foto de perfil associada ao usuário.",
        tags=["Contas e Autenticação"],
        request=None,
        responses={204: OpenApiResponse(description="Foto removida com sucesso.")}
    )
)
class MeView(generics.RetrieveUpdateAPIView):
    """Endpoint unificado para gerenciar o perfil do usuário logado (`/me`)."""
    permission_classes = [IsAuthenticated, IsActiveUser]
    serializer_class = UserDetailSerializer
    # DZAION-REVIEW: Definido explicitamente os métodos permitidos para maior clareza e segurança.
    http_method_names = ['get', 'put', 'delete']

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return UserPhotoSerializer
        return super().get_serializer_class()

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.photo.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    summary="Alterar Senha do Usuário Logado",
    description="Permite que o usuário autenticado altere sua própria senha. É obrigatório fornecer a senha atual para validação.",
    tags=["Contas e Autenticação"],
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(description="Senha alterada com sucesso.", examples=[OpenApiExample('Sucesso', value={'success': 'Senha alterada com sucesso.'})]),
        400: OpenApiResponse(description="Erro de validação (ex: senha atual incorreta, senhas novas não coincidem)."),
        403: OpenApiResponse(description="Permissão negada (usuário inativo)."),
    }
)
class ChangePasswordView(generics.GenericAPIView):
    """Endpoint para a alteração segura de senha."""
    permission_classes = [IsAuthenticated, IsActiveUser]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)
