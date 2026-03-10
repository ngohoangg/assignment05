import os

import requests
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from .models import Address, Customer, FullName
from .serializers import (
    CustomerSerializer,
    LoginSerializer,
    RegisterSerializer,
    UpdateAddressSerializer,
    UpdateCustomerProfileSerializer,
)

DEFAULT_CART_SERVICE_URLS = [
    'http://localhost:8004/api/carts',
    'http://cart-service:8004/api/carts',
]
ENV_CART_SERVICE_URL = os.getenv('CART_SERVICE_URL')
if ENV_CART_SERVICE_URL:
    CART_SERVICE_URLS = [ENV_CART_SERVICE_URL]
else:
    CART_SERVICE_URLS = DEFAULT_CART_SERVICE_URLS


@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.save()
        cart_created = False
        for cart_service_url in CART_SERVICE_URLS:
            try:
                cart_response = requests.post(
                    f'{cart_service_url}/{customer.id}/',
                    json={},
                    timeout=3,
                )
                if cart_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
                    cart_created = True
                    break
            except requests.RequestException:
                continue

        if not cart_created:
            customer.delete()
            return Response(
                {'error': 'Failed to initialize customer cart'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        address_data = None
        if customer.address:
            address_data = {
                'line1': customer.address.line1,
                'line2': customer.address.line2,
                'city': customer.address.city,
                'state': customer.address.state,
                'postal_code': customer.address.postal_code,
                'country': customer.address.country,
            }
        return Response({
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'address': address_data,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            customer = Customer.objects.get(email=email)
            if check_password(password, customer.password):
                return Response({
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email,
                    'token': f'customer_{customer.id}'
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Customer.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
def get_customer(request, customer_id):
    try:
        customer = Customer.objects.select_related('address', 'fullname').get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    serializer = UpdateCustomerProfileSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    update_data = serializer.validated_data

    if 'name' in update_data:
        if customer.fullname is None:
            customer.fullname = FullName.objects.create(full_name=update_data['name'])
            customer.save(update_fields=['fullname'])
        else:
            customer.fullname.full_name = update_data['name']
            customer.fullname.save(update_fields=['full_name'])

    if 'address' in update_data:
        address_data = update_data['address']
        if customer.address is None:
            customer.address = Address.objects.create(**address_data)
            customer.save(update_fields=['address'])
        else:
            for key, value in address_data.items():
                setattr(customer.address, key, value)
            customer.address.save(update_fields=list(address_data.keys()))

    response_serializer = CustomerSerializer(customer)
    return Response(response_serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def list_customers(request):
    customers = Customer.objects.all()
    serializer = CustomerSerializer(customers, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
def update_customer_address(request, customer_id):
    serializer = UpdateAddressSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        customer = Customer.objects.select_related('address').get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    address_data = serializer.validated_data
    address = customer.address
    if address is None:
        address = Address.objects.create(**address_data)
        customer.address = address
        customer.save(update_fields=['address'])
    else:
        for key, value in address_data.items():
            setattr(address, key, value)
        address.save()

    response_serializer = CustomerSerializer(customer)
    return Response(response_serializer.data, status=status.HTTP_200_OK)

