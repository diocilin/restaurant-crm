from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/customers/', include('customers.urls')),
    path('api/dining/', include('dining.urls')),
    path('api/reservations/', include('reservations.urls')),
    path('api/reminders/', include('reminders.urls')),
    path('api/dashboard/', include('customers.urls')),  # dashboard stats in customers
]
