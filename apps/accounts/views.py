# -*- coding: utf-8 -*-
"""
Módulo de Views (Controladores) para o App 'accounts'.

Author: Dzaion
Version: 1.3.2
"""
from django.db import transaction
from drf_spectacular.utils import (extend_schema, extend_schema_view,
                                   OpenApiExample, OpenApiResponse)
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from .permissions import IsActiveUser
from .serializers import (ChangePasswordSerializer,
                          CustomTokenObtainPairSerializer,
                          UserDetailSerializer, UserPhotoSerializer,
                          UserRegisterSerializer, UserUpdateSerializer)


class GoogleLoginView(SocialLoginView):
    """
    View para o login social com Google.
    """
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


# -----------------------------------------------------------------------------
# Bloco de Autenticação
# -----------------------------------------------------------------------------

@extend_schema(
    summary="Obter Tokens de Acesso e Atualização (Login)",
    description="Autentica um usuário e retorna os tokens JWT.",
    tags=["Contas e Autenticação"]
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# -----------------------------------------------------------------------------
# Bloco de Gerenciamento de Conta
# -----------------------------------------------------------------------------

@extend_schema(
    summary="Registrar um Novo Usuário",
    description="Cria uma nova conta de usuário. O usuário é criado como inativo (`is_active=False`) por padrão.",
    tags=["Contas e Autenticação"],
    request=UserRegisterSerializer
)
class RegisterView(generics.CreateAPIView):
    """Endpoint para o registro de novos usuários."""
    serializer_class = UserRegisterSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Sobrescreve o método create para customizar a resposta de sucesso.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = serializer.save()

        # DZAION-REFACTOR: Atualizada a mensagem de sucesso conforme solicitado.
        masked_whatsapp = f"....{user.whatsapp[-4:]}"
        response_data = {
            "message": "Cadastro realizado com sucesso! Em breve o Dzaion entrará em contato através do WhatsApp.",
            "contact_whatsapp": masked_whatsapp
        }
        
        headers = self.get_success_headers(serializer.data)
        
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

@extend_schema_view(
    get=extend_schema(
        summary="Obter Dados do Usuário Logado ('/me')",
        description="Retorna as informações detalhadas do usuário autenticado.",
        tags=["Contas e Autenticação"]
    ),
    put=extend_schema(
        summary="Atualizar Foto de Perfil",
        description="Atualiza a foto de perfil do usuário (requisição `multipart/form-data`).",
        tags=["Contas e Autenticação"],
        request=UserPhotoSerializer,
        responses={200: UserPhotoSerializer}
    ),
    patch=extend_schema(
        summary="Atualizar Dados Cadastrais",
        description="Atualiza informações do perfil do usuário como nome, gênero, etc.",
        tags=["Contas e Autenticação"],
        request=UserUpdateSerializer,
        responses={200: UserDetailSerializer}
    ),
    delete=extend_schema(
        summary="Remover Foto de Perfil",
        description="Remove a foto de perfil associada ao usuário.",
        tags=["Contas e Autenticação"],
    )
)
class MeView(generics.RetrieveUpdateAPIView):
    """Endpoint unificado para gerenciar o perfil do usuário logado (`/me`)."""
    permission_classes = [IsAuthenticated, IsActiveUser]
    serializer_class = UserDetailSerializer
    
    http_method_names = ['get', 'put', 'patch', 'delete']

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        """
        Retorna o serializer apropriado com base no método da requisição.
        """
        if self.request.method == 'PUT':
            return UserPhotoSerializer
        if self.request.method == 'PATCH':
            return UserUpdateSerializer
        return super().get_serializer_class()

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.photo.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    summary="Alterar Senha do Usuário Logado",
    description="Permite que o usuário autenticado altere sua própria senha.",
    tags=["Contas e Autenticação"],
    request=ChangePasswordSerializer
)
class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsActiveUser]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)

