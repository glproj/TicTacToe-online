from rest_framework import serializers
from django.contrib.auth import get_user_model


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "date_joined")
        read_only_fields = ("date_joined", "password", "is_active", "is_staff")
