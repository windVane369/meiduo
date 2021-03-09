import base64
import json
import pickle

from celery.utils.log import get_task_logger
from django import http
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

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
            redis_conn = get_redis_connection('carts')

            pl = redis_conn.pipeline()
            # hincrby 操作hash如果要添加的已经存在，会自动做累加，不存在就新增
            pl.hincrby(f'cart_{user.id}', sku_id, count)

            # 判断当前商品是否勾选
            if selected:
                pl.sadd(f'selected_{user.id}', sku_id)
            else:
                pl.srem(f'selected_{user.id}', sku_id)
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车数据成功'})
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

    def put(self, request):
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        if all([sku_id, count]) is False:
            return http.HttpResponseForbidden('缺少必传参数')

        try:
            sku = SKU.objects.get(pk=sku_id, is_launched=True)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku_id不存在')

        try:
            count = int(count)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('参数类型有误')

        if isinstance(selected, bool) is False:
            return http.HttpResponseForbidden('参数类型有误')

        sku_dict = {
            'id': sku.id,
            'name': sku.name,
            'default_image_url': sku.default_image.url,
            'price': str(sku.price),
            'count': count,
            'selected': selected,
            'amount': str(sku.price * count)
        }
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车数据成功', 'cart_sku': sku_dict})

        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hset(f'cart_{user.id}', sku_id, count)
            if selected:
                pl.sadd(f'selected_{user.id}', sku_id)
            else:
                pl.srem(f'selected_{user.id}', sku_id)
            pl.execute()
        else:
            pass

        return response

    def get(self, request):
        user = request.user
        cart_dict = dict()
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')

            redis_carts = redis_conn.hgetall(f'cart_{user.id}')
            selected_ids = redis_conn.smembers(f'selected_{user.id}')

            for sku_id_bytes in redis_carts:
                cart_dict[int(sku_id_bytes)] = {
                    'count': int(redis_carts[sku_id_bytes]),
                    'selected': sku_id_bytes in selected_ids
                }
        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

        # 查询sku模型
        sku_qs = SKU.objects.filter(id__in=cart_dict.keys())
        # 包装模版渲染时的数据
        sku_list = list()
        for sku_model in sku_qs:
            count = cart_dict[sku_model.id]['count']
            sku_list.append({
                'id': sku_model.id,
                'name': sku_model.name,
                'default_image_url': sku_model.default_image.url,
                'price': str(sku_model.price),
                'count': count,
                'selected': str(cart_dict[sku_model.id]['selected']),
                'amount': str(sku_model.price * count)
            })
        return render(request, 'cart.html', {'cart_skus': sku_list})
