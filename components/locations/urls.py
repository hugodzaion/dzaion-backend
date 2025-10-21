# -*- coding: utf-8 -*-
"""
Módulo de URLs para o App 'locations'.

Author: Dzaion
Version: 0.1.0
"""
from django.urls import path
from .views import StateListView, CityListView

urlpatterns = [
    path('states/', StateListView.as_view(), name='state-list'),
    path('states/<uuid:state_id>/cities/', CityListView.as_view(), name='city-list'),
]
