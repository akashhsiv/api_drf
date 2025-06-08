from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Customer, Staff, UserRole

User = get_user_model()

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', 'role', 'description']
        read_only_fields = ['id']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'user_type', 'is_active', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']

class CustomerSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = Customer
        fields = UserSerializer.Meta.fields + ['phone_number', 'address']
        extra_kwargs = {'password': {'write_only': True}}

class StaffSerializer(UserSerializer):
    role = UserRoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=UserRole.objects.all(),
        source='role',
        write_only=True,
        required=False
    )
    
    class Meta(UserSerializer.Meta):
        model = Staff
        fields = UserSerializer.Meta.fields + ['role', 'role_id', 'is_staff']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        role = validated_data.pop('role', None)
        user = Staff.objects.create_staff(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data.get('password'),
            role=role
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES, default='customer')

class CustomerLoginSerializer(UserLoginSerializer):
    user_type = serializers.HiddenField(default='customer')

class StaffLoginSerializer(UserLoginSerializer):
    user_type = serializers.HiddenField(default='staff')

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class CustomerRegisterSerializer(UserRegisterSerializer):
    class Meta(UserRegisterSerializer.Meta):
        model = Customer
        fields = UserRegisterSerializer.Meta.fields + ['phone_number', 'address']
    
    def create(self, validated_data):
        return Customer.objects.create_customer(**validated_data)

class StaffRegisterSerializer(UserRegisterSerializer):
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=UserRole.objects.all(),
        source='role',
        required=True,
        write_only=True
    )
    
    class Meta(UserRegisterSerializer.Meta):
        model = Staff
        fields = UserRegisterSerializer.Meta.fields + ['role_id']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate(self, data):
        data = super().validate(data)
        request = self.context.get('request')
        
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError({"role_id": "Authentication required to create staff users"})
        
        role = data.get('role')
        creator = request.user
        
        # Superuser can create any role
        if creator.is_superuser:
            return data
            
        # Regular users can't create staff
        if not creator.is_staff or not creator.role:
            raise serializers.ValidationError({"role_id": "Insufficient permissions"})
            
        # Check role hierarchy
        allowed_roles = UserRole.ROLE_HIERARCHY.get(creator.role.role, [])
        if role.role not in allowed_roles:
            raise serializers.ValidationError({
                "role_id": f"You can only create users with these roles: {', '.join(allowed_roles)}"
            })
            
        return data
    
    def create(self, validated_data):
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        validated_data.pop('password_confirm', None)
        
        # Extract name and email to avoid passing them twice
        name = validated_data.pop('name')
        email = validated_data.pop('email')
        
        user = Staff.objects.create_staff(
            email=email,
            name=name,
            password=password,
            role=role,
            created_by=self.context['request'].user,
            **validated_data  # Only pass remaining fields
        )
        return user

class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES, default='customer')

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES, default='customer')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
