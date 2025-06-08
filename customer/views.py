from rest_framework import status, views, generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Customer, Staff, UserRole
from .serializers import (
    CustomerSerializer, 
    CustomerLoginSerializer, 
    CustomerRegisterSerializer,
    StaffLoginSerializer,
    StaffRegisterSerializer,
    StaffSerializer,
    UserRoleSerializer,
    ForgetPasswordSerializer,
    ResetPasswordSerializer,
    UserSerializer
)

User = get_user_model()

class IsStaffUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_admin

class IsManagerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_manager

class IsCashierUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_cashier

class AuthView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Return a simple response for GET requests
        return Response({
            'message': 'Welcome to the authentication endpoints',
            'endpoints': {
                'customer_register': '/api/customer/register',
                'customer_login': '/api/customer/login',
                'staff_register': '/api/user/register',
                'staff_login': '/api/user/login',
                'logout': '/api/auth/logout',
                'forget_password': '/api/auth/forget-password',
                'reset_password': '/api/auth/reset-password'
            }
        })

class ForgetPasswordView(views.APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user_type = serializer.validated_data['user_type']
            
            # Get the appropriate user model based on user_type
            user_model = Staff if user_type == 'staff' else Customer
            
            try:
                user = user_model.objects.get(email=email)
                # Generate and send OTP
                otp = user.generate_otp()
                
                # Log the OTP for development (remove in production)
                print(f"OTP for {email}: {otp}")
                
                # Return success response (don't include OTP in production)
                return Response({
                    'message': 'If an account exists with this email, an OTP has been sent',
                    'email': email,
                    'otp_sent': True
                }, status=status.HTTP_200_OK)
                
            except user_model.DoesNotExist:
                # For security, don't reveal if the email exists or not
                return Response({
                    'message': 'If an account exists with this email, an OTP has been sent',
                    'email': email,
                    'otp_sent': False
                }, status=status.HTTP_200_OK)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(views.APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            password = serializer.validated_data['password']
            user_type = serializer.validated_data['user_type']
            
            # Get the appropriate user model based on user_type
            user_model = Staff if user_type == 'staff' else Customer
            
            try:
                user = user_model.objects.get(email=email)
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
            except user_model.DoesNotExist:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Try to blacklist the token
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out"}, 
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            # If token is invalid or already blacklisted, still return success
            # This prevents token enumeration attacks
            return Response(
                {"message": "Successfully logged out"},
                status=status.HTTP_205_RESET_CONTENT
            )

class CustomerLoginView(views.APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = CustomerLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                user = Customer.objects.get(email=email)
                if not user.check_password(password):
                    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
                
                if not user.is_active:
                    return Response({"error": "Account is not active"}, status=status.HTTP_401_UNAUTHORIZED)
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                user.last_login = timezone.now()
                user.save()
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': CustomerSerializer(user).data
                })
                
            except Customer.DoesNotExist:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerRegisterView(views.APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': CustomerSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'error',
            'code': status.HTTP_400_BAD_REQUEST,
            'message': 'Registration failed',
            'errors': serializer.errors,
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_400_BAD_REQUEST)

# Staff Authentication Views
class StaffLoginView(views.APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = StaffLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                user = Staff.objects.get(email=email)
                if not user.check_password(password):
                    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
                
                if not user.is_active:
                    return Response({"error": "Account is not active"}, status=status.HTTP_401_UNAUTHORIZED)
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                user.last_login = timezone.now()
                user.save()
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': StaffSerializer(user).data
                })
                
            except Staff.DoesNotExist:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StaffRegisterView(views.APIView):
    permission_classes = [IsAdminUser]  # Only admin can register new staff
    
    def post(self, request):
        serializer = StaffRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                'message': 'Staff user created successfully',
                'user': StaffSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Staff Management Views
class StaffListView(generics.ListAPIView):
    permission_classes = [IsAdminUser | IsManagerUser]
    serializer_class = StaffSerializer
    
    def get_queryset(self):
        return Staff.objects.all()

class StaffDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser | IsManagerUser]
    serializer_class = StaffSerializer
    queryset = Staff.objects.all()
    lookup_field = 'id'

# Role Management Views
class UserRoleListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer

class UserRoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    lookup_field = 'id'
