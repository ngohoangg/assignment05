from django.urls import path
from . import views

urlpatterns = [
    path('<int:customer_id>/', views.cart_view, name='cart_view'),
    path('items/<int:item_id>/', views.remove_item, name='remove_item'),
    path('items/<int:item_id>/update/', views.update_item, name='update_item'),
]
