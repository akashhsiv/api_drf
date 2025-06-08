from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import UserRole
from .serializers import StaffRegisterSerializer, StaffSerializer
from .permissions import IsSuperUser, IsAdminUser, IsManagerUser, CanCreateStaff

User = get_user_model()

class StaffRegisterView(APIView):
    """
    View for registering new staff members.
    Only authenticated users with proper permissions can create staff members.
    """
    permission_classes = [IsAuthenticated, CanCreateStaff]
    
    def post(self, request):
        serializer = StaffRegisterSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            staff_user = serializer.save()
            return Response(
                {
                    'message': 'Staff user created successfully',
                    'user': StaffSerializer(staff_user).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StaffListView(generics.ListAPIView):
    """
    View for listing all staff members.
    Accessible by admin and manager users.
    """
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated, (IsAdminUser | IsManagerUser)]
    
    def get_queryset(self):
        # Managers can only see cashiers they created
        if self.request.user.role and self.request.user.role.role == 'manager':
            return User.objects.filter(
                is_staff=True,
                created_by=self.request.user
            )
        # Admins can see all staff except superusers
        return User.objects.filter(is_staff=True).exclude(is_superuser=True)

class StaffDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, or deleting a staff member.
    """
    queryset = User.objects.filter(is_staff=True)
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated, (IsAdminUser | IsManagerUser)]
    lookup_field = 'id'
    
    def get_queryset(self):
        # Managers can only manage cashiers they created
        if self.request.user.role and self.request.user.role.role == 'manager':
            return User.objects.filter(
                is_staff=True,
                created_by=self.request.user
            )
        # Admins can manage all staff except superusers
        return User.objects.filter(is_staff=True).exclude(is_superuser=True)
    
    def destroy(self, request, *args, **kwargs):
        # Only allow admins to delete staff members
        if not (request.user.is_superuser or request.user.role.role == 'admin'):
            return Response(
                {'error': 'You do not have permission to perform this action'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

class RoleListView(APIView):
    """
    View for listing available roles that the current user can create.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.is_superuser:
            roles = UserRole.objects.all()
        elif request.user.role:
            allowed_roles = UserRole.ROLE_HIERARCHY.get(request.user.role.role, [])
            roles = UserRole.objects.filter(role__in=allowed_roles)
        else:
            roles = UserRole.objects.none()
            
        return Response([
            {'id': role.id, 'role': role.role, 'description': role.description}
            for role in roles
        ])
