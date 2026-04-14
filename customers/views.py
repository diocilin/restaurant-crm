from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from .models import Store, Tag, Customer
from .serializers import (StoreSerializer, TagSerializer,
                          CustomerListSerializer, CustomerDetailSerializer,
                          CustomerCreateUpdateSerializer)


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class CustomerViewSet(viewsets.ModelViewSet):
    """客户管理ViewSet"""
    queryset = Customer.objects.select_related('store').prefetch_related('customer_tags__tag')
    filterset_fields = ['store', 'level', 'gender']
    search_fields = ['name', 'phone', 'wechat', 'notes']
    ordering_fields = ['name', 'created_at', 'level']

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return CustomerCreateUpdateSerializer
        return CustomerDetailSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """客户统计数据"""
        today = timezone.now().date()
        week_ago = today - timezone.timedelta(days=7)

        total_customers = Customer.objects.count()
        new_this_week = Customer.objects.filter(created_at__date__gte=week_ago).count()
        vip_count = Customer.objects.filter(level__in=['vip', 'svip']).count()

        # 即将过生日的客户（未来7天）
        upcoming_birthdays = []
        for i in range(7):
            target = today + timezone.timedelta(days=i)
            bdays = Customer.objects.filter(
                birthday__isnull=False,
                birthday__month=target.month,
                birthday__day=target.day,
            )
            for c in bdays:
                upcoming_birthdays.append({
                    'customer_id': c.id,
                    'name': c.name,
                    'phone': c.phone,
                    'birthday': c.birthday.strftime('%m-%d'),
                    'days_until': i,
                })

        return Response({
            'total_customers': total_customers,
            'new_this_week': new_this_week,
            'vip_count': vip_count,
            'upcoming_birthdays': upcoming_birthdays,
        })
