import json

from celery.utils.log import get_task_logger
from django import http
from django.views import View

from apps.goods.models import SKU

logger = get_task_logger('django')


class CartsView(View):
    """购物车"""

    def post(self, request):
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        if all([sku_id, count]) is False:
            return http.HttpResponseForbidden('缺少必传参数')

        try:
            SKU.objects.get(pk=sku_id, is_launched=True)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku_id不存在')

        try:
            count = int(count)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('参数类型有误')

        if isinstance(selected, bool) is False:
            return http.HttpResponseForbidden('参数类型有误')

        user = request.user
        if user.is_authenticated:
            # 登录用户
            pass
        else:
            # 未登录用户
            pass

    def get(self, request):
        pass
