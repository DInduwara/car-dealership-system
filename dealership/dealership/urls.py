from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import LoginView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", LoginView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/", include("users.urls")),
    path("api/cars/", include("cars.urls")),
    path("api/bookings/", include("bookings.urls")),
    path("api/sales/", include("sales.urls")),
    path("api/staff/", include("staff.urls")),
    path("", include("frontend.urls")),
]