from rest_framework import serializers
from .models import Product, Attribute

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'name', 'description', 'values']

class ProductSerializer(serializers.ModelSerializer):
    attributes = AttributeSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'status', 'attributes']
        read_only_fields = ['slug']

    def create(self, validated_data):
        attributes_data = validated_data.pop('attributes', [])
        product = Product.objects.create(**validated_data)
        if attributes_data:
            for attribute_data in attributes_data:
                try:
                    attribute = Attribute.objects.get(id=attribute_data['id'])
                    product.attributes.add(attribute)
                except (Attribute.DoesNotExist, KeyError):
                    pass
        return product

    def update(self, instance, validated_data):
        attributes_data = validated_data.pop('attributes', [])
        instance = super().update(instance, validated_data)
        
        # Clear existing attributes
        instance.attributes.clear()
        
        # Add new attributes
        if attributes_data:
            for attribute_data in attributes_data:
                try:
                    attribute = Attribute.objects.get(id=attribute_data['id'])
                    instance.attributes.add(attribute)
                except (Attribute.DoesNotExist, KeyError):
                    pass
        
        return instance
