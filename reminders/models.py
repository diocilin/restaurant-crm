from django.db import models


class Reminder(models.Model):
    """提醒模型"""
    TYPE_CHOICES = [
        ('birthday', '生日'),
        ('anniversary', '纪念日'),
        ('custom', '自定义'),
    ]
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('handled', '已处理'),
        ('ignored', '已忽略'),
    ]

    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.CASCADE,
        related_name='reminders', verbose_name='客户'
    )
    remind_date = models.DateField('提醒日期')
    remind_type = models.CharField('提醒类型', max_length=15, choices=TYPE_CHOICES, default='custom')
    title = models.CharField('提醒标题', max_length=100)
    message = models.TextField('提醒内容', blank=True, default='')
    days_before = models.PositiveIntegerField('提前天数', default=3, help_text='提前几天提醒')
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='pending')
    handled_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='处理人'
    )
    handled_at = models.DateTimeField('处理时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '提醒'
        verbose_name_plural = '提醒'
        ordering = ['remind_date', '-created_at']

    def __str__(self):
        return f'{self.customer.name} - {self.title} ({self.remind_date})'
