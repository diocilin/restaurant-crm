from rest_framework import viewsets
from django.db.models import Count, Q
from django.utils import timezone
import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Reservation
from .serializers import ReservationSerializer
from customers.models import Store, TableArea
from dining.models import DiningRecord

WEEKDAYS = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related('customer', 'store', 'table_area')
    serializer_class = ReservationSerializer
    filterset_fields = ['customer', 'store', 'status', 'reservation_date']
    search_fields = ['customer__name', 'customer__phone', 'table_number', 'notes']
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
        """未来10天预订概览（按门店统计）"""
        today = timezone.localdate()
        store_id = request.query_params.get('store')

        days = []
        for i in range(10):
            target_date = today + datetime.timedelta(days=i)
            weekday = WEEKDAYS[target_date.weekday()]

            # 获取门店列表
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
                total_rooms = TableArea.objects.filter(store=store, is_active=True).count()
                booked_rooms = active_reservations.filter(seat_type='room').count()

                # 大堂桌子统计
                total_hall = store.hall_tables_count
                booked_hall = active_reservations.filter(seat_type='hall').count()

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
        """查询指定门店+日期的可用座位"""
        store_id = request.query_params.get('store')
        date_str = request.query_params.get('date')

        if not store_id or not date_str:
            return Response({'error': '请提供门店ID和日期'}, status=400)

        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({'error': '门店不存在'}, status=404)

        # 当日已被占用的座位
        occupied = Reservation.objects.filter(
            store=store,
            reservation_date=date_str,
            status__in=['pending', 'confirmed', 'arrived'],
        )

        # 已占用的包间ID列表
        occupied_room_ids = set(occupied.filter(seat_type='room').values_list('table_area_id', flat=True))

        # 已占用的大堂桌号列表
        occupied_hall_numbers = set(occupied.filter(seat_type='hall').values_list('table_number', flat=True))

        # 可用包间
        rooms = TableArea.objects.filter(store=store, is_active=True)
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
            timezone.datetime.combine(reservation.reservation_date, reservation.reservation_time)
        ) if reservation.reservation_time else timezone.now()

        # 确定桌号显示
        table_display = reservation.table_number or ''
        if reservation.seat_type == 'room' and reservation.table_area:
            table_display = reservation.table_area.name

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
