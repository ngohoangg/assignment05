import os

import requests
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import (
    AddCartItemSerializer,
    CartItemSerializer,
    CartSerializer,
    UpdateCartItemQuantitySerializer,
)


DEFAULT_BOOK_SERVICE_URLS = [
    'http://localhost:8003/api/books',
    'http://book-service:8003/api/books',
]
ENV_BOOK_SERVICE_URL = os.getenv('BOOK_SERVICE_URL')
BOOK_SERVICE_URLS = [ENV_BOOK_SERVICE_URL] if ENV_BOOK_SERVICE_URL else DEFAULT_BOOK_SERVICE_URLS


def _check_book_exists(book_id):
    for base_url in BOOK_SERVICE_URLS:
        try:
            response = requests.get(f'{base_url}/{book_id}/', timeout=5)
        except requests.RequestException:
            continue

        if response.status_code == status.HTTP_200_OK:
            return True
        if response.status_code == status.HTTP_404_NOT_FOUND:
            return False

    return None


@api_view(['GET', 'POST'])
def cart_view(request, customer_id):
    if request.method == 'GET':
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response({'items': []}, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        book_id = request.data.get('book_id')

        # Support empty-cart initialization from customer registration.
        if book_id is None:
            if request.data:
                return Response({'book_id': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)
            cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        payload_serializer = AddCartItemSerializer(data=request.data)
        payload_serializer.is_valid(raise_exception=True)

        validated_data = payload_serializer.validated_data
        book_exists = _check_book_exists(validated_data['book_id'])
        if book_exists is False:
            return Response({'book_id': ['Book does not exist.']}, status=status.HTTP_400_BAD_REQUEST)
        if book_exists is None:
            return Response(
                {'error': 'Book service is unavailable. Cannot validate book_id.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            book_id=validated_data['book_id'],
            defaults={'quantity': validated_data['quantity']},
        )

        if not created:
            cart_item.quantity += validated_data['quantity']
            cart_item.save(update_fields=['quantity'])

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def remove_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()
        return Response({'message': 'Item removed'}, status=status.HTTP_200_OK)
    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def update_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id)
        payload_serializer = UpdateCartItemQuantitySerializer(data=request.data)
        payload_serializer.is_valid(raise_exception=True)

        cart_item.quantity = payload_serializer.validated_data['quantity']
        cart_item.save(update_fields=['quantity'])
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)
    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

