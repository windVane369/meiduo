from django.urls import path, re_path
from apps.users import views
from utils import patterns

urlpatterns = [
    path('register/', views.RegisterView.as_view()),
    re_path(rf'usernames/(?P<username>{patterns.PATTERN_USERNAME_STR})/count/', views.UsernameCountView.as_view()),
    re_path(rf'mobiles/(?P<mobile>{patterns.PATTERN_MOBILE_STR})/count/', views.MobileCountView.as_view()),
]
