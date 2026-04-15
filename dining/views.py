from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.db.models import Sum, Count, F, Q, DecimalField
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import DiningRecord
from .serializers import DiningRecordSerializer
from .excel_import import parse_excel_file


class DiningRecordViewSet(viewsets.ModelViewSet):
    queryset = DiningRecord.objects.select_related('customer', 'store')
    serializer_class = DiningRecordSerializer
    filterset_fields = ['customer', 'store', 'satisfaction', 'source']
    search_fields = ['customer__name', 'customer__phone', 'table_number', 'notes', 'order_no']
    ordering_fields = ['dining_date', 'total_amount']

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def import_excel(self, request):
        """导入美团收银Excel文件"""
        file_obj = request.FILES.get('file')
        store_id = request.data.get('store')

        if not file_obj:
            return Response({'error': '请上传Excel文件'}, status=status.HTTP_400_BAD_REQUEST)
        if not store_id:
            return Response({'error': '请选择门店'}, status=status.HTTP_400_BAD_REQUEST)

        result = parse_excel_file(file_obj, store_id)

        return Response({
            'message': f'导入完成：成功{result["success"]}条，跳过{result["skipped"]}条（重复）',
            'success': result['success'],
            'skipped': result['skipped'],
            'errors': result['errors'],
            'total_amount': str(result['total_amount']),
            'records': result['records'],
            'type': result.get('type', 'order'),
        })

    @action(detail=False, methods=['get'])
    def dish_stats(self, request):
        """菜品销量统计"""
        store_id = request.query_params.get('store')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        qs = DiningRecord.objects.filter(source='meituan').exclude(dishes=[])

        if store_id:
            qs = qs.filter(store_id=store_id)
        if start_date:
            qs = qs.filter(dining_date__date__gte=start_date)
        if end_date:
            qs = qs.filter(dining_date__date__lte=end_date)

        # 从所有就餐记录中汇总菜品数据
        dish_stats = {}
        total_amount = Decimal('0')
        total_orders = qs.count()

        for record in qs:
            dishes = record.dishes if isinstance(record.dishes, list) else []
            for dish in dishes:
                if not isinstance(dish, dict):
                    continue
                name = dish.get('name', '').strip()
                if not name:
                    continue
                qty = dish.get('qty', 1)
                price = dish.get('price', 0)
                amount = Decimal(str(price)) * int(qty) if price else Decimal('0')

                if name not in dish_stats:
                    dish_stats[name] = {'name': name, 'qty': 0, 'amount': Decimal('0'), 'orders': 0}
                dish_stats[name]['qty'] += int(qty)
                dish_stats[name]['amount'] += amount
                dish_stats[name]['orders'] += 1

            total_amount += record.total_amount

        # 排序：按金额降序
        sorted_dishes = sorted(dish_stats.values(), key=lambda x: x['amount'], reverse=True)

        # 计算占比
        for d in sorted_dishes:
            d['ratio'] = round(float(d['amount'] / total_amount * 100), 2) if total_amount > 0 else 0
            d['amount'] = str(d['amount'])

        # 按日期统计（最近30天）
        daily_stats = []
        for i in range(29, -1, -1):
            target_date = timezone.localdate() - timedelta(days=i)
            day_qs = qs.filter(dining_date__date=target_date)
            day_count = day_qs.count()
            day_amount = day_qs.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            daily_stats.append({
                'date': target_date.strftime('%m-%d'),
                'count': day_count,
                'amount': str(day_amount),
            })

        return Response({
            'total_amount': str(total_amount),
            'total_orders': total_orders,
            'total_dishes': len(sorted_dishes),
            'dish_ranking': sorted_dishes[:50],  # 前50名
            'daily_stats': daily_stats,
        })

    @action(detail=False, methods=['get'])
    def import_logs(self, request):
        """导入记录列表（仅显示美团导入的）"""
        store_id = request.query_params.get('store')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        qs = DiningRecord.objects.filter(source='meituan').select_related('customer', 'store')
        if store_id:
            qs = qs.filter(store_id=store_id)
        if start_date:
            qs = qs.filter(dining_date__date__gte=start_date)
        if end_date:
            qs = qs.filter(dining_date__date__lte=end_date)

        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
