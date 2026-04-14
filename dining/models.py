from django.db import models


class DiningRecord(models.Model):
    """就餐记录"""
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.CASCADE, related_name='dining_records',
        verbose_name='客户'
    )
    store = models.ForeignKey(
        'customers.Store', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='门店', related_name='dining_records'
    )
    dining_date = models.DateTimeField('就餐时间')
    party_size = models.PositiveIntegerField('就餐人数', default=1)
    table_number = models.CharField('桌号', max_length=20, blank=True, default='')
    total_amount = models.DecimalField('消费金额', max_digits=10, decimal_places=2, default=0)
    dishes = models.JSONField('点菜记录', blank=True, default=dict, help_text='JSON格式，如 [{"name":"宫保鸡丁","price":38,"qty":1}]')
    satisfaction = models.PositiveIntegerField('满意度', null=True, blank=True, help_text='1-5分')
    notes = models.TextField('备注', blank=True, default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '就餐记录'
        verbose_name_plural = '就餐记录'
        ordering = ['-dining_date']

    def __str__(self):
        return f'{self.customer.name} - {self.dining_date.strftime("%Y-%m-%d %H:%M")}'
