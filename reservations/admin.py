from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'store', 'reservation_date', 'reservation_time',
                    'party_size', 'seat_info', 'status')
    list_filter = ('status', 'store', 'seat_type', 'reservation_date')
    search_fields = ('customer__name', 'customer__phone', 'table_number', 'notes')
    date_hierarchy = 'reservation_date'
    list_editable = ('status',)
    actions = ['confirm_reservations', 'cancel_reservations']

    fieldsets = (
        ('预订信息', {
            'fields': ('customer', 'store', 'reservation_date', 'reservation_time', 'party_size')
        }),
        ('座位信息', {
            'fields': ('seat_type', 'table_area', 'table_number'),
            'classes': ('wide',)
        }),
        ('其他', {
            'fields': ('status', 'notes'),
        }),
    )

    @admin.display(description='座位')
    def seat_info(self, obj):
        if obj.seat_type == 'room' and obj.table_area:
            return f'包间·{obj.table_area.name}'
        elif obj.seat_type == 'hall' and obj.table_number:
            return f'大堂·{obj.table_number}号'
        elif obj.table_number:
            return obj.table_number
        return '-'

    @admin.action(description='确认预订')
    def confirm_reservations(self, request, queryset):
        queryset.filter(status='pending').update(status='confirmed')

    @admin.action(description='取消预订')
    def cancel_reservations(self, request, queryset):
        queryset.exclude(status='arrived').update(status='cancelled')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'store', 'table_area')
