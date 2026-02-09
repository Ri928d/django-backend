from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.views import APIView
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

from .serializers import (
    RegisterSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class PasswordResetView(APIView):
    authentication_classes = []
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = (
            User.objects.filter(email=serializer.validated_data["email"])
            .order_by("id")
            .first()
        )
        if not user:
            return Response(
                {"message": "If email exists, reset link sent"},
                status=status.HTTP_200_OK,
            )

        # Create token
        from .models import PasswordResetToken

        token_obj = PasswordResetToken.objects.create(user=user)

        # Send email
        reset_url = (
            f"{os.getenv('FRONTEND_URL')}/reset-password?token={token_obj.token}"
        )

        message = Mail(
            from_email=os.getenv("DEFAULT_FROM_EMAIL"),
            to_emails=user.email,
            subject="Reset Your Password",
            html_content=f'<a href="{reset_url}">Click to reset password</a>',
        )

        try:
            sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
            sg.send(message)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({"message": "Reset email sent"}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from .models import PasswordResetToken

        try:
            token_obj = PasswordResetToken.objects.get(
                token=serializer.validated_data["token"]
            )
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not token_obj.is_valid():
            token_obj.delete()
            return Response(
                {"error": "Token expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = token_obj.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        token_obj.delete()

        return Response(
            {"message": "Password reset successful"}, status=status.HTTP_200_OK
        )
