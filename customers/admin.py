from django.contrib import admin
from django.db.models import Count, Q
from .models import Store, Tag, Customer, CustomerTag, TableArea


class TableAreaInline(admin.TabularInline):
    model = TableArea
    extra = 1
    verbose_name = '包间'
    verbose_name_plural = '包间'
    fields = ('name', 'capacity', 'is_active')


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'hall_tables_count', 'room_count', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')
    list_editable = ('is_active',)
    inlines = [TableAreaInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            room_count=Count('table_areas', filter=Q(table_areas__is_active=True))
        )

    @admin.display(description='包间数')
    def room_count(self, obj):
        return obj.room_count


@admin.register(TableArea)
class TableAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'area_type', 'capacity', 'is_active')
    list_filter = ('store', 'area_type', 'is_active')
    search_fields = ('name', 'store__name')
    list_editable = ('is_active', 'capacity')


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
