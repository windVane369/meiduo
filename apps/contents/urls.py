from django.urls import path

from apps.contents import views

urlpatterns = [
    path('', views.IndexView.as_view()),
]
