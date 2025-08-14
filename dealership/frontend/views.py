from django.shortcuts import redirect
from django.views.generic import TemplateView


class RoleRequiredTemplateView(TemplateView):
	allowed_roles = None  # None means public
	login_url = "/auth/login"

	def dispatch(self, request, *args, **kwargs):  # type: ignore[override]
		if self.allowed_roles is None:
			return super().dispatch(request, *args, **kwargs)
		# Prefer authenticated Django user when present
		if request.user.is_authenticated:
			role = getattr(request.user, "role", None)
			if role in self.allowed_roles:
				return super().dispatch(request, *args, **kwargs)
			return redirect(self.login_url)
		# Fallback: lightweight cookie-based gating for preview UI
		cookie_role = request.COOKIES.get("dw_role")
		if cookie_role in self.allowed_roles:
			return super().dispatch(request, *args, **kwargs)
		return redirect(f"{self.login_url}?next={request.path}")


class CustomerTemplateView(RoleRequiredTemplateView):
	allowed_roles = {"CUSTOMER"}


class AdminTemplateView(RoleRequiredTemplateView):
	allowed_roles = {"ADMIN"}


class StaffTemplateView(RoleRequiredTemplateView):
	allowed_roles = {"SALES"}