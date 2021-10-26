from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from restbucks.models import Product, ProductAttribute, ProductAttributeOption, Order, OrderItem

class ProductAttributeSerializer(serializers.ModelSerializer):
    options = SerializerMethodField()

    class Meta:
        fields = ['name', 'options']
        model = ProductAttribute

    def get_options(self, obj):
        return [opt.name for opt in obj.options.all()]

class ProductAttributeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name']
        model = ProductAttributeOption

class ProductSerializer(serializers.ModelSerializer):
    attributes = ProductAttributeSerializer(source='optional_attributes', many=True)

    class Meta:
        fields = ['product_name', 'unit_price', 'attributes']
        model = Product

class ItemAttributeOptionSerializer(serializers.ModelSerializer):
    name = SerializerMethodField(source='attribute')
    value = serializers.CharField(source='name')

    class Meta:
        fields = ['name', 'value']
        model = ProductAttributeOption

    def get_name(self, obj):
        return obj.attribute.name

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    selected_options = ItemAttributeOptionSerializer(many=True)

    class Meta:
        exclude = ['order']
        model = OrderItem


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = SerializerMethodField()

    class Meta:
        fields = ['id', 'customer', 'items', 'total_price', 'state']
        model = Order

    def get_customer(self, obj):
        return obj.customer.username
        
