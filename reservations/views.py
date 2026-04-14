from rest_framework import viewsets
from django.db.models import Count
from django.utils import timezone
import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Reservation
from .serializers import ReservationSerializer
from dining.models import DiningRecord


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related('customer', 'store')
    serializer_class = ReservationSerializer
    filterset_fields = ['customer', 'store', 'status', 'reservation_date']
    search_fields = ['customer__name', 'customer__phone', 'table_number', 'notes']
    ordering_fields = ['reservation_date', 'reservation_time', 'party_size']

    @action(detail=False, methods=['get'])
    def today(self, request):
        """今日预订"""
        today = timezone.now().date()
        queryset = self.filter_queryset(self.get_queryset()).filter(reservation_date=today)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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

        dining_record = DiningRecord.objects.create(
            customer=reservation.customer,
            store=reservation.store,
            dining_date=dining_datetime,
            party_size=reservation.party_size,
            table_number=reservation.table_number,
            total_amount=0,
            notes=f'由预订自动创建（预订ID: {reservation.id}）',
        )

        return Response({
            'reservation': self.get_serializer(reservation).data,
            'dining_record_id': dining_record.id,
            'message': '已标记到店并自动创建就餐记录',
        })
