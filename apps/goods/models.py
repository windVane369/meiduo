from django.db import models

from utils import db_utils


class GoodsCategory(db_utils.BaseModel):
    """商品类别"""
    name = models.CharField(max_length=10, verbose_name='名称')
    parent = db_utils.ForeignKey(
        'self', related_name='subs', null=True, blank=True, on_delete=models.CASCADE, verbose_name='父类别')

    class Meta:
        db_table = 'md_goods_category'
        verbose_name_plural = verbose_name = '商品类别'

    def __str__(self):
        return self.name


class GoodsChannelGroup(db_utils.BaseModel):
    """商品频道组"""
    name = models.CharField(max_length=20, verbose_name='频道组名')

    class Meta:
        verbose_name_plural = verbose_name = '商品频道组'

    def __str__(self):
        return self.name


class GoodsChannel(db_utils.BaseModel):
    """商品频道"""
    group = db_utils.ForeignKey(GoodsChannelGroup, verbose_name='频道组名')
    category = db_utils.ForeignKey(GoodsCategory, on_delete=models.CASCADE, verbose_name='顶级商品类别')
    url = models.CharField(max_length=50, verbose_name='频道页面链接')
    sequence = models.IntegerField(verbose_name='组内顺序')

    class Meta:
        db_table = 'md_goods_channel'
        verbose_name_plural = verbose_name = '商品频道'

    def __str__(self):
        return self.category.name


class Brand(db_utils.BaseModel):
    """品牌"""
    name = models.CharField(max_length=20, verbose_name='名称')
    logo = models.ImageField(verbose_name='Logo图片')
    first_letter = models.CharField(max_length=1, verbose_name='品牌首字母')

    class Meta:
        db_table = 'md_brand'
        verbose_name_plural = verbose_name = '品牌'

    def __str__(self):
        return self.name


class SPU(db_utils.BaseModel):
    """商品SPU"""
    name = models.CharField(max_length=50, verbose_name='名称')
    brand = db_utils.ForeignKey(
        Brand, on_delete=models.PROTECT, verbose_name='品牌')
    category1 = db_utils.ForeignKey(
        GoodsCategory, on_delete=models.PROTECT, related_name='cat1_spu', verbose_name='一级类别')
    category2 = db_utils.ForeignKey(
        GoodsCategory, on_delete=models.PROTECT, related_name='cat2_spu', verbose_name='二级类别')
    category3 = db_utils.ForeignKey(
        GoodsCategory, on_delete=models.PROTECT, related_name='cat3_spu', verbose_name='三级类别')
    sales = models.IntegerField(default=0, verbose_name='销量')
    comments = models.IntegerField(default=0, verbose_name='评价数')
    desc_detail = models.TextField(default='', verbose_name='详细介绍')
    desc_pack = models.TextField(default='', verbose_name='包装信息')
    desc_service = models.TextField(default='', verbose_name='售后服务')

    class Meta:
        db_table = 'md_spu'
        verbose_name_plural = verbose_name = '商品SPU'

    def __str__(self):
        return self.name


class SKU(db_utils.BaseModel):
    """商品SKU"""
    name = models.CharField(max_length=50, verbose_name='名称')
    caption = models.CharField(max_length=100, verbose_name='副标题')
    spu = db_utils.ForeignKey(SPU, on_delete=models.CASCADE, verbose_name='商品')
    category = db_utils.ForeignKey(GoodsCategory, on_delete=models.PROTECT, verbose_name='从属类别')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='进价')
    market_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='市场价')
    stock = models.IntegerField(default=0, verbose_name='库存')
    sales = models.IntegerField(default=0, verbose_name='销量')
    comments = models.IntegerField(default=0, verbose_name='评价数')
    is_launched = models.BooleanField(default=True, verbose_name='是否上架销售')
    default_image = models.ImageField(max_length=200, default='', null=True, blank=True, verbose_name='默认图片')

    class Meta:
        db_table = 'md_sku'
        verbose_name_plural = verbose_name = '商品SKU'

    def __str__(self):
        return '%s: %s' % (self.id, self.name)


class SKUImage(db_utils.BaseModel):
    """SKU图片"""
    sku = db_utils.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='sku')
    image = models.ImageField(verbose_name='图片')

    class Meta:
        db_table = 'md_sku_image'
        verbose_name_plural = verbose_name = 'SKU图片'

    def __str__(self):
        return '%s %s' % (self.sku.name, self.id)


class SPUSpecification(db_utils.BaseModel):
    """商品SPU规格"""
    spu = db_utils.ForeignKey(SPU, on_delete=models.CASCADE, related_name='specs', verbose_name='商品SPU')
    name = models.CharField(max_length=20, verbose_name='规格名称')

    class Meta:
        db_table = 'md_spu_specification'
        verbose_name_plural = verbose_name = '商品SPU规格'

    def __str__(self):
        return '%s: %s' % (self.spu.name, self.name)


class SpecificationOption(db_utils.BaseModel):
    """规格选项"""
    spec = db_utils.ForeignKey(SPUSpecification, related_name='options', on_delete=models.CASCADE, verbose_name='规格')
    value = models.CharField(max_length=20, verbose_name='选项值')

    class Meta:
        db_table = 'md_specification_option'
        verbose_name_plural = verbose_name = '规格选项'

    def __str__(self):
        return '%s - %s' % (self.spec, self.value)


class SKUSpecification(db_utils.BaseModel):
    """SKU具体规格"""
    sku = db_utils.ForeignKey(SKU, related_name='specs', on_delete=models.CASCADE, verbose_name='sku')
    spec = db_utils.ForeignKey(SPUSpecification, on_delete=models.PROTECT, verbose_name='规格名称')
    option = db_utils.ForeignKey(SpecificationOption, on_delete=models.PROTECT, verbose_name='规格值')

    class Meta:
        db_table = 'md_sku_specification'
        verbose_name_plural = verbose_name = 'SKU规格'

    def __str__(self):
        return '%s: %s - %s' % (self.sku, self.spec.name, self.option.value)


class GoodsVisitCount(db_utils.BaseModel):
    """统计分类商品访问量模型类"""
    category = db_utils.ForeignKey(GoodsCategory, on_delete=models.CASCADE, verbose_name='商品分类')
    count = models.IntegerField(verbose_name='访问量', default=0)
    date = models.DateField(auto_now_add=True, verbose_name='统计日期')

    class Meta:
        db_table = 'md_goods_visit'
        verbose_name = '统计分类商品访问量'
        verbose_name_plural = verbose_name
