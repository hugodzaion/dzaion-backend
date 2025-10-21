# -*- coding: utf-8 -*-
"""
Módulo de URLs para o App 'contacts'.

Author: Dzaion
Version: 0.1.0
"""
from django.urls import path
from .views import ChannelContactsListView

urlpatterns = [
    path('channels/', ChannelContactsListView.as_view(), name='channel-list'),
]
