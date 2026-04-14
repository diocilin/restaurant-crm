from django.contrib import admin
from .models import DiningRecord


@admin.register(DiningRecord)
class DiningRecordAdmin(admin.ModelAdmin):
    list_display = ('customer', 'store', 'dining_date', 'party_size', 'table_number', 'total_amount', 'satisfaction')
    list_filter = ('store', 'satisfaction')
    search_fields = ('customer__name', 'customer__phone', 'table_number')
    date_hierarchy = 'dining_date'
    list_editable = ('satisfaction',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'store')
