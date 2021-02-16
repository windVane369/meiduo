from django import http
from django.views import View
from django.core.cache import cache

from apps.areas.models import Area
from utils.response_code import RETCODE


class AreasView(View):
    """省市区"""

    def get(self, request):
        area_id = request.GET.get('area_id')
        if not area_id:
            province_list = cache.get('province_list') or list()
            if not province_list:
                provinces = Area.objects.filter(parent_id__isnull=True)

                for model in provinces:
                    province_list.append({
                        'id': model.id,
                        'name': model.name
                    })
                cache.set('province_list', province_list, 7 * 60 * 60)
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
        else:
            sub_data = cache.get(f'sub_area_{area_id}')
            if not sub_data:
                try:
                    parent_model = Area.objects.get(id=area_id)
                except Area.DoesNotExist:
                    return http.HttpResponseForbidden('area_id不存在')
                sub_areas = parent_model.subs.all()
                sub_area_list = []
                for model in sub_areas:
                    sub_area_list.append({
                        'id': model.id,
                        'name': model.name
                    })

                sub_data = {
                    'id': area_id,
                    'name': parent_model.name,
                    'subs': sub_area_list
                }
                cache.set(f'sub_area_{area_id}', sub_data, 7 * 60 * 60)
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
