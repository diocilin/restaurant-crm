from rest_framework import serializers
from .models import Reservation


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
        """验证座位是否已被占用"""
        seat_type = attrs.get('seat_type', '')
        table_number = attrs.get('table_number', '')
        table_area = attrs.get('table_area')
        store = attrs.get('store')
        reservation_date = attrs.get('reservation_date')

        # 如果是更新操作，排除自身
        instance = getattr(self, 'instance', None)
        qs = Reservation.objects.filter(status__in=['pending', 'confirmed', 'arrived'])

        if instance:
            qs = qs.exclude(pk=instance.pk)

        if store and reservation_date:
            qs = qs.filter(store=store, reservation_date=reservation_date)

            if seat_type == 'room' and table_area:
                if qs.filter(table_area=table_area).exists():
                    raise serializers.ValidationError({
                        'table_area': f'该包间在 {reservation_date} 已被预订'
                    })
            elif seat_type == 'hall' and table_number:
                if qs.filter(seat_type='hall', table_number=table_number).exists():
                    raise serializers.ValidationError({
                        'table_number': f'大堂 {table_number} 号桌在 {reservation_date} 已被预订'
                    })

        return attrs
