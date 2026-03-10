from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('staff/login/', views.staff_login, name='staff_login'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/orders/<int:order_id>/status/', views.update_order_status_by_staff, name='update_order_status_by_staff'),
    path('staff/books/create/', views.create_book_by_staff, name='create_book_by_staff'),
    path('staff/books/<int:book_id>/update/', views.update_book_by_staff, name='update_book_by_staff'),
    path('staff/books/<int:book_id>/delete/', views.delete_book_by_staff, name='delete_book_by_staff'),
    path('staff/books/<int:book_id>/stock/', views.update_book_stock_by_staff, name='update_book_stock_by_staff'),
    path('staff/categories/create/', views.create_category_by_staff, name='create_category_by_staff'),
    path('staff/categories/<int:category_id>/update/', views.update_category_by_staff, name='update_category_by_staff'),
    path('staff/categories/<int:category_id>/delete/', views.delete_category_by_staff, name='delete_category_by_staff'),
    path('logout/', views.logout_view, name='logout'),
    path('books/', views.books, name='books'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('cart/', views.cart_view, name='cart'),
    path('orders/', views.orders, name='orders'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
]
