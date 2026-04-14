import calendar
from datetime import date, timedelta
from celery import shared_task
from django.utils import timezone
from .models import Reminder
from customers.models import Customer


@shared_task
def scan_upcoming_dates():
    """扫描即将到来的生日和纪念日，自动创建提醒"""
    today = timezone.localdate()
    # 扫描未来30天内的日期
    for days_ahead in range(0, 31):
        target_date = today + timedelta(days=days_ahead)
        year = target_date.year

        # 扫描生日
        customers_with_birthday = Customer.objects.filter(
            birthday__isnull=False,
        )
        for customer in customers_with_birthday:
            try:
                birthday_this_year = customer.birthday.replace(year=year)
                if birthday_this_year == target_date:
                    _create_reminder_if_not_exists(
                        customer=customer,
                        remind_date=target_date,
                        remind_type='birthday',
                        title=f'{customer.name}的生日',
                        message=f'{customer.name}的生日是{customer.birthday.strftime("%m月%d日")}，请提前准备祝福！',
                        days_before=days_ahead,
                    )
            except ValueError:
                # 闰年2月29日处理
                continue

        # 扫描纪念日
        customers_with_anniversary = Customer.objects.filter(
            anniversary__isnull=False,
        )
        for customer in customers_with_anniversary:
            try:
                anniversary_this_year = customer.anniversary.replace(year=year)
                if anniversary_this_year == target_date:
                    _create_reminder_if_not_exists(
                        customer=customer,
                        remind_date=target_date,
                        remind_type='anniversary',
                        title=f'{customer.name}的纪念日',
                        message=f'{customer.name}的纪念日是{customer.anniversary.strftime("%m月%d日")}，请提前准备祝福！',
                        days_before=days_ahead,
                    )
            except ValueError:
                continue

    return f'扫描完成: {today}'


def _create_reminder_if_not_exists(customer, remind_date, remind_type, title, message, days_before):
    """如果提醒不存在则创建"""
    exists = Reminder.objects.filter(
        customer=customer,
        remind_date=remind_date,
        remind_type=remind_type,
    ).exists()
    if not exists:
        Reminder.objects.create(
            customer=customer,
            remind_date=remind_date,
            remind_type=remind_type,
            title=title,
            message=message,
            days_before=days_before,
        )
