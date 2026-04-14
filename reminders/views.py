from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Reminder
from .serializers import ReminderSerializer


class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.select_related('customer')
    serializer_class = ReminderSerializer
    filterset_fields = ['customer', 'remind_type', 'status', 'remind_date']
    search_fields = ['customer__name', 'customer__phone', 'title', 'message']
    ordering_fields = ['remind_date', 'created_at', 'status']

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """待处理提醒"""
        queryset = self.filter_queryset(self.get_queryset()).filter(status='pending')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """即将到来的提醒（未来7天）"""
        today = timezone.now().date()
        week_later = today + timezone.timedelta(days=7)
        queryset = self.filter_queryset(self.get_queryset()).filter(
            remind_date__gte=today,
            remind_date__lte=week_later,
            status='pending',
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def handle(self, request, pk=None):
        """标记为已处理"""
        reminder = self.get_object()
        reminder.status = 'handled'
        reminder.handled_by = request.user
        reminder.handled_at = timezone.now()
        reminder.save()
        return Response(self.get_serializer(reminder).data)

    @action(detail=True, methods=['post'])
    def ignore(self, request, pk=None):
        """标记为已忽略"""
        reminder = self.get_object()
        reminder.status = 'ignored'
        reminder.handled_by = request.user
        reminder.handled_at = timezone.now()
        reminder.save()
        return Response(self.get_serializer(reminder).data)
