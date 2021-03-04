from datetime import datetime

from django import http
from django.core.paginator import EmptyPage, Paginator
from django.shortcuts import render
from django.views import View

from apps.contents.utils import get_categories
from apps.goods.models import GoodsCategory, SKU, GoodsVisitCount
from apps.goods.utils import get_breadcrumb
from utils.response_code import RETCODE


class ListView(View):
    """商品列表界面"""

    def get(self, request, category_id):

        try:
            cat3 = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('类别id不存在')

        page_num = request.GET.get('page_num') or 1
        page_size = request.GET.get('page_size') or 5

        # 获取查询参数中的排序规则
        sort = request.GET.get('sort')

        if sort == 'price':
            sort_filed = 'price'
        elif sort == 'hot':
            sort_filed = 'sales'
        else:
            sort = 'default'
            sort_filed = '-create_time'
        # 查询指定三级类别下的所有sku
        sku_qs = cat3.sku_set.filter(is_launched=True).order_by(sort_filed)
        paginator = Paginator(sku_qs, page_size)  # 创建分页对象
        try:
            page_skus = paginator.page(page_num)  # 返回指定页的数据
        except EmptyPage:
            return http.HttpResponseForbidden('没有下一页了')

        context = {
            'categories': get_categories(),  # 频道分类
            'breadcrumb': get_breadcrumb(cat3),  # 面包屑导航
            'sort': sort,  # 排序字段
            'category': cat3,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': paginator.num_pages,  # 总页数
            'page_num': page_num  # 当前页码
        }
        return render(request, 'list.html', context)


class HotGoodsView(View):
    """热销商品排行"""

    def get(self, request, category_id):
        skus = SKU.objects.filter(is_launched=True, category_id=category_id).order_by('-sales')[:2]
        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_skus})


class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)
        # 查询当前sku所对应的spu
        spu = sku.spu
        # 获取当前sku所对应的三级分类
        category = sku.category

        """1.准备当前商品的规格选项列表 [8, 11]"""
        # 获取出当前正显示的sku商品的规格选项id列表
        current_sku_spec_qs = sku.specs.order_by('spec_id')
        current_sku_option_ids = []  # [8, 11]
        for current_sku_spec in current_sku_spec_qs:
            current_sku_option_ids.append(current_sku_spec.option_id)

        """2.构造规格选择仓库
        {(8, 11): 3, (8, 12): 4, (9, 11): 5, (9, 12): 6, (10, 11): 7, (10, 12): 8}
        """
        # 构造规格选择仓库
        temp_sku_qs = spu.sku_set.all()  # 获取当前spu下的所有sku
        # 选项仓库大字典
        spec_sku_map = {}  # {(8, 11): 3, (8, 12): 4, (9, 11): 5, (9, 12): 6, (10, 11): 7, (10, 12): 8}
        for temp_sku in temp_sku_qs:
            # 查询每一个sku的规格数据
            temp_spec_qs = temp_sku.specs.order_by('spec_id')
            temp_sku_option_ids = []  # 用来包装每个sku的选项值
            for temp_spec in temp_spec_qs:
                temp_sku_option_ids.append(temp_spec.option_id)
            spec_sku_map[tuple(temp_sku_option_ids)] = temp_sku.id

        """3.组合 并找到sku_id 绑定"""
        spu_spec_qs = spu.specs.order_by('id')  # 获取当前spu中的所有规格

        for index, spec in enumerate(spu_spec_qs):  # 遍历当前所有的规格
            spec_option_qs = spec.options.all()  # 获取当前规格中的所有选项
            temp_option_ids = current_sku_option_ids[:]  # 复制一个新的当前显示商品的规格选项列表
            for option in spec_option_qs:  # 遍历当前规格下的所有选项
                temp_option_ids[index] = option.id  # [8, 12]
                option.sku_id = spec_sku_map.get(tuple(temp_option_ids))  # 给每个选项对象绑定下他sku_id属性

            spec.spec_options = spec_option_qs  # 把规格下的所有选项绑定到规格对象的spec_options属性上

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'spu': spu,
            'category': category,
            'spec_qs': spu_spec_qs
        }

        return render(request, 'detail.html', context)


class DetailVisitView(View):
    """详情页分类商品访问量"""

    def post(self, request, category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('缺少必传参数')
        date = datetime.now()
        try:
            visit_obj = GoodsVisitCount.objects.get(date=date, category=category)
        except GoodsVisitCount.DoesNotExist:
            visit_obj = GoodsVisitCount(category=category)
        visit_obj.count += 1
        visit_obj.save()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
