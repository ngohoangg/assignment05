import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_service.settings')
django.setup()

from books.models import Book

books_data = [
    {"title": "Clean Code", "author": "Robert C. Martin", "price": 32.00, "stock": 50},
    {"title": "The Pragmatic Programmer", "author": "Andrew Hunt", "price": 35.00, "stock": 45},
    {"title": "Design Patterns", "author": "Gang of Four", "price": 40.00, "stock": 30},
    {"title": "Refactoring", "author": "Martin Fowler", "price": 38.00, "stock": 40},
    {"title": "You Don't Know JS", "author": "Kyle Simpson", "price": 25.00, "stock": 60},
    {"title": "JavaScript: The Good Parts", "author": "Douglas Crockford", "price": 28.00, "stock": 55},
    {"title": "Eloquent JavaScript", "author": "Marijn Haverbeke", "price": 30.00, "stock": 50},
    {"title": "Python Crash Course", "author": "Eric Matthes", "price": 33.00, "stock": 48},
    {"title": "Automate the Boring Stuff", "author": "Al Sweigart", "price": 29.00, "stock": 52},
    {"title": "Learning Python", "author": "Mark Lutz", "price": 42.00, "stock": 35},
    {"title": "Effective Java", "author": "Joshua Bloch", "price": 36.00, "stock": 42},
    {"title": "Head First Java", "author": "Kathy Sierra", "price": 34.00, "stock": 47}
]

print("Populating books...")
for book_data in books_data:
    book, created = Book.objects.get_or_create(
        title=book_data['title'],
        defaults=book_data
    )
    if created:
        print(f"✓ Created: {book.title}")
    else:
        print(f"- Exists: {book.title}")

print(f"\nTotal books: {Book.objects.count()}")
