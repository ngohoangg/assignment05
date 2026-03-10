from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_id', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer_id',)
    ordering = ('-created_at',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'book_id', 'quantity')
    list_filter = ('cart__created_at',)
    search_fields = ('cart__customer_id', 'book_id')
    ordering = ('-cart__created_at',)
