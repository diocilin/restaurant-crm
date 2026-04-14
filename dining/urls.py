from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiningRecordViewSet

router = DefaultRouter()
router.register(r'records', DiningRecordViewSet, basename='dining')

urlpatterns = [
    path('', include(router.urls)),
]
