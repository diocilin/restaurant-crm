from rest_framework import serializers
from .models import DiningRecord


class DiningRecordSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True, default='散客')
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)

    class Meta:
        model = DiningRecord
        fields = '__all__'
