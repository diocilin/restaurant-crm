from django.contrib import admin
from .models import Store, Tag, Customer, CustomerTag


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'tables_count', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')
    list_editable = ('is_active',)


class CustomerTagInline(admin.TabularInline):
    model = CustomerTag
    extra = 1
    verbose_name = '标签'
    verbose_name_plural = '标签'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'color')
    list_filter = ('category',)
    search_fields = ('name',)
    list_editable = ('color',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'wechat', 'gender', 'level', 'store', 'birthday', 'anniversary', 'created_at')
    list_filter = ('level', 'gender', 'store', 'tags')
    search_fields = ('name', 'phone', 'wechat', 'notes')
    inlines = [CustomerTagInline]
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'phone', 'wechat', 'gender', 'store', 'level')
        }),
        ('重要日期', {
            'fields': ('birthday', 'anniversary'),
            'classes': ('collapse',)
        }),
        ('其他', {
            'fields': ('notes',)
        }),
    )
    date_hierarchy = 'created_at'
    actions = ['mark_as_vip', 'mark_as_svip']

    @admin.action(description='标记为VIP')
    def mark_as_vip(self, request, queryset):
        queryset.update(level='vip')

    @admin.action(description='标记为SVIP')
    def mark_as_svip(self, request, queryset):
        queryset.update(level='svip')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('store')
