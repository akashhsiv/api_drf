from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from .serializers import (
    UserSerializer, 
    UserLoginSerializer, 
    UserRegisterSerializer,
    ForgetPasswordSerializer,
    ResetPasswordSerializer
)

class AuthView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Return a simple response for GET requests
        return Response({
            'message': 'Welcome to the authentication endpoints',
            'endpoints': {
                'register': '/api/register/',
                'login': '/api/login/',
                'logout': '/api/logout/',
                'forget_password': '/api/forget_password/',
                'reset_password': '/api/reset_password/'
            }
        })

    def post(self, request):
        if request.path.endswith('register'):
            return self.register(request)
        elif request.path.endswith('login'):
            return self.login(request)
        elif request.path.endswith('logout'):
            return self.logout(request)
        elif request.path.endswith('forget_password'):
            return self.forget_password(request)
        elif request.path.endswith('reset_password'):
            return self.reset_password(request)
        return Response({'error': 'Invalid endpoint'}, status=status.HTTP_400_BAD_REQUEST)

    def forget_password(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                # Generate OTP
                otp = user.generate_otp()
                # In a real application, you would send this OTP via SMS or email
                # For now, we'll just return it in the response for testing
                return Response({
                    'message': 'OTP sent successfully',
                    'otp': otp  # Remove in production
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({
                    'message': 'If an account exists with this email, an OTP has been sent'
                }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(email=email)
                if not user.is_otp_valid(otp):
                    return Response({
                        'error': 'Invalid or expired OTP'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Reset password
                user.set_password(password)
                user.clear_otp()
                user.save()
                return Response({
                    'message': 'Password reset successfully'
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # First validate the token
                token = RefreshToken(refresh_token)
                if token.check_blacklist():
                    return Response({"error": "Token is already blacklisted"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Then blacklist it
                token.blacklist()
                return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
            except Exception as e:
                # If token is invalid or expired, still consider it logged out
                return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def register(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.filter(email=serializer.validated_data['email']).first()
        if user and user.check_password(serializer.validated_data['password']):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
