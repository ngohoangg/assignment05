from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_id', 'shipping_city', 'shipping_country', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_id', 'shipping_line1', 'shipping_city', 'shipping_country')
    ordering = ('-created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'book_id', 'quantity', 'unit_price', 'subtotal')
    list_filter = ('order__created_at',)
    search_fields = ('order__customer_id', 'book_id', 'book_title')
    ordering = ('-order__created_at',)
