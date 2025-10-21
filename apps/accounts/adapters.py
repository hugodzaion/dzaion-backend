# -*- coding: utf-8 -*-
"""
Módulo de Adaptadores Customizados para o django-allauth.

Este módulo intercepta o fluxo de login social para lidar com casos
específicos da nossa aplicação, como a necessidade de coletar dados
adicionais (CPF, WhatsApp) de novos usuários.

Author: Dzaion
Version: 1.0.0
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.http import JsonResponse

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adaptador que customiza o comportamento do login social.
    """
    def pre_social_login(self, request, sociallogin):
        """
        Intercepta o login ANTES que um usuário seja criado ou logado.
        
        Verifica se o usuário já existe no nosso sistema. Se não existir,
        interrompe o fluxo e retorna uma resposta especial para o frontend,
        instruindo-o a iniciar o fluxo de registro completo.
        """
        user = sociallogin.user
        
        # Se o usuário já tem um ID, significa que ele já existe no nosso banco.
        # Deixamos o fluxo de login continuar normalmente.
        if user.id:
            return

        # Se o usuário não tem ID, é a primeira vez que ele faz login via Google.
        # Precisamos verificar se um usuário com o e-mail dele já existe.
        try:
            # Busca por um usuário existente com o mesmo e-mail
            existing_user = self.get_user_model().objects.get(email__iexact=user.email)
            # Se encontrou, conecta a conta social à conta existente e continua.
            sociallogin.connect(request, existing_user)
            return
        except self.get_user_model().DoesNotExist:
            # Este é o caso de um usuário 100% novo.
            # Interrompemos o fluxo de login aqui.
            
            # Preparamos a resposta que o frontend espera (conforme os requisitos)
            response_data = {
                "status": "registration_required",
                "user_info": {
                    "email": user.email,
                    "name": user.get_full_name()
                }
            }
            
            # Usamos ImmediateHttpResponse para parar o allauth e enviar nossa resposta.
            raise ImmediateHttpResponse(JsonResponse(response_data, status=202))

    def get_user_model(self):
        """Helper para obter o modelo de usuário do projeto."""
        from django.contrib.auth import get_user_model
        return get_user_model()
