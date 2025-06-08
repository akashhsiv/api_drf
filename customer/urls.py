from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views_staff import StaffRegisterView, StaffListView, StaffDetailView, RoleListView

urlpatterns = [
    # Authentication endpoints
    path('', views.AuthView.as_view(), name='auth'),
    
    # Customer endpoints
    path('customer/register/', views.CustomerRegisterView.as_view(), name='customer-register'),
    path('customer/login/', views.CustomerLoginView.as_view(), name='customer-login'),
    
    # User management endpoints (for staff)
    path('user/register/', StaffRegisterView.as_view(), name='user-register'),
    path('user/', StaffListView.as_view(), name='user-list'),
    path('user/<int:id>/', StaffDetailView.as_view(), name='user-detail'),
    path('user/roles/', RoleListView.as_view(), name='role-list'),
    
    # Common auth endpoints
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/forget-password/', views.ForgetPasswordView.as_view(), name='forget-password'),
    path('auth/reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Backward compatibility
    path('user/login/', views.StaffLoginView.as_view(), name='staff-login'),
    path('roles/<int:id>/', views.UserRoleDetailView.as_view(), name='role-detail'),
]
