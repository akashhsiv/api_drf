from django.urls import path
from .views import AuthView

urlpatterns = [
    path('register', AuthView.as_view(), name='register'),
    path('login', AuthView.as_view(), name='login'),
]
