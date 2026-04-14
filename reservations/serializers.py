from rest_framework import serializers
from .models import Reservation
from datetime import timedelta


class ReservationSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    seat_type_display = serializers.CharField(source='get_seat_type_display', read_only=True)
    table_area_name = serializers.CharField(source='table_area.name', default='', read_only=True)

    class Meta:
        model = Reservation
        fields = '__all__'

    def validate(self, attrs):
        """验证座位是否在时间段内被占用（前1小时~后2小时）"""
        seat_type = attrs.get('seat_type', '')
        table_number = attrs.get('table_number', '')
        table_area = attrs.get('table_area')
        store = attrs.get('store')
        reservation_date = attrs.get('reservation_date')
        reservation_time = attrs.get('reservation_time')

        if not (store and reservation_date and reservation_time):
            return attrs

        # 计算时间窗口：预订时间前1小时 ~ 后2小时
        from datetime import datetime, time as dt_time
        res_datetime = datetime.combine(reservation_date, reservation_time)
        window_start = (res_datetime - timedelta(hours=1)).time()
        window_end = (res_datetime + timedelta(hours=2)).time()

        # 如果是更新操作，排除自身
        instance = getattr(self, 'instance', None)
        qs = Reservation.objects.filter(status__in=['pending', 'confirmed', 'arrived'])

        if instance:
            qs = qs.exclude(pk=instance.pk)

        qs = qs.filter(store=store, reservation_date=reservation_date)

        # 筛选时间窗口内有冲突的预订
        # 冲突条件：已有预订的 [时间-1h, 时间+2h] 与新预订的 [时间-1h, 时间+2h] 有重叠
        # 简化：已有预订时间在新预订的窗口内，或新预订时间在已有预订的窗口内
        conflicting = []
        for r in qs:
            if not r.reservation_time:
                continue
            r_start = (datetime.combine(reservation_date, r.reservation_time) - timedelta(hours=1)).time()
            r_end = (datetime.combine(reservation_date, r.reservation_time) + timedelta(hours=2)).time()
            # 时间窗口重叠检测
            if not (window_end <= r_start or r_end <= window_start):
                conflicting.append(r)

        if seat_type == 'room' and table_area:
            for r in conflicting:
                if r.table_area_id == table_area.id:
                    raise serializers.ValidationError({
                        'table_area': f'该包间在 {r.reservation_time.strftime("%H:%M")} 已被预订（时间冲突）'
                    })
        elif seat_type == 'hall' and table_number:
            for r in conflicting:
                if r.seat_type == 'hall' and r.table_number == table_number:
                    raise serializers.ValidationError({
                        'table_number': f'大堂 {table_number} 号桌在 {r.reservation_time.strftime("%H:%M")} 已被预订（时间冲突）'
                    })

        return attrs
