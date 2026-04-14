from django.db import models


class Reservation(models.Model):
    """预订模型"""
    STATUS_CHOICES = [
        ('pending', '待确认'),
        ('confirmed', '已确认'),
        ('arrived', '已到店'),
        ('cancelled', '已取消'),
        ('noshow', '未到店'),
    ]

    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.CASCADE,
        related_name='reservations', verbose_name='客户'
    )
    store = models.ForeignKey(
        'customers.Store', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='门店', related_name='reservations'
    )
    reservation_date = models.DateField('预订日期')
    reservation_time = models.TimeField('预订时间')
    party_size = models.PositiveIntegerField('预订人数', default=1)
    table_areas = models.ManyToManyField(
        'customers.TableArea', blank=True,
        verbose_name='包间', related_name='reservations',
        help_text='可同时选择多个包间'
    )
    table_numbers = models.CharField('大堂桌号', max_length=255, blank=True, default='',
        help_text='多个桌号用逗号分隔，如：01,02,03')
    status = models.CharField('状态', max_length=15, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField('备注', blank=True, default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '预订'
        verbose_name_plural = '预订'
        ordering = ['-reservation_date', '-reservation_time']

    def __str__(self):
        return f'{self.customer.name} - {self.reservation_date} {self.reservation_time} ({self.get_status_display()})'

    @property
    def seat_info_display(self):
        """返回座位信息的可读文本"""
        parts = []
        for room in self.table_areas.all():
            parts.append(f'包间·{room.name}')
        for num in self.get_table_number_list():
            parts.append(f'大堂·{num}号')
        return ', '.join(parts) if parts else '-'

    @property
    def seat_type_display(self):
        """返回座位类型"""
        has_room = self.table_areas.exists()
        has_hall = bool(self.table_numbers)
        if has_room and has_hall:
            return '大堂+包间'
        elif has_room:
            return '包间'
        elif has_hall:
            return '大堂'
        return ''

    def get_table_number_list(self):
        """返回桌号列表"""
        if not self.table_numbers:
            return []
        return [n.strip() for n in self.table_numbers.split(',') if n.strip()]
