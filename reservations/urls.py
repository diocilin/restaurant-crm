from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReservationViewSet, admin_available_seats

router = DefaultRouter()
router.register(r'list', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('admin_seats/', admin_available_seats, name='admin-available-seats'),
    path('', include(router.urls)),
]
