from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Product, Attribute
from .serializers import ProductSerializer, AttributeSerializer

class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        product_id = self.kwargs.get('product_pk')
        if product_id:
            product = Product.objects.get(id=product_id)
            return product.attributes.all()
        return Attribute.objects.all()

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        attribute_id = self.kwargs.get('attribute_pk')
        if attribute_id:
            attribute = Attribute.objects.get(id=attribute_id)
            return attribute.products.all()
        return Product.objects.all()

    def perform_create(self, serializer):
        serializer.save()
