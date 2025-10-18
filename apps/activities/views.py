# -*- coding: utf-8 -*-
"""
Módulo de Views (Controladores) para o App 'activities'.

Contém os endpoints da API para consulta de atividades do usuário.

Author: Dzaion
Version: 1.0.0
"""
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import UserActivity
from .serializers import UserActivitySerializer
from accounts.permissions import IsActiveUser

class StandardResultsSetPagination(PageNumberPagination):
    """
    Configuração de paginação padrão para a API.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

@extend_schema(
    summary="Listar Atividades do Usuário Logado",
    description="Retorna uma lista paginada de todas as atividades associadas ao usuário autenticado, ordenadas da mais recente para a mais antiga.",
    tags=["Atividades"],
)
class UserActivityListView(generics.ListAPIView):
    """
    Endpoint para retornar o feed de atividades do usuário logado.
    """
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated, IsActiveUser]
    pagination_class = StandardResultsSetPagination
    
    # O queryset base. Usamos select_related para otimizar a busca dos ContentTypes.
    queryset = UserActivity.objects.select_related(
        'actor_content_type', 
        'target_content_type'
    ).all()

    def get_queryset(self):
        """
        Filtra o queryset para retornar apenas as atividades do usuário
        que fez a requisição.
        """
        # Garante que um usuário só possa ver seu próprio feed.
        return self.queryset.filter(user=self.request.user).order_by('-timestamp')
