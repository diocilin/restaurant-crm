"""
美团收银Excel导入引擎

适配美团管家后台导出的"店内订单明细"Excel格式：
- Sheet1 "订单明细": 订单汇总（桌号、金额、时间等）
- Sheet3 "菜品明细": 每笔订单的菜品明细（通过订单号关联）

导入逻辑：
1. 读取"订单明细"Sheet → 创建就餐记录
2. 读取"菜品明细"Sheet → 按订单号聚合菜品 → 写入dishes字段
3. 通过桌号匹配CRM预订记录 → 关联客户
4. 重复订单号自动跳过
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
    解析美团收银Excel文件并导入

    返回: {
        'success': int, 'skipped': int, 'errors': list,
        'total_amount': Decimal, 'records': list,
    }
    """
    try:
        wb = openpyxl.load_workbook(file_obj, data_only=True)
    except Exception as e:
        return {'success': 0, 'skipped': 0, 'errors': [f'无法读取Excel文件: {str(e)}'],
                'total_amount': Decimal('0'), 'records': []}

    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        return {'success': 0, 'skipped': 0, 'errors': [f'门店不存在(ID:{store_id})'],
                'total_amount': Decimal('0'), 'records': []}

    # 1. 解析菜品明细Sheet（先解析，后面关联到订单）
    dish_map = _parse_dish_sheet(wb)

    # 2. 解析订单明细Sheet
    result = _parse_order_sheet(wb, store, dish_map)

    return result


def _parse_order_sheet(wb, store, dish_map):
    """解析"订单明细"Sheet"""
    ws_name = None
    for name in wb.sheetnames:
        if '订单明细' in name and '菜品' not in name and '支付' not in name and '优惠' not in name and '联台' not in name:
            ws_name = name
            break
    if not ws_name:
        return {'success': 0, 'skipped': 0, 'errors': ['未找到"订单明细"Sheet'],
                'total_amount': Decimal('0'), 'records': []}

    ws = wb[ws_name]
    rows = []
    for row in ws.iter_rows(min_row=1, values_only=False):
        rows.append([cell.value for cell in row])

    if len(rows) < 4:
        return {'success': 0, 'skipped': 0, 'errors': ['订单明细数据行不足'],
                'total_amount': Decimal('0'), 'records': []}

    # 表头在第3行（index 2）
    headers = [str(h).strip() if h else '' for h in rows[2]]

    # 美团标准列映射
    COL = {
        'date': 0,         # A: 营业日期
        'order_no': 1,     # B: 订单号
        'mode': 2,         # C: 经营模式
        'source': 3,       # D: 订单来源
        'dining_type': 4,  # E: 用餐方式
        'order_time': 5,   # F: 下单时间
        'pay_time': 6,     # G: 结账时间
        'table': 9,        # J: 桌牌号
        'area': 11,        # L: 桌台区域
        'party_size': 12,  # M: 用餐人数
        'amount': 13,      # N: 订单金额（元）
        'actual': 14,      # O: 顾客应付（元）
        'pay_total': 15,   # P: 支付合计（元）
        'discount': 16,    # Q: 订单优惠（元）
        'income': 17,      # R: 订单收入（元）
        'pay_method': 18,  # S: 结账方式
        'order_status': 19,# T: 订单状态
        'notes': 24,       # Y: 整单备注
    }

    success = 0
    skipped = 0
    errors = []
    total_amount = Decimal('0')
    records = []

    for row_idx, row in enumerate(rows[3:], start=4):
        if not row or len(row) < 15:
            continue

        try:
            order_no = str(row[COL['order_no']]).strip() if row[COL['order_no']] else ''
            if not order_no or order_no == '--':
                continue

            # 只导入已结账的订单
            order_status = str(row[COL['order_status']]).strip() if row[COL['order_status']] else ''
            if '已结账' not in order_status:
                continue

            table_number = str(row[COL['table']]).strip() if row[COL['table']] else ''
            area = str(row[COL['area']]).strip() if row[COL['area']] else ''
            raw_time = row[COL['order_time']]
            raw_amount = row[COL['income']] or row[COL['pay_total']] or row[COL['amount']] or 0
            raw_party = row[COL['party_size']]
            pay_method = str(row[COL['pay_method']]).strip() if row[COL['pay_method']] else ''
            notes = str(row[COL['notes']]).strip() if row[COL['notes']] and row[COL['notes']] != '--' else ''

            # 解析金额
            try:
                amount = Decimal(str(raw_amount))
            except (InvalidOperation, ValueError):
                amount = Decimal('0')

            # 解析人数
            try:
                party_size = int(float(str(raw_party))) if raw_party else 1
            except (ValueError, TypeError):
                party_size = 1

            # 解析时间
            dining_date = _parse_datetime(raw_time)

            # 跳过重复
            if DiningRecord.objects.filter(store=store, order_no=order_no).exists():
                skipped += 1
                continue

            # 获取菜品明细
            dishes = dish_map.get(order_no, [])

            # 桌号补充区域信息（如"04"→"大厅04"，"大河"→"包间·大河"）
            table_display = table_number
            if area and area != '--':
                if area == '大厅':
                    table_display = table_number
                elif area == '包间':
                    table_display = table_number  # 包间名就是桌牌号

            # 匹配客户
            customer = _match_customer(store, table_number, dining_date)

            # 构建备注
            note_parts = ['美团导入']
            if area and area != '--':
                note_parts.append(area)
            if pay_method and pay_method != '--':
                note_parts.append(pay_method)
            if notes:
                note_parts.append(notes)

            record = DiningRecord(
                customer=customer,
                store=store,
                dining_date=dining_date,
                party_size=party_size,
                table_number=table_display,
                total_amount=amount,
                dishes=dishes,
                source='meituan',
                order_no=order_no,
                notes=' | '.join(note_parts),
            )
            record.save()
            success += 1
            total_amount += amount
            records.append({
                'order_no': order_no,
                'table': table_display,
                'area': area,
                'amount': str(amount),
                'customer': customer.name if customer else '散客(未匹配)',
                'time': dining_date.strftime('%Y-%m-%d %H:%M') if dining_date else '-',
                'dishes_count': len(dishes),
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


def _parse_dish_sheet(wb):
    """
    解析"菜品明细"Sheet，返回 {订单号: [菜品列表]} 的映射

    菜品明细列：
    A: 订单编号, B: 取餐号, C: 桌牌号, D: 菜品编码, E: 菜品名称,
    F: 规格, G: 做法, H: 加料, I: 销售数量, J: 单位,
    K: 金额合计（元）, L: 菜品优惠（元）, M: 菜品收入（元）, N: 备注
    """
    dish_map = {}

    ws_name = None
    for name in wb.sheetnames:
        if '菜品明细' in name:
            ws_name = name
            break
    if not ws_name:
        return dish_map

    ws = wb[ws_name]
    rows = []
    for row in ws.iter_rows(min_row=1, values_only=False):
        rows.append([cell.value for cell in row])

    if len(rows) < 4:
        return dish_map

    # 表头在第3行（index 2）
    for row in rows[3:]:
        if not row or len(row) < 11:
            continue

        order_no = str(row[0]).strip() if row[0] else ''
        if not order_no:
            continue

        dish_name = str(row[4]).strip() if row[4] else ''
        if not dish_name:
            continue

        try:
            qty = float(str(row[8])) if row[8] else 1
        except (ValueError, TypeError):
            qty = 1

        try:
            price = Decimal(str(row[10])) if row[10] else Decimal('0')
        except (InvalidOperation, ValueError):
            price = Decimal('0')

        unit = str(row[9]).strip() if row[9] else '份'

        if order_no not in dish_map:
            dish_map[order_no] = []

        dish_map[order_no].append({
            'name': dish_name,
            'qty': qty,
            'price': float(price),
            'unit': unit,
        })

    return dish_map


def _parse_datetime(value):
    """解析美团时间格式"""
    if value is None:
        return timezone.now()
    if isinstance(value, datetime):
        return timezone.make_aware(value) if value.tzinfo is None else value
    if isinstance(value, dt_date):
        return timezone.make_aware(datetime.combine(value, dt_time(12, 0)))
    s = str(value).strip()
    if not s or s == '--':
        return timezone.now()
    for fmt in ['%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M',
                '%Y-%m-%d %H:%M', '%Y/%m/%d', '%Y-%m-%d']:
        try:
            dt = datetime.strptime(s, fmt)
            return timezone.make_aware(dt)
        except ValueError:
            continue
    return timezone.now()


def _match_customer(store, table_number, dining_date):
    """通过桌号+日期匹配预订记录"""
    if not table_number or not dining_date:
        return None

    date_part = dining_date.date() if hasattr(dining_date, 'date') else dining_date

    reservations = Reservation.objects.filter(
        store=store,
        reservation_date=date_part,
        status__in=['confirmed', 'arrived'],
    )

    # 大堂桌号匹配
    for res in reservations:
        if table_number in res.get_table_number_list():
            return res.customer

    # 包间名匹配
    for res in reservations:
        for room in res.table_areas.all():
            if table_number in room.name or room.name in table_number:
                return res.customer

    return None
