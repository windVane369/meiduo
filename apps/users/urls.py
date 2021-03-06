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
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('info/', views.InfoView.as_view(), name='info'),
    path('emails/', views.EmailView.as_view(), name='emails'),
    path('emails/verification/', views.EmailVerifyView.as_view(), name='verify'),
    path('addresses/', views.AddressesView.as_view(), name='addresses'),
    path('addresses/create/', views.AddressCreateView.as_view(), name='createAddress'),
    path('browse_histories/', views.UserBrowseHistory.as_view(), name='browseHistories'),
    re_path('addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view(), name='changeAddress'),
    re_path('addresses/(?P<address_id>\d+)/title/', views.UpdateAddressTitleView.as_view(), name='changeAddressTitle'),
    re_path(
        'addresses/(?P<address_id>\d+)/default/',
        views.UpdateUserDefaultAddressView.as_view(), name='changeDefaultAddress'),
]
