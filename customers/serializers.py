from rest_framework import serializers
from .models import Store, Tag, Customer, CustomerTag, TableArea


class StoreSerializer(serializers.ModelSerializer):
    customer_count = serializers.IntegerField(source='customers.count', read_only=True)
    room_count = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = '__all__'

    def get_room_count(self, obj):
        return obj.table_areas.filter(is_active=True).count()


class TableAreaSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = TableArea
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CustomerTagSerializer(serializers.ModelSerializer):
    tag = TagSerializer(read_only=True)

    class Meta:
        model = CustomerTag
        fields = ('id', 'tag', 'created_at')


class CustomerListSerializer(serializers.ModelSerializer):
    """客户列表序列化器（轻量）"""
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    tag_names = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ('id', 'name', 'phone', 'wechat', 'gender', 'level',
                  'store', 'store_name', 'birthday', 'anniversary',
                  'tag_names', 'notes', 'created_at')

    def get_tag_names(self, obj):
        return [ct.tag.name for ct in obj.customer_tags.select_related('tag').all()]


class CustomerDetailSerializer(serializers.ModelSerializer):
    """客户详情序列化器（含统计）"""
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    tags = serializers.SerializerMethodField()
    dining_count = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    avg_spent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    last_dining_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Customer
        fields = '__all__'

    def get_tags(self, obj):
        tags = []
        for ct in obj.customer_tags.select_related('tag').all():
            tags.append({
                'id': ct.tag.id,
                'name': ct.tag.name,
                'category': ct.tag.category,
                'color': ct.tag.color,
            })
        return tags


class CustomerCreateUpdateSerializer(serializers.ModelSerializer):
    """客户创建/更新序列化器"""
    tag_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False, default=[])

    class Meta:
        model = Customer
        fields = ('id', 'name', 'phone', 'wechat', 'gender', 'birthday',
                  'anniversary', 'store', 'level', 'tag_ids', 'notes')

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        customer = super().create(validated_data)
        self._update_tags(customer, tag_ids)
        return customer

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        customer = super().update(instance, validated_data)
        if tag_ids is not None:
            self._update_tags(customer, tag_ids)
        return customer

    def _update_tags(self, customer, tag_ids):
        from .models import Tag
        # 过滤掉不存在的标签ID，避免外键错误
        valid_tag_ids = set(Tag.objects.filter(id__in=tag_ids).values_list('id', flat=True))
        CustomerTag.objects.filter(customer=customer).delete()
        for tag_id in tag_ids:
            if tag_id in valid_tag_ids:
                CustomerTag.objects.create(customer=customer, tag_id=tag_id)
