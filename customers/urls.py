from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StoreViewSet, TagViewSet, TableAreaViewSet, CustomerViewSet

router = DefaultRouter()
router.register(r'stores', StoreViewSet)
router.register(r'tags', TagViewSet)
router.register(r'table-areas', TableAreaViewSet, basename='table-area')
router.register(r'list', CustomerViewSet, basename='customer')

urlpatterns = [
    path('', include(router.urls)),
]
