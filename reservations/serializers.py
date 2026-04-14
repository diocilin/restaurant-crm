from rest_framework import serializers
from .models import Reservation
from datetime import timedelta


class ReservationSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    seat_info = serializers.CharField(source='seat_info_display', read_only=True)
    seat_type_display = serializers.CharField(source='seat_type_display', read_only=True)
    table_area_names = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = '__all__'

    def get_table_area_names(self, obj):
        return [room.name for room in obj.table_areas.all()]

    def validate(self, attrs):
        """验证座位是否在时间段内被占用（前1小时~后2小时）"""
        table_numbers = attrs.get('table_numbers', '')
        table_areas = attrs.get('table_areas', [])
        store = attrs.get('store')
        reservation_date = attrs.get('reservation_date')
        reservation_time = attrs.get('reservation_time')

        if not (store and reservation_date and reservation_time):
            return attrs

        from datetime import datetime
        res_datetime = datetime.combine(reservation_date, reservation_time)
        window_start = (res_datetime - timedelta(hours=1)).time()
        window_end = (res_datetime + timedelta(hours=2)).time()

        instance = getattr(self, 'instance', None)
        qs = Reservation.objects.filter(status__in=['pending', 'confirmed', 'arrived'])
        if instance:
            qs = qs.exclude(pk=instance.pk)
        qs = qs.filter(store=store, reservation_date=reservation_date)

        # 收集时间窗口内有冲突的预订
        conflicting = []
        for r in qs:
            if not r.reservation_time:
                continue
            r_start = (datetime.combine(reservation_date, r.reservation_time) - timedelta(hours=1)).time()
            r_end = (datetime.combine(reservation_date, r.reservation_time) + timedelta(hours=2)).time()
            if not (window_end <= r_start or r_end <= window_start):
                conflicting.append(r)

        # 检查包间冲突
        for room in table_areas:
            for r in conflicting:
                if r.table_areas.filter(id=room.id).exists():
                    raise serializers.ValidationError({
                        'table_areas': f'包间 {room.name} 在 {r.reservation_time.strftime("%H:%M")} 已被预订（时间冲突）'
                    })

        # 检查大堂桌号冲突
        if table_numbers:
            for number in table_numbers.split(','):
                number = number.strip()
                if not number:
                    continue
                for r in conflicting:
                    if number in r.get_table_number_list():
                        raise serializers.ValidationError({
                            'table_numbers': f'大堂 {number} 号桌在 {r.reservation_time.strftime("%H:%M")} 已被预订（时间冲突）'
                        })

        return attrs
