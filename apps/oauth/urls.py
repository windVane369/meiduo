from django.urls import path, re_path
from apps.oauth import views

urlpatterns = [
    path('qq/authorization/', views.QQAuthURLView.as_view()),
    path('oauth_callback/', views.QQAuthUserView.as_view())
]
