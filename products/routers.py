from rest_framework.routers import DefaultRouter
from .views import AttributeViewSet

router = DefaultRouter()
router.register(r'products/attributes', AttributeViewSet, basename='attribute')
