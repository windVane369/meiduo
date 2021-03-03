from django.urls import path, re_path

from apps.goods import views

urlpatterns = [
    # 商品列表
    re_path('list/(?P<category_id>\d+)/$', views.ListView.as_view()),
    # 热销商品
    re_path('hot/(?P<category_id>\d+)/$', views.HotGoodsView.as_view()),
    # 商品详情页
    re_path('detail/(?P<sku_id>\d+)/$', views.DetailView.as_view()),
]
