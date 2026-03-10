import os
from decimal import Decimal, InvalidOperation

import requests
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import BookCategory, Category
from .serializers import BookCategorySerializer, CategorySerializer

BOOK_SERVICE_URL = os.getenv('BOOK_SERVICE_URL', 'http://localhost:8003/api/books').rstrip('/')
ALLOWED_SORT_FIELDS = {'title', 'author', 'price', 'stock'}


def _book_service_list():
    try:
        response = requests.get(f'{BOOK_SERVICE_URL}/', timeout=8)
    except requests.RequestException:
        return None, status.HTTP_502_BAD_GATEWAY
    if response.status_code != 200:
        return None, response.status_code
    payload = response.json()
    if not isinstance(payload, list):
        return None, status.HTTP_502_BAD_GATEWAY
    return payload, status.HTTP_200_OK


def _book_service_set_category(book_id, category_id):
    payload = {'category_id': category_id}
    try:
        return requests.put(f'{BOOK_SERVICE_URL}/{book_id}/update/', json=payload, timeout=8)
    except requests.RequestException:
        return None


def _sort_books(books, sort):
    if not sort:
        return books

    reverse = sort.startswith('-')
    field = sort[1:] if reverse else sort
    if field not in ALLOWED_SORT_FIELDS:
        return None

    def sort_key(book):
        value = book.get(field)
        if field in {'price', 'stock'}:
            try:
                return Decimal(str(value))
            except (TypeError, InvalidOperation):
                return Decimal('0')
        return str(value or '').lower()

    return sorted(books, key=sort_key, reverse=reverse)


@api_view(['GET'])
def list_catalog_books(request):
    books, fetch_status = _book_service_list()
    if books is None:
        return Response({'error': 'Cannot fetch books from book-service.'}, status=fetch_status)

    mappings = BookCategory.objects.select_related('category').all()
    mapping_by_book_id = {mapping.book_id: mapping for mapping in mappings}
    category_map = {category.id: category for category in Category.objects.all()}
    category_id = request.GET.get('category_id')

    if category_id:
        try:
            category_id_int = int(category_id)
        except ValueError:
            return Response({'error': 'category_id must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
        filtered_books = []
        for book in books:
            book_category_id = book.get('category_id')
            if book_category_id is None and mapping_by_book_id.get(book.get('id')):
                book_category_id = mapping_by_book_id[book['id']].category_id
            if book_category_id == category_id_int:
                filtered_books.append(book)
        books = filtered_books

    response_books = []
    for book in books:
        mapping = mapping_by_book_id.get(book.get('id'))
        category_id_value = book.get('category_id')
        if category_id_value is None and mapping:
            category_id_value = mapping.category_id
        category_payload = None
        if category_id_value is not None:
            category_obj = category_map.get(category_id_value)
            if category_obj:
                category_payload = CategorySerializer(category_obj).data

        response_books.append(
            {
                **book,
                'category_id': category_id_value,
                'category': category_payload,
            }
        )

    sort = request.GET.get('sort', '').strip()
    sorted_books = _sort_books(response_books, sort)
    if sorted_books is None:
        return Response(
            {'error': 'sort must be one of: title, -title, author, -author, price, -price, stock, -stock'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(sorted_books)


@api_view(['GET', 'POST'])
def categories(request):
    if request.method == 'GET':
        data = CategorySerializer(Category.objects.all(), many=True).data
        return Response(data)

    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        category = serializer.save()
        return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def category_detail(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(CategorySerializer(category).data)

    if request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    books, _ = _book_service_list()
    if books is not None:
        for book in books:
            if book.get('category_id') == category_id:
                _book_service_set_category(book['id'], None)

    category.delete()
    return Response({'message': 'Category deleted successfully'}, status=status.HTTP_200_OK)


@api_view(['PUT'])
def set_book_category(request, book_id):
    category_id = request.data.get('category_id')
    if category_id is None:
        book_response = _book_service_set_category(book_id, None)
        if not book_response or book_response.status_code != 200:
            return Response({'error': 'Cannot update book category in book-service.'}, status=status.HTTP_502_BAD_GATEWAY)
        BookCategory.objects.filter(book_id=book_id).delete()
        return Response({'message': 'Category mapping removed', 'book_id': book_id, 'category_id': None})

    try:
        category_id_int = int(category_id)
    except (TypeError, ValueError):
        return Response({'error': 'category_id must be an integer or null.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        category = Category.objects.get(id=category_id_int)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    book_response = _book_service_set_category(book_id, category_id_int)
    if not book_response or book_response.status_code != 200:
        return Response({'error': 'Cannot update book category in book-service.'}, status=status.HTTP_502_BAD_GATEWAY)

    mapping, _ = BookCategory.objects.update_or_create(
        book_id=book_id,
        defaults={'category': category},
    )
    return Response(BookCategorySerializer(mapping).data)
