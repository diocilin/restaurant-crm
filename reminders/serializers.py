from rest_framework import serializers
from .models import Reminder


class ReminderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    remind_type_display = serializers.CharField(source='get_remind_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Reminder
        fields = '__all__'
        read_only_fields = ('handled_by', 'handled_at')
