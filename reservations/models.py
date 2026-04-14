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
    SEAT_TYPE_CHOICES = [
        ('hall', '大堂'),
        ('room', '包间'),
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
    seat_type = models.CharField('座位类型', max_length=10, choices=SEAT_TYPE_CHOICES,
        blank=True, default='', help_text='大堂或包间')
    table_number = models.CharField('桌号/包间名', max_length=50, blank=True, default='',
        help_text='大堂桌号(01,02...)或包间名称')
    table_area = models.ForeignKey(
        'customers.TableArea', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='包间', related_name='reservations'
    )
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
