from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_books, name='list_books'),
    path('create/', views.create_book, name='create_book'),
    path('<int:book_id>/', views.get_book, name='get_book'),
    path('<int:book_id>/update/', views.update_book, name='update_book'),
    path('<int:book_id>/delete/', views.delete_book, name='delete_book'),
    path('<int:book_id>/stock/', views.update_stock, name='update_stock'),
]
