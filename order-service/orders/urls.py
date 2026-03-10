from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.list_orders, name='list_orders'),
    path('<int:customer_id>/', views.orders_view, name='orders_view'),
    path('detail/<int:order_id>/', views.get_order, name='get_order'),
    path('detail/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
]
