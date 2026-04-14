from django.contrib import admin
from django import forms
from django.utils.html import mark_safe
from .models import Reservation
from customers.models import Store, TableArea
from datetime import datetime, timedelta


class ReservationAdminForm(forms.ModelForm):
    """自定义预订表单 - 动态座位选择 + 冲突检测"""
    hall_table = forms.ChoiceField(
        label='大堂桌号', required=False,
        widget=forms.Select(attrs={'style': 'width:300px;'})
    )
    room_choice = forms.ChoiceField(
        label='包间', required=False,
        widget=forms.Select(attrs={'style': 'width:300px;'})
    )

    class Meta:
        model = Reservation
        fields = '__all__'
        widgets = {
            'seat_type': forms.Select(attrs={'style': 'width:300px;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化座位选项为空
        self.fields['hall_table'].choices = [('', '---------')]
        self.fields['room_choice'].choices = [('', '---------')]

        # 编辑时预填
        if self.instance.pk:
            if self.instance.seat_type == 'hall' and self.instance.table_number:
                self.fields['hall_table'].initial = self.instance.table_number
            if self.instance.seat_type == 'room' and self.instance.table_area_id:
                self.fields['room_choice'].initial = self.instance.table_area_id

    def clean(self):
        cleaned_data = super().clean()
        seat_type = cleaned_data.get('seat_type', '')
        store = cleaned_data.get('store')
        reservation_date = cleaned_data.get('reservation_date')
        reservation_time = cleaned_data.get('reservation_time')

        if not (store and reservation_date and reservation_time and seat_type):
            return cleaned_data

        # 时间窗口冲突检测（前1h~后2h）
        res_dt = datetime.combine(reservation_date, reservation_time)
        window_start = (res_dt - timedelta(hours=1)).time()
        window_end = (res_dt + timedelta(hours=2)).time()

        from .models import Reservation as ResModel
        qs = ResModel.objects.filter(
            store=store, reservation_date=reservation_date,
            status__in=['pending', 'confirmed', 'arrived'],
        )
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        conflicting = []
        for r in qs:
            if not r.reservation_time:
                continue
            r_start = (datetime.combine(reservation_date, r.reservation_time) - timedelta(hours=1)).time()
            r_end = (datetime.combine(reservation_date, r.reservation_time) + timedelta(hours=2)).time()
            if not (window_end <= r_start or r_end <= window_start):
                conflicting.append(r)

        if seat_type == 'room':
            room_id = cleaned_data.get('room_choice')
            if room_id:
                for r in conflicting:
                    if r.table_area_id == int(room_id):
                        raise forms.ValidationError(
                            f'该包间在 {r.reservation_time.strftime("%H:%M")} 已被预订（时间冲突，锁定时段为预订前后2小时）'
                        )
                cleaned_data['table_area_id'] = int(room_id)
                cleaned_data['table_number'] = ''
            else:
                raise forms.ValidationError('请选择一个包间')

        elif seat_type == 'hall':
            hall_number = cleaned_data.get('hall_table')
            if hall_number:
                for r in conflicting:
                    if r.seat_type == 'hall' and r.table_number == hall_number:
                        raise forms.ValidationError(
                            f'大堂 {hall_number} 号桌在 {r.reservation_time.strftime("%H:%M")} 已被预订（时间冲突）'
                        )
                cleaned_data['table_number'] = hall_number
                cleaned_data['table_area'] = None
            else:
                raise forms.ValidationError('请选择一个大堂桌号')

        return cleaned_data


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    form = ReservationAdminForm
    list_display = ('customer', 'store', 'reservation_date', 'reservation_time',
                    'party_size', 'seat_info', 'status')
    list_filter = ('status', 'store', 'seat_type', 'reservation_date')
    search_fields = ('customer__name', 'customer__phone', 'table_number', 'notes')
    date_hierarchy = 'reservation_date'
    list_editable = ('status',)
    actions = ['confirm_reservations', 'cancel_reservations']
    change_form_template = 'reservations/admin_change_form.html'

    fieldsets = (
        ('预订信息', {
            'fields': ('customer', 'store', 'reservation_date', 'reservation_time', 'party_size')
        }),
        ('座位信息', {
            'fields': ('seat_type', 'hall_table', 'room_choice'),
            'description': '选择座位类型后，点击"刷新座位"按钮加载可用座位（基于时间段冲突检测）',
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
