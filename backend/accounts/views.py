from django.contrib.auth import get_user_model
from accounts.serializers import CustomUserSerializer
from .models import CustomUser
from rest_framework import viewsets
User = get_user_model()

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer