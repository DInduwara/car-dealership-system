from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(write_only=True)
    accept_terms = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "full_name",
            "accept_terms",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if not attrs.get("accept_terms"):
            raise serializers.ValidationError({"accept_terms": "You must accept the Terms to create an account."})
        return attrs

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        full_name = validated_data.pop("full_name", "").strip()
        validated_data.pop("accept_terms", None)
        # Force CUSTOMER role and derive names
        if full_name:
            parts = full_name.split(" ")
            validated_data["first_name"] = parts[0]
            validated_data["last_name"] = " ".join(parts[1:]) if len(parts) > 1 else ""
        if not validated_data.get("username") and validated_data.get("email"):
            validated_data["username"] = validated_data["email"]
        user = User.objects.create_user(**validated_data, role=User.Roles.CUSTOMER)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "phone", "role"]
        read_only_fields = ["id", "role"]