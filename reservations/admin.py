from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'store', 'reservation_date', 'reservation_time', 'party_size', 'table_number', 'status')
    list_filter = ('status', 'store', 'reservation_date')
    search_fields = ('customer__name', 'customer__phone', 'table_number')
    date_hierarchy = 'reservation_date'
    list_editable = ('status', 'table_number')
    actions = ['confirm_reservations', 'cancel_reservations']

    @admin.action(description='确认预订')
    def confirm_reservations(self, request, queryset):
        queryset.filter(status='pending').update(status='confirmed')

    @admin.action(description='取消预订')
    def cancel_reservations(self, request, queryset):
        queryset.exclude(status='arrived').update(status='cancelled')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'store')
