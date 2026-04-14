from django.contrib import admin
from .models import Reminder


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'remind_date', 'remind_type', 'title', 'status', 'days_before', 'created_at')
    list_filter = ('status', 'remind_type', 'remind_date')
    search_fields = ('customer__name', 'customer__phone', 'title')
    date_hierarchy = 'remind_date'
    list_editable = ('status',)
    actions = ['mark_handled', 'mark_ignored']

    @admin.action(description='标记为已处理')
    def mark_handled(self, request, queryset):
        queryset.filter(status='pending').update(status='handled')

    @admin.action(description='标记为已忽略')
    def mark_ignored(self, request, queryset):
        queryset.filter(status='pending').update(status='ignored')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer')
