from django.urls import path, re_path
from apps.users import views
from utils import patterns

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    re_path(
        rf'usernames/(?P<username>{patterns.PATTERN_USERNAME_STR})/count/',
        views.UsernameCountView.as_view(), name='user_count'
    ),
    re_path(
        rf'mobiles/(?P<mobile>{patterns.PATTERN_MOBILE_STR})/count/',
        views.MobileCountView.as_view(), name='mobile_count'
    ),
    path('info/', views.InfoView.as_view(), name='info'),
    path('emails/', views.EmailView.as_view(), name='emails'),
    path('emails/verification/', views.EmailVerifyView.as_view(), name='verify'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
