from django.db import models
from django.utils import timezone


class Store(models.Model):
    """门店模型"""
    name = models.CharField('门店名称', max_length=100)
    address = models.CharField('门店地址', max_length=255, blank=True, default='')
    phone = models.CharField('联系电话', max_length=20, blank=True, default='')
    hall_tables_count = models.PositiveIntegerField('大堂桌数', default=20,
        help_text='大堂桌子数量，编号自动生成为 01, 02, 03...')
    is_active = models.BooleanField('是否营业', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '门店'
        verbose_name_plural = '门店'
        ordering = ['id']

    def __str__(self):
        return self.name


class TableArea(models.Model):
    """座位区域模型"""
    AREA_TYPE_CHOICES = [
        ('room', '包间'),
        ('hall', '大厅'),
    ]

    store = models.ForeignKey(
        Store, on_delete=models.CASCADE,
        related_name='table_areas', verbose_name='门店'
    )
    area_type = models.CharField('区域类型', max_length=10, choices=AREA_TYPE_CHOICES, default='room')
    name = models.CharField('包间名称', max_length=50,
        help_text='如：牡丹厅、VIP包间等，自由命名')
    capacity = models.PositiveIntegerField('可容纳人数', default=10)
    is_active = models.BooleanField('是否可用', default=True)

    class Meta:
        verbose_name = '座位区域'
        verbose_name_plural = '座位区域'
        unique_together = ('store', 'name')
        ordering = ['store', 'id']

    def __str__(self):
        return f'{self.store.name} - {self.get_area_type_display()} {self.name}'


class Tag(models.Model):
    """客户标签"""
    CATEGORY_CHOICES = [
        ('taste', '口味偏好'),
        ('allergy', '忌口'),
        ('environment', '环境偏好'),
        ('consumption', '消费等级'),
        ('other', '其他'),
    ]

    name = models.CharField('标签名称', max_length=50, unique=True)
    category = models.CharField('分类', max_length=20, choices=CATEGORY_CHOICES, default='other')
    color = models.CharField('颜色', max_length=20, default='#409EFF')

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['category', 'name']

    def __str__(self):
        return f'{self.get_category_display()}: {self.name}'


class Customer(models.Model):
    """客户模型"""
    LEVEL_CHOICES = [
        ('normal', '普通'),
        ('vip', 'VIP'),
        ('svip', 'SVIP'),
    ]
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
        ('', '未知'),
    ]

    name = models.CharField('姓名', max_length=50)
    phone = models.CharField('手机号', max_length=20, unique=True)
    wechat = models.CharField('微信号', max_length=50, blank=True, default='')
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES, blank=True, default='')
    birthday = models.DateField('生日', null=True, blank=True)
    anniversary = models.DateField('纪念日', null=True, blank=True, help_text='如结婚纪念日等')
    store = models.ForeignKey(
        Store, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='常去门店', related_name='customers'
    )
    level = models.CharField('客户等级', max_length=10, choices=LEVEL_CHOICES, default='normal')
    tags = models.ManyToManyField(Tag, through='CustomerTag', blank=True, verbose_name='标签')
    notes = models.TextField('备注', blank=True, default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '客户'
        verbose_name_plural = '客户'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.phone})'

    @property
    def dining_count(self):
        return self.dining_records.count()

    @property
    def total_spent(self):
        return self.dining_records.aggregate(total=models.Sum('total_amount'))['total'] or 0

    @property
    def avg_spent(self):
        count = self.dining_count
        if count == 0:
            return 0
        return self.total_spent / count

    @property
    def last_dining_date(self):
        last = self.dining_records.order_by('-dining_date').first()
        return last.dining_date if last else None


class CustomerTag(models.Model):
    """客户-标签关联"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='customer_tags')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '客户标签'
        verbose_name_plural = '客户标签'
        unique_together = ('customer', 'tag')

    def __str__(self):
        return f'{self.customer.name} - {self.tag.name}'
