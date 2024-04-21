import random

from django.shortcuts import redirect
from django.views import View
from rest_framework import status, generics, permissions
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import CustomUser
from .serializers import UserSerializer
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .task_1 import send_signup_verification, send_signup_email, send_login_verification

import random


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=False)  # User inactive until verification
            # Generate random 8-digit verification code
            verification_code = ''.join(str(random.randint(0, 9)) for _ in range(8))

            # Save verification code to the user object
            user.verification_code = verification_code
            user.save()  # Save user with verification code before sending email

            # Send signup verification email with celery task
            send_signup_verification.delay(user.pk, verification_code)

            return Response(
                {'message': 'A verification code has been sent to your email. Please verify to complete signup.'},
                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserVerificationView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        verification_code = request.data.get('verification_code')

        user = get_object_or_404(CustomUser, email=email)

        user.is_active = True  # Activate user upon successful verification
        user.save()

        # Send welcome email with celery task (optional)
        send_signup_email.delay(user.pk)
        response_data = {'message': 'Signup verification successful'}
        return Response(response_data, status=status.HTTP_200_OK)


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)  # Validate email format
        except ValidationError:
            return Response({'error': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)
        if user is not None:
            verification_code = ''.join(str(random.randint(0, 9)) for _ in range(8))
            user.login_verification_code = verification_code
            user.save()
            # Call the Celery task to send the login verification code asynchronously
            send_login_verification.apply_async(args=[user.id, verification_code])
            return Response({'message': 'Verification code sent successfully'}, status=status.HTTP_200_OK)

        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


# Login verification view (assuming similar logic to UserVerificationView)
# Login verification view
class LoginVerificationView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        verification_code = request.data.get('verification_code')

        user = get_object_or_404(CustomUser, email=email)
        if verification_code == user.login_verification_code:
            # Clear the login verification code after successful verification
            user.login_verification_code = None
            user.save()

            # Log in the user
            login(request, user)

            # Generate token for login
            # Generate access token and refresh token
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login verification successful',
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])  # Use an empty list to disable JWT and session authentication
def check_auth(request):
    user = request.user
    return Response({'authenticated': True})
