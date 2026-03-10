from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer

ALLOWED_SORT_FIELDS = {'title', 'author', 'price', 'stock', 'category_id'}


@api_view(['GET'])
def list_books(request):
    books = Book.objects.all()

    category_id = request.GET.get('category_id', '').strip()
    if category_id:
        try:
            books = books.filter(category_id=int(category_id))
        except ValueError:
            return Response({'error': 'category_id must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

    sort = request.GET.get('sort', '').strip()
    if sort:
        sort_field = sort[1:] if sort.startswith('-') else sort
        if sort_field not in ALLOWED_SORT_FIELDS:
            return Response(
                {'error': 'sort must be one of: title, -title, author, -author, price, -price, stock, -stock, category_id, -category_id'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        books = books.order_by(sort)

    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_book(request):
    serializer = BookSerializer(data=request.data)
    if serializer.is_valid():
        book = serializer.save()
        return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_book(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
        serializer = BookSerializer(book)
        return Response(serializer.data)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def update_book(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = BookSerializer(book, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_book(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
        book.delete()
        return Response({'message': 'Book deleted successfully'}, status=status.HTTP_200_OK)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def update_stock(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
        stock_change = int(request.data.get('stock_change', 0))
        if book.stock + stock_change < 0:
            return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
        book.stock += stock_change
        book.save()
        serializer = BookSerializer(book)
        return Response(serializer.data)
    except (TypeError, ValueError):
        return Response({'error': 'stock_change must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

