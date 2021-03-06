from django.shortcuts import render
from django.views import View

from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories


class IndexView(View):
    """首页"""

    def get(self, request):
        # 查询商品频道和分类
        categories = get_categories()

        return render(request, 'index.html', {'categories': categories, 'contents': self.get_advertising()})

    @staticmethod
    def get_advertising():
        content = {}
        for cat in ContentCategory.objects.all():
            content[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
        return content
