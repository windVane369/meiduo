from django.urls import path, re_path
from apps.verifications import views
from utils import patterns

urlpatterns = [
    re_path(rf'image_codes/(?P<uuid>{patterns.PATTERN_IMAGE_CODE_STR})/', views.ImageCodeView.as_view()),
    re_path(rf'sms_codes/(?P<mobile>{patterns.PATTERN_MOBILE_STR})/', views.SMSCodeView.as_view())
]
