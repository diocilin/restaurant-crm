"""
数据初始化命令：创建默认门店和标签
用法：python manage.py load_initial_data
"""
from django.core.management.base import BaseCommand
from customers.models import Store, Tag


class Command(BaseCommand):
    help = '加载初始数据：默认门店和标签'

    def handle(self, *args, **options):
        self.stdout.write('正在创建初始数据...')

        # 创建默认门店
        stores_data = [
            {'name': '总店', 'address': '市中心商业街1号', 'phone': '010-88888888', 'tables_count': 30},
            {'name': '分店一', 'address': '东区购物中心2楼', 'phone': '010-66666666', 'tables_count': 20},
            {'name': '分店二', 'address': '西湖区美食街5号', 'phone': '010-77777777', 'tables_count': 25},
        ]
        for s in stores_data:
            store, created = Store.objects.get_or_create(name=s['name'], defaults=s)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  创建门店: {store.name}'))
            else:
                self.stdout.write(f'  门店已存在: {store.name}')

        # 创建默认标签
        tags_data = [
            # 口味偏好
            {'name': '不吃辣', 'category': 'taste', 'color': '#F56C6C'},
            {'name': '微辣', 'category': 'taste', 'color': '#E6A23C'},
            {'name': '重口味', 'category': 'taste', 'color': '#F56C6C'},
            {'name': '清淡', 'category': 'taste', 'color': '#67C23A'},
            {'name': '喜欢甜食', 'category': 'taste', 'color': '#409EFF'},
            # 忌口
            {'name': '不吃香菜', 'category': 'allergy', 'color': '#F56C6C'},
            {'name': '不吃葱蒜', 'category': 'allergy', 'color': '#F56C6C'},
            {'name': '海鲜过敏', 'category': 'allergy', 'color': '#F56C6C'},
            {'name': '坚果过敏', 'category': 'allergy', 'color': '#F56C6C'},
            # 环境偏好
            {'name': '喜欢靠窗', 'category': 'environment', 'color': '#409EFF'},
            {'name': '需要包间', 'category': 'environment', 'color': '#909399'},
            {'name': '带小孩', 'category': 'environment', 'color': '#E6A23C'},
            {'name': '需要儿童椅', 'category': 'environment', 'color': '#E6A23C'},
            # 消费
            {'name': '高消费', 'category': 'consumption', 'color': '#E6A23C'},
            {'name': '价格敏感', 'category': 'consumption', 'color': '#67C23A'},
            # 其他
            {'name': '老客户', 'category': 'other', 'color': '#409EFF'},
            {'name': '企业客户', 'category': 'other', 'color': '#909399'},
            {'name': '朋友推荐', 'category': 'other', 'color': '#67C23A'},
        ]
        for t in tags_data:
            tag, created = Tag.objects.get_or_create(name=t['name'], defaults=t)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  创建标签: {tag.name}'))
            else:
                self.stdout.write(f'  标签已存在: {tag.name}')

        self.stdout.write(self.style.SUCCESS('\n初始数据加载完成！'))
