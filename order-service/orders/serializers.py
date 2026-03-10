from decimal import Decimal

from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'book_id', 'book_title', 'quantity', 'unit_price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_id',
            'shipping_address',
            'total_amount',
            'status',
            'created_at',
            'items',
        ]

    def get_shipping_address(self, obj):
        return {
            'line1': obj.shipping_line1,
            'line2': obj.shipping_line2,
            'city': obj.shipping_city,
            'state': obj.shipping_state,
            'postal_code': obj.shipping_postal_code,
            'country': obj.shipping_country,
        }


class CreateOrderItemSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    book_title = serializers.CharField(required=False, allow_blank=True, default='')
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))


class CreateOrderSerializer(serializers.Serializer):
    items = CreateOrderItemSerializer(many=True)
    shipping_address = serializers.DictField()

    def validate_shipping_address(self, value):
        required_fields = ['line1', 'city', 'country']
        for field in required_fields:
            field_value = value.get(field, '')
            if not isinstance(field_value, str) or not field_value.strip():
                raise serializers.ValidationError(f'{field} is required')

        normalized = {
            'line1': str(value.get('line1', '')).strip(),
            'line2': str(value.get('line2', '')).strip(),
            'city': str(value.get('city', '')).strip(),
            'state': str(value.get('state', '')).strip(),
            'postal_code': str(value.get('postal_code', '')).strip(),
            'country': str(value.get('country', '')).strip(),
        }
        return normalized
