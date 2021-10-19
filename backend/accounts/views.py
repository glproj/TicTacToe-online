from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from accounts.serializers import CustomUserSerializer
from rest_framework import status

User = get_user_model()


@api_view(["GET", "PUT", "DELETE"])
def custom_user_detail(request, pk):
    """
    Retrieve, update and create user detail.
    """
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serialized_user = CustomUserSerializer(user)
        return Response(serialized_user.data)
    elif request.method == "PUT":
        updated_user_serialized = CustomUserSerializer(user, data=request.data, partial=True)

        if updated_user_serialized.is_valid():
            updated_user_serialized.save()
            return Response(updated_user_serialized.data)
        return Response(
            updated_user_serialized.errors, status=status.HTTP_400_BAD_REQUEST
        )
    elif request.method == "DELETE":
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
