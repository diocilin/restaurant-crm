from rest_framework import viewsets
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta, time as dt_time
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Reservation
from .serializers import ReservationSerializer
from customers.models import Store, TableArea
from dining.models import DiningRecord

WEEKDAYS = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']


def get_time_window_conflicts(store, reservation_date, reservation_time, exclude_pk=None):
    """
    获取指定时间段内（前1h~后2h）有冲突的预订QuerySet
    """
    res_datetime = datetime.combine(reservation_date, reservation_time)
    window_start = (res_datetime - timedelta(hours=1)).time()
    window_end = (res_datetime + timedelta(hours=2)).time()

    qs = Reservation.objects.filter(
        store=store,
        reservation_date=reservation_date,
        status__in=['pending', 'confirmed', 'arrived'],
    )
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)

    # 筛选时间窗口内有冲突的预订ID
    conflicting_ids = []
    for r in qs:
        if not r.reservation_time:
            continue
        r_start = (datetime.combine(reservation_date, r.reservation_time) - timedelta(hours=1)).time()
        r_end = (datetime.combine(reservation_date, r.reservation_time) + timedelta(hours=2)).time()
        if not (window_end <= r_start or r_end <= window_start):
            conflicting_ids.append(r.id)

    return qs.filter(id__in=conflicting_ids)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related('customer', 'store').prefetch_related('table_areas')
    serializer_class = ReservationSerializer
    filterset_fields = ['customer', 'store', 'status', 'reservation_date']
    search_fields = ['customer__name', 'customer__phone', 'table_numbers', 'notes']
    ordering_fields = ['reservation_date', 'reservation_time', 'party_size']

    @action(detail=False, methods=['get'])
    def today(self, request):
        """今日预订（排除已取消）"""
        today = timezone.localdate()
        queryset = self.filter_queryset(self.get_queryset()).filter(
            reservation_date=today
        ).exclude(status='cancelled')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overview(self, request):
        """未来10天预订概览（按门店统计，基于时间段冲突检测）"""
        today = timezone.localdate()
        store_id = request.query_params.get('store')
        time_str = request.query_params.get('time')

        days = []
        for i in range(10):
            target_date = today + timedelta(days=i)
            weekday = WEEKDAYS[target_date.weekday()]

            stores = Store.objects.filter(is_active=True)
            if store_id:
                stores = stores.filter(id=store_id)

            store_stats = []
            for store in stores:
                # 该门店当日有效预订
                active_reservations = Reservation.objects.filter(
                    store=store,
                    reservation_date=target_date,
                    status__in=['pending', 'confirmed', 'arrived'],
                )

                # 包间统计
                total_rooms = TableArea.objects.filter(store=store, is_active=True, area_type='room').count()
                # 如果传了时间参数，按时间段统计冲突的包间数
                if time_str:
                    try:
                        target_time = datetime.strptime(time_str, '%H:%M:%S').time()
                        conflicting = get_time_window_conflicts(store, target_date, target_time)
                        booked_rooms = conflicting.filter(table_areas__isnull=False).distinct().count()
                    except (ValueError, TypeError):
                        booked_rooms = active_reservations.filter(table_areas__isnull=False).distinct().count()
                else:
                    booked_rooms = active_reservations.filter(table_areas__isnull=False).distinct().count()

                # 大堂桌子统计
                total_hall = store.hall_tables_count
                if time_str:
                    try:
                        target_time = datetime.strptime(time_str, '%H:%M:%S').time()
                        conflicting = get_time_window_conflicts(store, target_date, target_time)
                        booked_hall = conflicting.exclude(table_numbers='').count()
                    except (ValueError, TypeError):
                        booked_hall = active_reservations.exclude(table_numbers='').count()
                else:
                    booked_hall = active_reservations.exclude(table_numbers='').count()

                store_stats.append({
                    'store_id': store.id,
                    'store_name': store.name,
                    'total_rooms': total_rooms,
                    'booked_rooms': booked_rooms,
                    'available_rooms': max(0, total_rooms - booked_rooms),
                    'total_hall': total_hall,
                    'booked_hall': booked_hall,
                    'available_hall': max(0, total_hall - booked_hall),
                    'total_reservations': active_reservations.count(),
                })

            days.append({
                'date': target_date.strftime('%Y-%m-%d'),
                'date_short': target_date.strftime('%m/%d'),
                'weekday': weekday,
                'is_today': i == 0,
                'stores': store_stats,
            })

        return Response(days)

    @action(detail=False, methods=['get'])
    def available_seats(self, request):
        """查询指定门店+日期+时间的可用座位（基于时间段冲突检测）"""
        store_id = request.query_params.get('store')
        date_str = request.query_params.get('date')
        time_str = request.query_params.get('time')

        if not store_id or not date_str:
            return Response({'error': '请提供门店ID和日期'}, status=400)

        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({'error': '门店不存在'}, status=404)

        # 解析日期
        try:
            from datetime import date as dt_date
            reservation_date = dt_date.fromisoformat(date_str)
        except (ValueError, TypeError):
            return Response({'error': '日期格式错误'}, status=400)

        # 获取时间段内有冲突的预订
        if time_str:
            try:
                reservation_time = datetime.strptime(time_str, '%H:%M:%S').time()
                conflicting = get_time_window_conflicts(store, reservation_date, reservation_time)
            except (ValueError, TypeError):
                conflicting = Reservation.objects.none()
        else:
            # 没传时间，默认整天都不可用（保守策略）
            conflicting = Reservation.objects.filter(
                store=store,
                reservation_date=reservation_date,
                status__in=['pending', 'confirmed', 'arrived'],
            )

        # 已占用的包间ID
        occupied_room_ids = set(conflicting.values_list('table_areas__id', flat=True).distinct())

        # 已占用的大堂桌号
        occupied_hall_numbers = set()
        for r in conflicting:
            occupied_hall_numbers.update(r.get_table_number_list())

        # 可用包间
        rooms = TableArea.objects.filter(store=store, is_active=True, area_type='room')
        available_rooms = []
        occupied_rooms = []
        for room in rooms:
            item = {'id': room.id, 'name': room.name, 'capacity': room.capacity}
            if room.id in occupied_room_ids:
                item['available'] = False
                occupied_rooms.append(item)
            else:
                item['available'] = True
                available_rooms.append(item)

        # 可用大堂桌子
        hall_tables = []
        occupied_hall = []
        for i in range(1, store.hall_tables_count + 1):
            number = f'{i:02d}'
            item = {'number': number}
            if number in occupied_hall_numbers:
                item['available'] = False
                occupied_hall.append(item)
            else:
                item['available'] = True
                hall_tables.append(item)

        return Response({
            'store_name': store.name,
            'date': date_str,
            'time': time_str or '',
            'rooms': {
                'available': available_rooms,
                'occupied': occupied_rooms,
                'total': rooms.count(),
                'booked': len(occupied_rooms),
            },
            'hall': {
                'available': hall_tables,
                'occupied': occupied_hall,
                'total': store.hall_tables_count,
                'booked': len(occupied_hall),
            },
        })

    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """日历视图数据"""
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')
        queryset = self.filter_queryset(self.get_queryset())
        if start_date:
            queryset = queryset.filter(reservation_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(reservation_date__lte=end_date)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """确认预订"""
        reservation = self.get_object()
        reservation.status = 'confirmed'
        reservation.save()
        return Response(self.get_serializer(reservation).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消预订"""
        reservation = self.get_object()
        reservation.status = 'cancelled'
        reservation.save()
        return Response(self.get_serializer(reservation).data)

    @action(detail=True, methods=['post'])
    def arrive(self, request, pk=None):
        """标记到店，并自动创建就餐记录"""
        reservation = self.get_object()
        reservation.status = 'arrived'
        reservation.save()

        # 自动创建就餐记录
        dining_datetime = timezone.make_aware(
            datetime.combine(reservation.reservation_date, reservation.reservation_time)
        ) if reservation.reservation_time else timezone.now()

        # 确定桌号显示
        table_display = reservation.seat_info_display

        dining_record = DiningRecord.objects.create(
            customer=reservation.customer,
            store=reservation.store,
            dining_date=dining_datetime,
            party_size=reservation.party_size,
            table_number=table_display,
            total_amount=0,
            notes=f'由预订自动创建（预订ID: {reservation.id}）',
        )

        return Response({
            'reservation': self.get_serializer(reservation).data,
            'dining_record_id': dining_record.id,
            'message': '已标记到店并自动创建就餐记录',
        })


def admin_available_seats(request):
    """Admin专用座位查询接口（使用Django Session认证，不需要JWT）"""
    from django.http import JsonResponse
    from django.contrib.auth.decorators import login_required

    if not request.user.is_staff:
        return JsonResponse({'error': '无权限'}, status=403)

    store_id = request.GET.get('store')
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')

    if not store_id or not date_str:
        return JsonResponse({'error': '请提供门店ID和日期'}, status=400)

    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        return JsonResponse({'error': '门店不存在'}, status=404)

    try:
        # 兼容多种日期格式
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y']:
            try:
                reservation_date = datetime.strptime(date_str, fmt).date()
                break
            except ValueError:
                continue
        else:
            raise ValueError('无法解析日期格式')
    except (ValueError, TypeError):
        return JsonResponse({'error': '日期格式错误'}, status=400)

    if time_str:
        try:
            # 兼容多种时间格式
            for fmt in ['%H:%M:%S', '%H:%M', '%H:%M:%S.%f']:
                try:
                    reservation_time = datetime.strptime(time_str, fmt).time()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError('无法解析时间格式')
            conflicting = get_time_window_conflicts(store, reservation_date, reservation_time)
        except (ValueError, TypeError):
            conflicting = Reservation.objects.none()
    else:
        conflicting = Reservation.objects.filter(
            store=store, reservation_date=reservation_date,
            status__in=['pending', 'confirmed', 'arrived'],
        )

    occupied_room_ids = set(conflicting.values_list('table_areas__id', flat=True).distinct())

    occupied_hall_numbers = set()
    for r in conflicting:
        occupied_hall_numbers.update(r.get_table_number_list())

    rooms = TableArea.objects.filter(store=store, is_active=True, area_type='room')
    available_rooms = [{'id': r.id, 'name': r.name, 'capacity': r.capacity, 'available': True} for r in rooms if r.id not in occupied_room_ids]
    occupied_rooms = [{'id': r.id, 'name': r.name, 'capacity': r.capacity, 'available': False} for r in rooms if r.id in occupied_room_ids]

    hall_tables = []
    occupied_hall = []
    for i in range(1, store.hall_tables_count + 1):
        number = f'{i:02d}'
        item = {'number': number}
        if number in occupied_hall_numbers:
            item['available'] = False
            occupied_hall.append(item)
        else:
            item['available'] = True
            hall_tables.append(item)

    return JsonResponse({
        'store_name': store.name,
        'date': date_str,
        'time': time_str or '',
        'rooms': {'available': available_rooms, 'occupied': occupied_rooms, 'total': rooms.count(), 'booked': len(occupied_rooms)},
        'hall': {'available': hall_tables, 'occupied': occupied_hall, 'total': store.hall_tables_count, 'booked': len(occupied_hall)},
    })
