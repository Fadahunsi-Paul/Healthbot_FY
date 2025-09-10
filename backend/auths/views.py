from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi 
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, views, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny 
from rest_framework.validators import ValidationError
from rest_framework.decorators import action
from django.utils.translation import gettext_lazy as _
from .serializer import *
from .models import UserProfile
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import Util, user_email, generate_six_digit_code, send_reset_code
from .models import ResetPassword
from datetime import datetime, timedelta
import jwt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import requests
# from google.oauth2 import id_token  
from rest_framework import permissions
# from google.auth.transport import requests as google_requests
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

User = get_user_model()

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Missing refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as exc:
            return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            email = data.get("email", "").lower().strip()
            password = data.get("password", "").strip()
            confirm_password = data.get("confirm_password", "").strip()
            if not all([email, password, confirm_password, first_name, last_name]):
                return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email=email).exists():
                return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            if password != confirm_password:
                return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                is_verified=False, 
            )
            user_email(request, user)
            return Response({
                    "message": "Registration successful! Please check your email to verify your account.",
                "user": {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_verified": user.is_verified,
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Registration error:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get("email", "").lower().strip()
            password = request.data.get("password", "").strip()
            print(f"Login attempt - Email: {email}, Password Provided: {'Yes' if password else 'No'}")
            if not email or not password:
                print("Missing email or password")
                return Response({"error": "Email and password are required"}, status=400)
            try:
                user_exists = User.objects.get(email=email)
                print(f"User exists: {user_exists.email}, Verified: {user_exists.is_verified}, Active: {user_exists.is_active}")
            except User.DoesNotExist:
                print(f"No user found with email: {email}")
                return Response({"error": "Invalid credentials"}, status=401)
            user = authenticate(request, username=email, password=password)

            if not user:
                print(f"Authentication failed for email: {email}")
                print("This could mean wrong password or user is not active")
                return Response({"error": "Invalid credentials"}, status=401)

            print(f"Authentication successful: {user.email}")
            if not user.is_active:
                print("User account not active")
                return Response({"error": "Account not active"}, status=401)

            refresh = RefreshToken.for_user(user)

            print("Login successful. Returning tokens.")

            return Response({
                    "message": "Login successful",
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                "user": {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_verified": user.is_verified,
                }
            }, status=200)

        except Exception as e:
            print(f"Login error: {str(e)}")
            return Response({"error": "Login failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def logout(self, request):
        logout(request)
        return Response({"Message": _("Logout Successful")}, status=status.HTTP_200_OK)

class VerifyEmailViewSet(viewsets.GenericViewSet):
    serializer_class = VerifyEmailSerializer
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'token',
                openapi.IN_QUERY,
                description="JWT token for email verification",
                type=openapi.TYPE_STRING
            )
        ]
    )
    @action(methods=['get'], detail=False)
    def verify(self, request):
        token = request.GET.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            email_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=email_token['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.is_active = True  # Also activate the user
                user.save()
                print(f"User {user.email} verified and activated successfully")
            return Response({'message': 'User is successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Email activation link has expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def generate_token(user):
        expiration = datetime.utcnow() + timedelta(hours=24)
        payload = {
            'user_id': user.id,
            'exp': expiration,
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token

class RequestPasswordResetEmail(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RequestPasswordSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid input'}, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data
        email = validated_data.get('email') 
        try:
            user = User.objects.get(email=email)
            code = generate_six_digit_code()
            ResetPassword.objects.create(user=user, code=code)
            
            # Only send email in production
            if not settings.DEBUG:
                send_reset_code(user, code)
            else:
                print(f"Development mode: Reset code for {email} is {code}")
                
        except ObjectDoesNotExist:
            pass

        return Response({'message': 'If your email is registered, a reset code has been sent.'}, status=status.HTTP_200_OK)


class VerifyPasswordReset(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer
    def post(self, request):
        print(f"Password reset request data: {request.data}")       
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            print(f"Password reset validation errors: {serializer.errors}")          
            errors = serializer.errors
            if 'new_password' in errors:
                password_errors = errors['new_password']
                user_friendly_errors = []               
                for error in password_errors:
                    if 'too short' in str(error).lower():
                        user_friendly_errors.append('This password is too short. It must contain at least 8 characters.')
                    elif 'too common' in str(error).lower():
                        user_friendly_errors.append('This password is too common.')
                    elif 'numeric' in str(error).lower():
                        user_friendly_errors.append('This password is entirely numeric.')
                    elif 'similar' in str(error).lower():
                        user_friendly_errors.append('This password is too similar to your personal information.')
                    else:
                        user_friendly_errors.append(str(error))                
                return Response({'error': user_friendly_errors[0] if user_friendly_errors else 'Invalid password.'}, status=status.HTTP_400_BAD_REQUEST)           
            return Response({'error': 'Invalid input data.'}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data  # type: ignore
        email = validated_data['email']
        code = validated_data['code']
        new_password = validated_data['new_password']
        
        print(f"Password reset validated data - Email: {email}, Code: {code}")

        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            return Response({'error': 'Invalid email or code.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reset_code = ResetPassword.objects.get(user=user, code=code)
        except ObjectDoesNotExist:
            return Response({'error': 'Invalid email or code.'}, status=status.HTTP_400_BAD_REQUEST)
        if not reset_code.is_valid():
            return Response({'error': 'Reset code has expired.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        reset_code.delete()
        return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)


class ProfileUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        """Get complete user profile data"""
        try:
            user = request.user
            profile, created = UserProfile.objects.get_or_create(user=user)
            serializer = CompleteUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Profile get error: {str(e)}")
            return Response({"error": "Failed to retrieve profile"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def put(self, request):
        """Update complete user profile data"""
        try:
            user = request.user
            data = request.data            
            if 'first_name' in data:
                user.first_name = data['first_name'].strip()
            if 'last_name' in data:
                user.last_name = data['last_name'].strip()
            if 'email' in data:
                new_email = data['email'].lower().strip()
                if new_email != user.email:
                    if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                        return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
                    user.email = new_email
                    user.is_verified = False
            user.save()            
            profile, created = UserProfile.objects.get_or_create(user=user)            
            profile_fields = [
                'phone', 'date_of_birth', 'address', 'emergency_contact',
                'medical_conditions', 'allergies', 'medications', 'blood_type',
                'height', 'weight', 'email_notifications', 'push_notifications',
                'health_reminders', 'appointment_reminders', 'share_health_data',
                'allow_analytics', 'public_profile'
            ]
            for field in profile_fields:
                if field in data:
                    value = data[field]
                    if field == 'date_of_birth' and value == '':
                        value = None
                    elif isinstance(value, str) and value.strip() == '' and field not in ['email_notifications', 'push_notifications', 'health_reminders', 'appointment_reminders', 'share_health_data', 'allow_analytics', 'public_profile']:
                        value = None
                    setattr(profile, field, value)
            profile.save()            
            serializer = CompleteUserSerializer(user)
            return Response({
                "message": "Profile updated successfully",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Profile update error: {str(e)}")
            return Response({"error": "Profile update failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)