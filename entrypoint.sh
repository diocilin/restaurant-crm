#!/bin/bash
set -e

# 等待数据库就绪
echo "Waiting for database..."
while ! python -c "
import psycopg2
import os
try:
    psycopg2.connect(
        host=os.environ.get('DB_HOST', 'postgres'),
        database=os.environ.get('DB_NAME', 'restaurant_crm'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres'),
    )
    print('Database is ready!')
except Exception as e:
    print(f'Database not ready: {e}')
    exit(1)
" 2>/dev/null; do
    sleep 2
done

# 执行数据库迁移
echo "Running migrations..."
python manage.py migrate --noinput

# 创建超级管理员（如果不存在）
echo "Creating superuser if not exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
"

# 加载初始数据
echo "Loading initial data..."
python manage.py load_initial_data 2>/dev/null || echo 'No initial data to load'

# 收集静态文件
echo "Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

# 启动Celery Worker和Beat（后台）
echo "Starting Celery worker..."
celery -A config worker --loglevel=info &
celery -A config beat --loglevel=info &

# 启动Django
echo "Starting Django server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
