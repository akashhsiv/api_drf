# Authentication & User Management API Documentation

This document provides detailed information about the authentication and user management endpoints available in the system, including role-based access control for staff users.

## Table of Contents
1. [Customer Authentication](#customer-authentication)
   - [Customer Registration](#customer-registration)
   - [Customer Login](#customer-login)

2. [Staff Authentication](#staff-authentication)
   - [Staff Login](#staff-login)
   - [Create Staff](#create-staff)
   - [List Staff](#list-staff)
   - [Staff Details](#staff-details)
   - [Available Roles](#available-roles)

3. [Common Authentication](#common-authentication)
   - [Logout](#logout)
   - [Forget Password](#forget-password)
   - [Reset Password](#reset-password)
   - [Token Refresh](#token-refresh)

4. [Role Hierarchy](#role-hierarchy)
5. [Error Handling](#error-handling)

## Role Hierarchy
Before using the API, understand the role hierarchy:
- **Superuser**: Can create any role (admin, manager, cashier)
- **Admin**: Can create managers and cashiers
- **Manager**: Can create cashiers
- **Cashier**: Cannot create other users
- **Customer**: Regular user with no staff privileges

## Customer Authentication

### Customer Registration

Register a new customer account. No authentication required.

**Endpoint**: `POST /api/customer/register/`

**Required Fields**:
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123",
}
```

**Optional Fields**:
- `phone_number`: String (e.g., "+1234567890")
- `address`: String (e.g., "123 Main St, City")

**Response (Success - 201 Created)**:
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "user_type": "customer",
        "is_active": true,
        "date_joined": "2025-06-07T13:05:00Z",
        "last_login": null,
        "phone_number": "+1234567890",
        "address": "123 Main St, City"
    }
}
```

### Customer Login

Authenticate a customer and retrieve access and refresh tokens.

**Endpoint**: `POST /api/customer/login/`

**Request Body**:
```json
{
    "email": "john@example.com",
    "password": "securepassword123"
}
```

**Response (Success - 200 OK)**:
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "user_type": "customer",
        "is_active": true,
        "date_joined": "2025-06-07T13:05:00Z",
        "last_login": "2025-06-07T14:30:00Z",
        "phone_number": "+1234567890",
        "address": "123 Main St, City"
    }
}
```

## Staff Authentication

### Staff Login

Authenticate a staff member and retrieve access and refresh tokens.

**Endpoint**: `POST /api/user/login/`

**Request Body**:
```json
{
    "email": "jane@example.com",
    "password": "staffpassword123"
}
```

**Response (Success - 200 OK)**:
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 2,
        "name": "Jane Manager",
        "email": "jane@example.com",
        "user_type": "staff",
        "is_active": true,
        "is_staff": true,
        "date_joined": "2025-06-07T14:00:00Z",
        "last_login": "2025-06-07T15:30:00Z",
        "role": {
            "id": 2,
            "role": "manager",
            "description": "Manager role with extended permissions"
        }
    }
}
```

## Common Authentication

### Logout

Invalidate the provided refresh token.

**Endpoint**: `POST /api/auth/logout/`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (Success - 205 Reset Content)**:
```json
{
    "message": "Successfully logged out"
}
```

### Forget Password

Request a password reset OTP for a user.

**Endpoint**: `POST /api/auth/forget-password/`

**Request Body**:
```json
{
    "email": "user@example.com",
    "user_type": "customer"
}
```

**Response (Success - 200 OK)**:
```json
{
    "message": "OTP has been sent to your email"
}
```

### Reset Password

Reset password using the OTP received via email.

**Endpoint**: `POST /api/auth/reset-password/`

**Request Body**:
```json
{
    "email": "user@example.com",
    "otp": "123456",
    "new_password": "newsecurepassword123",
    "confirm_password": "newsecurepassword123"
}
```

**Response (Success - 200 OK)**:
```json
{
    "message": "Password has been reset successfully"
}
```

### Token Refresh

Get a new access token using a valid refresh token.

**Endpoint**: `POST /api/auth/token/refresh/`

**Request Body**:
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (Success - 200 OK)**:
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Staff Management

### Create Staff

Create a new staff user. Requires authentication and appropriate permissions based on role hierarchy.

**Endpoint**: `POST /api/user/register/`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Request Body**:
```json


```

**Response (Success - 201 Created)**:
```json
{
    "message": "Staff user created successfully",
    "user": {
        "id": 3,
        "name": "New Staff",
        "email": "new.staff@example.com",
        "user_type": "staff",
        "is_active": true,
        "is_staff": true,
        "date_joined": "2025-06-07T16:00:00Z",
        "last_login": null,
        "role": {
            "id": 3,
            "role": "cashier",
            "description": "Cashier role with basic permissions"
        },
        "created_by": 2
    }
}
```

### List Staff

List all staff users. Accessible by admin and manager users.

**Endpoint**: `GET /api/user/`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response (Success - 200 OK)**:
```json
[
    {
        "id": 2,
        "name": "Jane Manager",
        "email": "jane@example.com",
        "user_type": "staff",
        "is_active": true,
        "is_staff": true,
        "date_joined": "2025-06-07T14:00:00Z",
        "last_login": "2025-06-07T15:30:00Z",
        "role": {
            "id": 2,
            "role": "manager",
            "description": "Manager role with extended permissions"
        },
        "created_by": 1
    },
    {
        "id": 3,
        "name": "New Staff",
        "email": "new.staff@example.com",
        "user_type": "staff",
        "is_active": true,
        "is_staff": true,
        "date_joined": "2025-06-07T16:00:00Z",
        "last_login": null,
        "role": {
            "id": 3,
            "role": "cashier",
            "description": "Cashier role with basic permissions"
        },
        "created_by": 2
    }
]
```

### Staff Details

Retrieve, update, or delete a staff user. Accessible by admin and manager users.

**Endpoint**: `GET|PUT|PATCH|DELETE /api/user/{id}/`

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Response (Success - 200 OK for GET)**:
```json
{
    "id": 3,
    "name": "Updated Staff",
    "email": "updated.staff@example.com",
    "user_type": "staff",
    "is_active": true,
    "is_staff": true,
    "date_joined": "2025-06-07T16:00:00Z",
    "last_login": "2025-06-07T17:00:00Z",
    "role": {
        "id": 3,
        "role": "cashier",
        "description": "Cashier role with basic permissions"
    },
    "created_by": 2,
    "created_at": "2025-06-07T16:00:00Z",
    "updated_at": "2025-06-07T17:30:00Z"
}
```

### Available Roles

List all available roles that the current user can assign.

**Endpoint**: `GET /api/user/roles/`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response (Success - 200 OK)**:
```json
[
    {
        "id": 1,
        "role": "admin",
        "description": "Administrator with full access"
    },
    {
        "id": 2,
        "role": "manager",
        "description": "Manager with limited admin access"
    },
    {
        "id": 3,
        "role": "cashier",
        "description": "Cashier with basic access"
    }
]
```

## Error Handling

### Common Error Responses

**400 Bad Request**: Invalid input data
```json
{
    "field_name": [
        "This field is required."
    ]
}
```

**401 Unauthorized**: Missing or invalid authentication
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden**: Insufficient permissions
```json
{
    "detail": "You do not have permission to perform this action."
}
```

**404 Not Found**: Resource not found
```json
{
    "detail": "Not found."
}
```

### Role-based Access Control Errors

When trying to create a user with an unauthorized role:
```json
{
    "role_id": [
        "You can only create users with these roles: manager, cashier"
    ]
}
```

## Rate Limiting

- Authentication endpoints: 100 requests per hour per IP
- Staff management endpoints: 200 requests per hour per user
- Password reset endpoints: 5 requests per hour per IP

## Security Considerations

- Always use HTTPS in production
- Store refresh tokens securely (httpOnly, Secure, SameSite=Strict)
- Implement proper password policies
- Regularly rotate API keys and secrets
- Monitor and log authentication attempts

## Versioning

API versioning is handled through the URL path (e.g., `/api/v1/...`). The current version is v1.

## Support

For support, please contact support@example.com or visit our [support portal](https://support.example.com).

## Customer Registration

Register a new customer account.

**Endpoint**: `POST /api/customer/register/`

**Request Body**:
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "phone_number": "+1234567890",
    "address": "123 Main St, City"
}
```

**Response (Success - 201 Created)**:
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "user_type": "customer",
        "is_active": true,
        "date_joined": "2025-06-07T13:05:00Z",
        "last_login": null,
        "phone_number": "+1234567890",
        "address": "123 Main St, City"
    }
}
```

## Customer Login

Authenticate a customer and retrieve access and refresh tokens.

**Endpoint**: `POST /api/customer/login/`

**Request Body**:
```json
{
    "email": "john@example.com",
    "password": "securepassword123"
}
```

**Response (Success - 200 OK)**:
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "user_type": "customer",
        "is_active": true,
        "date_joined": "2025-06-07T13:05:00Z",
        "last_login": "2025-06-07T14:30:00Z",
        "phone_number": "+1234567890",
        "address": "123 Main St, City"
    }
}
```

## Staff Registration

Register a new staff account. (Admin only)

**Endpoint**: `POST /api/user/register/`

**Headers**:
```
Authorization: Bearer <admin_access_token>
```

**Request Body**:
```json
{
    "name": "Jane Manager",
    "email": "jane@example.com",
    "password": "staffpassword123",
    "password_confirm": "staffpassword123",
    "role_id": 2
}
```

**Response (Success - 201 Created)**:
```json
{
    "message": "Staff user created successfully",
    "user": {
        "id": 2,
        "name": "Jane Manager",
        "email": "jane@example.com",
        "user_type": "staff",
        "is_active": true,
        "is_staff": true,
        "date_joined": "2025-06-07T14:00:00Z",
        "last_login": null,
        "role": {
            "id": 2,
            "role": "manager",
            "description": "Manager role with extended permissions"
        }
    }
}
```

## Staff Login

Authenticate a staff member and retrieve access and refresh tokens.

**Endpoint**: `POST /api/user/login/`

**Request Body**:
```json
{
    "email": "jane@example.com",
    "password": "staffpassword123"
}
```

**Response (Success - 200 OK)**:
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 2,
        "name": "Jane Manager",
        "email": "jane@example.com",
        "user_type": "staff",
        "is_active": true,
        "is_staff": true,
        "date_joined": "2025-06-07T14:00:00Z",
        "last_login": "2025-06-07T15:30:00Z",
        "role": {
            "id": 2,
            "role": "manager",
            "description": "Manager role with extended permissions"
        }
    }
}
```

## Logout

Invalidate the provided refresh token.

**Endpoint**: `POST /api/auth/logout/`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (Success - 205 Reset Content)**:
```json
{
    "message": "Successfully logged out"
}
```

## Forget Password

Request a password reset OTP for a user.

**Endpoint**: `POST /api/auth/forget-password/`

**Request Body**:
```json
{
    "email": "john@example.com",
    "user_type": "customer"
}
```

**Response (Success - 200 OK)**:
```json
{
    "message": "OTP sent successfully",
    "otp": "123456"
}
```

## Reset Password

Reset password using the OTP received via email.

**Endpoint**: `POST /api/auth/reset-password/`

**Request Body**:
```json
{
    "email": "john@example.com",
    "otp": "123456",
    "password": "newsecurepassword123",
    "confirm_password": "newsecurepassword123",
    "user_type": "customer"
}
```

**Response (Success - 200 OK)**:
```json
{
    "message": "Password reset successfully"
}
```

## Token Refresh

Get a new access token using a valid refresh token.

**Endpoint**: `POST /api/auth/token/refresh/`

**Request Body**:
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (Success - 200 OK)**:
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "Invalid input data",
    "details": {
        "field_name": ["Error message"]
    }
}
```

### 401 Unauthorized
```json
{
    "error": "Invalid credentials"
}
```

### 403 Forbidden
```json
{
    "error": "You do not have permission to perform this action"
}
```

### 404 Not Found
```json
{
    "error": "User not found"
}
```

## Rate Limiting

- Authentication endpoints are rate-limited to prevent abuse
- Default rate: 5 requests per minute per IP address
- Exceeding the limit will result in a 429 Too Many Requests response
