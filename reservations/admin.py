from django.contrib import admin
from django import forms
from .models import Reservation
from customers.models import Store, TableArea
from datetime import datetime, timedelta


class ReservationAdminForm(forms.ModelForm):
    """自定义预订表单 - 复选框座位类型 + 格子多选 + 冲突检测"""
    # 隐藏字段，用于接收JS提交的多选座位数据
    selected_hall = forms.CharField(
        label='已选大堂桌号', required=False,
        widget=forms.HiddenInput()
    )
    selected_rooms = forms.CharField(
        label='已选包间ID', required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Reservation
        fields = '__all__'
        widgets = {
            'seat_type': forms.Select(attrs={'style': 'display:none;'}),
            'table_number': forms.HiddenInput(),
            'table_area': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 编辑时预填隐藏字段
        if self.instance.pk:
            if self.instance.seat_type == 'hall' and self.instance.table_number:
                self.fields['selected_hall'].initial = self.instance.table_number
            if self.instance.seat_type == 'room' and self.instance.table_area_id:
                self.fields['selected_rooms'].initial = str(self.instance.table_area_id)

    def clean(self):
        cleaned_data = super().clean()
        store = cleaned_data.get('store')
        reservation_date = cleaned_data.get('reservation_date')
        reservation_time = cleaned_data.get('reservation_time')
        selected_hall = cleaned_data.get('selected_hall', '')
        selected_rooms = cleaned_data.get('selected_rooms', '')

        if not (store and reservation_date and reservation_time):
            return cleaned_data

        if not selected_hall and not selected_rooms:
            raise forms.ValidationError('请至少选择一个座位（大堂桌号或包间）')

        # 时间窗口冲突检测（前1h~后2h）
        res_dt = datetime.combine(reservation_date, reservation_time)
        window_end = (res_dt + timedelta(hours=2)).time()
        window_start = (res_dt - timedelta(hours=1)).time()

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

        # 验证大堂桌号
        if selected_hall:
            for number in selected_hall.split(','):
                number = number.strip()
                if not number:
                    continue
                for r in conflicting:
                    if r.seat_type == 'hall' and r.table_number == number:
                        raise forms.ValidationError(
                            f'大堂 {number} 号桌在 {r.reservation_time.strftime("%H:%M")} 已被预订（时间冲突）'
                        )
            cleaned_data['table_number'] = selected_hall
            cleaned_data['seat_type'] = 'hall' if not selected_rooms else cleaned_data.get('seat_type', 'hall')

        # 验证包间
        if selected_rooms:
            for room_id_str in selected_rooms.split(','):
                room_id_str = room_id_str.strip()
                if not room_id_str:
                    continue
                try:
                    room_id = int(room_id_str)
                except ValueError:
                    continue
                for r in conflicting:
                    if r.table_area_id == room_id:
                        room_name = r.table_area.name if r.table_area else str(room_id)
                        raise forms.ValidationError(
                            f'包间 {room_name} 在 {r.reservation_time.strftime("%H:%M")} 已被预订（时间冲突）'
                        )
            cleaned_data['table_area_id'] = int(selected_rooms.split(',')[0].strip())
            cleaned_data['seat_type'] = 'room' if not selected_hall else cleaned_data.get('seat_type', 'room')

        return cleaned_data

    def save(self, commit=True):
        """多座位时创建多条预订记录"""
        selected_hall = self.cleaned_data.get('selected_hall', '')
        selected_rooms = self.cleaned_data.get('selected_rooms', '')
        hall_numbers = [n.strip() for n in selected_hall.split(',') if n.strip()]
        room_ids = [r.strip() for r in selected_rooms.split(',') if r.strip()]

        # 如果只有一个座位类型，直接保存
        if len(hall_numbers) <= 1 and len(room_ids) <= 1:
            if hall_numbers:
                self.instance.table_number = hall_numbers[0]
                self.instance.seat_type = 'hall'
                self.instance.table_area = None
            elif room_ids:
                self.instance.table_area_id = int(room_ids[0])
                self.instance.seat_type = 'room'
                self.instance.table_number = ''
            return super().save(commit=commit)

        # 多座位：保存第一条，然后创建额外的预订
        extra_instances = []
        if hall_numbers:
            self.instance.table_number = hall_numbers[0]
            self.instance.seat_type = 'hall'
            self.instance.table_area = None
            for number in hall_numbers[1:]:
                extra_instances.append(Reservation(
                    customer=self.instance.customer,
                    store=self.instance.store,
                    reservation_date=self.instance.reservation_date,
                    reservation_time=self.instance.reservation_time,
                    party_size=self.instance.party_size,
                    seat_type='hall',
                    table_number=number,
                    table_area=None,
                    status=self.instance.status,
                    notes=self.instance.notes,
                ))
        if room_ids:
            self.instance.table_area_id = int(room_ids[0])
            self.instance.seat_type = 'room'
            self.instance.table_number = ''
            for rid in room_ids[1:]:
                extra_instances.append(Reservation(
                    customer=self.instance.customer,
                    store=self.instance.store,
                    reservation_date=self.instance.reservation_date,
                    reservation_time=self.instance.reservation_time,
                    party_size=self.instance.party_size,
                    seat_type='room',
                    table_number='',
                    table_area_id=int(rid),
                    status=self.instance.status,
                    notes=self.instance.notes,
                ))

        instance = super().save(commit=commit)
        if commit:
            for extra in extra_instances:
                extra.save()
        return instance


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
            'fields': ('seat_type', 'selected_hall', 'selected_rooms'),
            'description': '选择门店、日期和时间后自动加载可用座位。可同时选择大堂和包间，支持多选。',
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
