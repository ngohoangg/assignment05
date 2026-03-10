from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.list_catalog_books, name='list_catalog_books'),
    path('categories/', views.categories, name='categories'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),
    path('books/<int:book_id>/category/', views.set_book_category, name='set_book_category'),
]
