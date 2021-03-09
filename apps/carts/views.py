import base64
import json
import pickle

from celery.utils.log import get_task_logger
from django import http
from django.views import View

from apps.goods.models import SKU
from utils.response_code import RETCODE

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
            # 登录用户数据存储到redis中
            pass
        else:
            # 未登录用户数据存储到cookie中
            cart_str = request.COOKIES.get('carts')
            # 判断用户是否已经存在cookie购物车数据
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
                # 判断本次要添加的商品是否存在
                if sku_id in cart_dict:
                    count += cart_dict[sku_id]['count']
            else:
                cart_dict = {}
            cart_dict[sku_id] = {'count': count, 'selected': selected}
            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
            response.set_cookie('carts', cart_str)
            return response

    def get(self, request):
        pass
