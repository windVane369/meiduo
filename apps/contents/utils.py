# -*- coding: utf-8 -*-
from apps.goods.models import GoodsChannel


def get_categories():
    """返回商品类别数据"""

    categories = {}  # 用来包装所有商品类别数据
    goods_channels_qs = GoodsChannel.objects.order_by('group_id', 'sequence')
    for channel in goods_channels_qs:
        group_id = channel.group_id  # 获取组号

        # 判断当前的组号在字典中是否存在
        if group_id not in categories:
            # 不存在,包装一个当前组的准备数据
            categories[group_id] = {'channels': [], 'sub_cats': []}

        cat1 = channel.category  # 获取一级类别数据
        cat1.url = channel.url  # 将频道中的url绑定给一级类别对象

        categories[group_id]['channels'].append(cat1)

        cat2_qs = cat1.subs.all()  # 获取当前一组下面的所有二级数据
        for cat2 in cat2_qs:  # 遍历二级数据查询集
            cat3_qs = cat2.subs.all()  # 获取当前二级下面的所有三级，得到三级查询集
            cat2.sub_cats = cat3_qs
            categories[group_id]['sub_cats'].append(cat2)

    return categories
