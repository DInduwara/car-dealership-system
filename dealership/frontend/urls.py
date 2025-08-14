from django.urls import path, re_path
from django.views.generic import TemplateView
from .views import AdminTemplateView, StaffTemplateView, CustomerTemplateView

# Map routes to templates with role protection where needed.
urlpatterns = [
	# Auth pages (public)
	path("auth/login", TemplateView.as_view(template_name="auth/login.html"), name="login"),
	path("auth/register", TemplateView.as_view(template_name="auth/register.html"), name="register"),
	path("auth/forgot-password", TemplateView.as_view(template_name="auth/forgot_password.html"), name="forgot_password"),
	path("auth/reset-password", TemplateView.as_view(template_name="auth/reset_password.html"), name="reset_password"),

	# Legal (public)
	path("terms", TemplateView.as_view(template_name="legal/terms.html"), name="terms"),
	path("privacy", TemplateView.as_view(template_name="legal/privacy.html"), name="privacy"),
	path("cookies", TemplateView.as_view(template_name="legal/cookies.html"), name="cookies"),

	# Customer pages
	path("", TemplateView.as_view(template_name="home/index.html"), name="home"),
	path("cars", TemplateView.as_view(template_name="cars/list.html"), name="cars"),
	path("cars/<uuid:id>", TemplateView.as_view(template_name="cars/detail.html"), name="car_detail"),
	path("bookings", CustomerTemplateView.as_view(template_name="bookings/list.html"), name="my_bookings"),
	path("profile", CustomerTemplateView.as_view(template_name="profile/index.html"), name="profile"),

	# Admin
	path("admin/dashboard", AdminTemplateView.as_view(template_name="admin/dashboard.html"), name="admin_dashboard"),
	path("admin/cars", AdminTemplateView.as_view(template_name="admin/cars.html"), name="admin_cars"),
	path("admin/cars/new", AdminTemplateView.as_view(template_name="admin/car_new.html"), name="admin_car_new"),
	path("admin/bookings", AdminTemplateView.as_view(template_name="admin/bookings.html"), name="admin_bookings"),
	path("admin/staff", AdminTemplateView.as_view(template_name="admin/staff.html"), name="admin_staff"),
	path("admin/staff/new", AdminTemplateView.as_view(template_name="admin/staff_new.html"), name="admin_staff_new"),
	path("admin/sales", AdminTemplateView.as_view(template_name="admin/sales.html"), name="admin_sales"),

	# Staff
	path("staff/dashboard", StaffTemplateView.as_view(template_name="staff/dashboard.html"), name="staff_dashboard"),
]