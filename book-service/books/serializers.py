from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Price must be non-negative.')
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('Stock must be non-negative.')
        return value

    def validate_category_id(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError('category_id must be a positive integer.')
        return value

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'stock', 'category_id']
