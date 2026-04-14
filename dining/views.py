from rest_framework import viewsets
from .models import DiningRecord
from .serializers import DiningRecordSerializer


class DiningRecordViewSet(viewsets.ModelViewSet):
    queryset = DiningRecord.objects.select_related('customer', 'store')
    serializer_class = DiningRecordSerializer
    filterset_fields = ['customer', 'store', 'satisfaction']
    search_fields = ['customer__name', 'customer__phone', 'table_number', 'notes']
    ordering_fields = ['dining_date', 'total_amount']
