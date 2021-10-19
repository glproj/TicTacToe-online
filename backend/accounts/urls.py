from django.urls import path
from .views import custom_user_detail

urlpatterns = [
    path('<int:pk>/', custom_user_detail)
]