# -*- coding: utf-8 -*-

from django.urls import path
from apps.areas import views

urlpatterns = [
    path('areas/', views.AreasView.as_view())
]
