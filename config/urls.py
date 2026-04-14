import os
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import FileResponse, HttpResponseNotFound
from django.views.static import serve
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/customers/', include('customers.urls')),
    path('api/dining/', include('dining.urls')),
    path('api/reservations/', include('reservations.urls')),
    path('api/reminders/', include('reminders.urls')),
]

# 前端SPA路由 - 提供Vue构建产物的静态文件
FRONTEND_DIR = getattr(settings, 'FRONTEND_DIST_DIR', None)

if FRONTEND_DIR and FRONTEND_DIR.is_dir():
    # 前端静态资源（js/css/img等）
    urlpatterns += [
        re_path(r'^(?!api/|admin/|static/|media/)(?P<path>.*)$', serve_frontend, name='frontend'),
    ]


def serve_frontend(request, path):
    """提供Vue SPA前端页面"""
    frontend_dir = getattr(settings, 'FRONTEND_DIST_DIR', None)
    if not frontend_dir or not frontend_dir.is_dir():
        return HttpResponseNotFound('Frontend not built.')

    # 尝试查找具体文件（如 /assets/xxx.js）
    file_path = frontend_dir / path
    if file_path.is_file():
        return FileResponse(open(file_path, 'rb'))

    # SPA回退：所有未匹配路径返回index.html
    index_path = frontend_dir / 'index.html'
    if index_path.is_file():
        return FileResponse(open(index_path, 'rb'))

    return HttpResponseNotFound('Not found.')


# 开发模式下提供媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
