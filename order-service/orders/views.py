from decimal import Decimal

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import CreateOrderSerializer, OrderSerializer


@api_view(['GET', 'POST'])
def orders_view(request, customer_id):
    if request.method == 'GET':
        orders = Order.objects.filter(customer_id=customer_id).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    serializer = CreateOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    items_data = serializer.validated_data['items']
    shipping_address = serializer.validated_data['shipping_address']
    if not items_data:
        return Response({'error': 'Order items are required'}, status=status.HTTP_400_BAD_REQUEST)

    total_amount = Decimal('0.00')
    order_items_to_create = []
    for item in items_data:
        quantity = item['quantity']
        unit_price = item['unit_price']
        subtotal = unit_price * quantity
        total_amount += subtotal
        order_items_to_create.append(
            OrderItem(
                book_id=item['book_id'],
                book_title=item.get('book_title', ''),
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal,
            )
        )

    with transaction.atomic():
        order = Order.objects.create(
            customer_id=customer_id,
            shipping_line1=shipping_address['line1'],
            shipping_line2=shipping_address['line2'],
            shipping_city=shipping_address['city'],
            shipping_state=shipping_address['state'],
            shipping_postal_code=shipping_address['postal_code'],
            shipping_country=shipping_address['country'],
            total_amount=total_amount,
            status=Order.STATUS_PENDING,
        )
        for order_item in order_items_to_create:
            order_item.order = order
            order_item.save()

    response_serializer = OrderSerializer(order)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def list_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def update_order_status(request, order_id):
    valid_statuses = {choice[0] for choice in Order.STATUS_CHOICES}

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    status_value = request.data.get('status')
    if status_value not in valid_statuses:
        return Response(
            {'error': f'Invalid status. Allowed: {", ".join(sorted(valid_statuses))}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order.status = status_value
    order.save()
    serializer = OrderSerializer(order)
    return Response(serializer.data)

