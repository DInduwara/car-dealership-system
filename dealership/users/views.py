from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Placeholder: accept email, respond success
        email = request.data.get("email")
        if not email:
            return Response({"email": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "If this email exists, a reset link has been sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.query_params.get("token") or request.data.get("token")
        new_password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")
        if not token:
            return Response({"token": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password or not confirm_password:
            return Response({"password": "Password and confirm password are required"}, status=status.HTTP_400_BAD_REQUEST)
        if new_password != confirm_password:
            return Response({"confirm_password": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
        # Placeholder: accept reset
        return Response({"detail": "Password has been reset."})


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):  # type: ignore[override]
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer