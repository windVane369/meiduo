"""meiduo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('apps.users.urls', 'users'), namespace='users')),
    path('', include(('apps.verifications.urls', 'verifications'), namespace='verifications')),
    path('', include(('apps.contents.urls', 'contents'), namespace='contents')),
    path('', include(('apps.oauth.urls', 'oauth'), namespace='oauth')),
    path('', include(('apps.areas.urls', 'areas'), namespace='areas')),
    path('', include(('apps.goods.urls', 'goods'), namespace='goods')),
    path('', include(('apps.carts.urls', 'carts'), namespace='carts')),
    path('search/', include(('haystack.urls', 'search'), namespace='search')),
]
