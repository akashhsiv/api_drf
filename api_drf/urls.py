from django.contrib import admin
from django.urls import path, include
from api.views import AuthView
from products.routers import router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register', AuthView.as_view(), name='register'),
    path('api/login', AuthView.as_view(), name='login'),
    path('api/logout', AuthView.as_view(), name='logout'),
    path('api/forget_password', AuthView.as_view(), name='forget_password'),
    path('api/reset_password', AuthView.as_view(), name='reset_password'),
    path('api/', include(router.urls)),
]
