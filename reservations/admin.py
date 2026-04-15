from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'store', 'reservation_date', 'reservation_time',
                    'party_size', 'seat_info', 'status')
    list_filter = ('status', 'store', 'reservation_date')
    search_fields = ('customer__name', 'customer__phone', 'table_numbers', 'notes')
    date_hierarchy = 'reservation_date'
    list_editable = ('status',)
    actions = ['confirm_reservations', 'cancel_reservations']
    filter_horizontal = ('table_areas',)

    fieldsets = (
        ('预订信息', {
            'fields': ('customer', 'store', 'reservation_date', 'reservation_time', 'party_size')
        }),
        ('座位信息', {
            'fields': ('table_areas', 'table_numbers'),
            'description': '座位选择请在前端页面操作（支持可视化选座和冲突检测）。后台仅支持手动编辑。',
            'classes': ('wide',)
        }),
        ('其他', {
            'fields': ('status', 'notes'),
        }),
    )

    @admin.display(description='座位')
    def seat_info(self, obj):
        return obj.seat_info_display or '-'

    @admin.action(description='确认预订')
    def confirm_reservations(self, request, queryset):
        queryset.filter(status='pending').update(status='confirmed')

    @admin.action(description='取消预订')
    def cancel_reservations(self, request, queryset):
        queryset.exclude(status='arrived').update(status='cancelled')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'store').prefetch_related('table_areas')
