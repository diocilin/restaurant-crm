"""
美团收银Excel导入引擎

支持两种Excel格式：
1. 店内订单明细（含桌号、金额、订单号）
2. 菜品销售统计（含菜品名、销量、金额）

导入逻辑：
- 解析Excel → 通过桌号匹配CRM预订记录 → 关联客户 → 创建就餐记录
- 无预订的桌号 → 创建无客户关联的散客记录
- 重复订单号自动跳过（unique_together约束）
"""
import openpyxl
from datetime import datetime, time as dt_time, date as dt_date
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils import timezone

from .models import DiningRecord
from reservations.models import Reservation
from customers.models import Store


def parse_excel_file(file_obj, store_id):
    """
    解析上传的Excel文件，自动识别格式并导入

    返回: {
        'success': int,
        'skipped': int,
        'errors': list,
        'total_amount': Decimal,
        'records': list,
    }
    """
    try:
        wb = openpyxl.load_workbook(file_obj, read_only=True, data_only=True)
    except Exception as e:
        return {'success': 0, 'skipped': 0, 'errors': [f'无法读取Excel文件: {str(e)}'], 'total_amount': Decimal('0'), 'records': []}

    ws = wb.active
    rows = list(ws.iter_rows(min_row=1, values_only=True))

    if not rows:
        return {'success': 0, 'skipped': 0, 'errors': ['Excel文件为空'], 'total_amount': Decimal('0'), 'records': []}

    # 自动识别格式：通过表头关键词判断
    headers = [str(h).strip() if h else '' for h in rows[0]]

    if any('菜品' in h and '销量' in h for h in headers):
        return _import_dish_sales(rows, store_id)
    else:
        return _import_order_details(rows, store_id)


def _import_order_details(rows, store_id):
    """导入店内订单明细"""
    if len(rows) < 2:
        return {'success': 0, 'skipped': 0, 'errors': ['数据行不足'], 'total_amount': Decimal('0'), 'records': []}

    headers = [str(h).strip() if h else '' for h in rows[0]]

    # 智能匹配列索引
    col_map = {}
    for i, h in enumerate(headers):
        h_lower = h.lower()
        if '订单' in h and ('号' in h or '编号' in h or '单号' in h):
            col_map['order_no'] = i
        elif '桌' in h:
            col_map['table'] = i
        elif '时间' in h or '日期' in h:
            col_map['time'] = i
        elif '金额' in h or '实收' in h or '合计' in h:
            col_map['amount'] = i
        elif '人数' in h or '就餐' in h:
            col_map['party_size'] = i
        elif '菜品' in h or '明细' in h or '内容' in h:
            col_map['dishes'] = i
        elif '支付' in h and '方式' in h:
            col_map['pay_method'] = i

    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        return {'success': 0, 'skipped': 0, 'errors': [f'门店不存在(ID:{store_id})'], 'total_amount': Decimal('0'), 'records': []}

    success = 0
    skipped = 0
    errors = []
    total_amount = Decimal('0')
    records = []

    for row_idx, row in enumerate(rows[1:], start=2):
        if not row or all(cell is None for cell in row):
            continue

        try:
            # 提取字段
            order_no = str(row[col_map['order_no']]).strip() if 'order_no' in col_map and row[col_map['order_no']] else ''
            table_number = str(row[col_map['table']]).strip() if 'table' in col_map and row[col_map['table']] else ''
            raw_time = row[col_map['time']] if 'time' in col_map else None
            raw_amount = row[col_map['amount']] if 'amount' in col_map else 0
            raw_party = row[col_map['party_size']] if 'party_size' in col_map else 1
            raw_dishes = row[col_map['dishes']] if 'dishes' in col_map else ''
            pay_method = str(row[col_map['pay_method']]).strip() if 'pay_method' in col_map and row[col_map['pay_method']] else ''

            # 解析金额
            try:
                amount = Decimal(str(raw_amount)) if raw_amount else Decimal('0')
            except (InvalidOperation, ValueError):
                amount = Decimal('0')

            # 解析人数
            try:
                party_size = int(float(str(raw_party))) if raw_party else 1
            except (ValueError, TypeError):
                party_size = 1

            # 解析时间
            dining_date = _parse_datetime(raw_time)

            # 解析菜品明细
            dishes = _parse_dishes(raw_dishes)

            # 跳过重复订单
            if order_no:
                if DiningRecord.objects.filter(store=store, order_no=order_no).exists():
                    skipped += 1
                    continue

            # 匹配预订记录（通过桌号+日期）
            customer = _match_customer(store, table_number, dining_date)

            # 创建就餐记录
            record = DiningRecord(
                customer=customer,
                store=store,
                dining_date=dining_date,
                party_size=party_size,
                table_number=table_number,
                total_amount=amount,
                dishes=dishes,
                source='meituan',
                order_no=order_no,
                notes=f'美团导入 | 支付方式: {pay_method}' if pay_method else '美团导入',
            )
            record.save()
            success += 1
            total_amount += amount
            records.append({
                'order_no': order_no or f'行{row_idx}',
                'table': table_number,
                'amount': str(amount),
                'customer': customer.name if customer else '散客(未匹配)',
                'time': dining_date.strftime('%Y-%m-%d %H:%M') if dining_date else '-',
            })

        except Exception as e:
            errors.append(f'第{row_idx}行: {str(e)}')

    return {
        'success': success,
        'skipped': skipped,
        'errors': errors,
        'total_amount': total_amount,
        'records': records,
    }


def _import_dish_sales(rows, store_id):
    """导入菜品销售统计"""
    if len(rows) < 2:
        return {'success': 0, 'skipped': 0, 'errors': ['数据行不足'], 'total_amount': Decimal('0'), 'records': []}

    headers = [str(h).strip() if h else '' for h in rows[0]]

    # 智能匹配列
    col_name = col_qty = col_amount = 0
    for i, h in enumerate(headers):
        h_lower = h.lower()
        if '菜品' in h or '名称' in h:
            col_name = i
        elif '销量' in h or '数量' in h or '份数' in h:
            col_qty = i
        elif '金额' in h or '销售额' in h:
            col_amount = i

    success = 0
    errors = []
    total_amount = Decimal('0')
    records = []

    for row_idx, row in enumerate(rows[1:], start=2):
        if not row or all(cell is None for cell in row):
            continue
        try:
            name = str(row[col_name]).strip() if row[col_name] else ''
            if not name:
                continue
            try:
                qty = int(float(str(row[col_qty]))) if row[col_qty] else 0
            except (ValueError, TypeError):
                qty = 0
            try:
                amount = Decimal(str(row[col_amount])) if row[col_amount] else Decimal('0')
            except (InvalidOperation, ValueError):
                amount = Decimal('0')

            if qty > 0 or amount > 0:
                success += 1
                total_amount += amount
                records.append({
                    'name': name,
                    'qty': qty,
                    'amount': str(amount),
                })
        except Exception as e:
            errors.append(f'第{row_idx}行: {str(e)}')

    return {
        'success': success,
        'skipped': 0,
        'errors': errors,
        'total_amount': total_amount,
        'records': records,
        'type': 'dish_sales',
    }


def _parse_datetime(value):
    """解析多种时间格式"""
    if value is None:
        return timezone.now()
    if isinstance(value, datetime):
        return timezone.make_aware(value) if value.tzinfo is None else value
    if isinstance(value, dt_date):
        return timezone.make_aware(datetime.combine(value, dt_time(12, 0)))
    s = str(value).strip()
    if not s:
        return timezone.now()
    # 尝试多种格式
    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M:%S',
                '%Y/%m/%d %H:%M', '%Y-%m-%d', '%Y/%m/%d', '%H:%M:%S']:
        try:
            dt = datetime.strptime(s, fmt)
            if fmt in ['%H:%M:%S']:
                dt = datetime.combine(timezone.localdate(), dt.time())
            return timezone.make_aware(dt)
        except ValueError:
            continue
    return timezone.now()


def _parse_dishes(value):
    """解析菜品明细文本为JSON列表"""
    if not value:
        return []
    s = str(value).strip()
    if not s:
        return []

    dishes = []
    # 格式1: "宫保鸡丁x1, 鱼香肉丝x2" 或 "宫保鸡丁*1"
    import re
    items = re.split(r'[,，;；\n]', s)
    for item in items:
        item = item.strip()
        if not item:
            continue
        # 匹配 "菜品名 x数量" 或 "菜品名*数量" 或 "菜品名 数量"
        m = re.match(r'(.+?)[xX×*]\s*(\d+)', item)
        if m:
            dishes.append({'name': m.group(1).strip(), 'qty': int(m.group(2)), 'price': 0})
        else:
            # 没有数量，默认1
            dishes.append({'name': item, 'qty': 1, 'price': 0})
    return dishes


def _match_customer(store, table_number, dining_date):
    """
    通过桌号+日期匹配预订记录，返回关联的客户

    匹配逻辑：
    1. 查找同门店、同日期、同桌号的已确认/已到店预订
    2. 大堂桌号精确匹配
    3. 包间名模糊匹配
    """
    if not table_number or not dining_date:
        return None

    date_part = dining_date.date() if hasattr(dining_date, 'date') else dining_date

    # 查找匹配的预订
    reservations = Reservation.objects.filter(
        store=store,
        reservation_date=date_part,
        status__in=['confirmed', 'arrived'],
    )

    # 大堂桌号匹配
    for res in reservations:
        if table_number in res.get_table_number_list():
            return res.customer

    # 包间名匹配（桌号可能是包间名）
    for res in reservations:
        for room in res.table_areas.filter(name__icontains=table_number):
            return res.customer
        # 也反过来匹配：桌号包含包间名
        for room in res.table_areas.all():
            if table_number in room.name or room.name in table_number:
                return res.customer

    return None
