from django.urls import path

from .views import RegisterView, MeView, PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth_register"),
    path("me/", MeView.as_view(), name="auth_me"),
    path("password/forgot/", PasswordResetRequestView.as_view(), name="auth_password_forgot"),
    path("password/reset/", PasswordResetConfirmView.as_view(), name="auth_password_reset"),
]