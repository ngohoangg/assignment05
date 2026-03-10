# Microservices Architecture - BookStore

## Kiến trúc
Hệ thống gồm 3 microservices độc lập và 1 Gateway:

### 1. Customer Service (Port 8002)
- **Database**: customer_db
- **Chức năng**: Quản lý tài khoản người dùng
- **APIs**:
  - POST `/api/customers/register/` - Đăng ký
  - POST `/api/customers/login/` - Đăng nhập
  - GET `/api/customers/<id>/` - Thông tin customer
  - GET `/api/customers/` - Danh sách customers

### 2. Book Service (Port 8003)
- **Database**: book_db
- **Chức năng**: Quản lý danh mục sách
- **APIs**:
  - GET `/api/books/` - Danh sách sách
  - GET `/api/books/<id>/` - Chi tiết sách
  - PUT `/api/books/<id>/stock/` - Cập nhật tồn kho

### 3. Cart Service (Port 8004)
- **Database**: cart_db
- **Chức năng**: Quản lý giỏ hàng
- **APIs**:
  - GET `/api/carts/<customer_id>/` - Xem giỏ hàng
  - POST `/api/carts/<customer_id>/` - Thêm vào giỏ
  - DELETE `/api/carts/items/<item_id>/` - Xóa item
  - PUT `/api/carts/items/<item_id>/update/` - Cập nhật số lượng

### 4. Gateway (Port 8005)
- **Chức năng**: Web interface gọi các microservices
- **Công nghệ**: Django + Requests library
- **URL**: http://localhost:8005/

## Cách chạy

### Cách 1: Tự động (Recommended)
```bash
cd c:\assignment_01\micro
start_all_services.bat
```

### Cách 2: Thủ công
Mở 4 terminal riêng biệt:

```bash
# Terminal 1 - Customer Service
cd c:\assignment_01\micro\customer-service
python manage.py runserver 8002

# Terminal 2 - Book Service
cd c:\assignment_01\micro\book-service
python manage.py runserver 8003

# Terminal 3 - Cart Service
cd c:\assignment_01\micro\cart-service
python manage.py runserver 8004

# Terminal 4 - Gateway
cd c:\assignment_01\micro\gateway
python manage.py runserver 8005
```

## Thiết lập lần đầu

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Tạo databases trong MySQL
```sql
CREATE DATABASE customer_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE book_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE cart_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Cấu hình database password
Mở các file settings và thay đổi password nếu cần:
- `customer-service/customer_service/settings.py`
- `book-service/book_service/settings.py`
- `cart-service/cart_service/settings.py`

Tìm section `DATABASES` và thay đổi `PASSWORD`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'xxx_db',
        'USER': 'root',
        'PASSWORD': '24102004dz',  # Thay đổi thành password MySQL của bạn
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 4. Chạy migrations cho từng service
```bash
# Customer Service
cd customer-service
python manage.py migrate
cd ..

# Book Service
cd book-service
python manage.py migrate
cd ..

# Cart Service
cd cart-service
python manage.py migrate
cd ..

# Gateway
cd gateway
python manage.py migrate
cd ..
```

### 5. Populate dữ liệu mẫu

#### Tạo superuser cho Customer Service
```bash
cd customer-service
python manage.py shell
```
Trong shell:
```python
from customers.models import Customer
from django.contrib.auth.hashers import make_password

admin = Customer.objects.create(
    name='Admin',
    email='admin@bookstore.com',
    password=make_password('admin123'),
    is_staff=True,
    is_superuser=True
)
print(f'Created superuser: {admin.email}')
exit()
```

#### Tạo superuser cho Book Service
```bash
cd book-service
python manage.py createsuperuser --username admin --email admin@bookstore.com
# Password: admin123
```

#### Tạo superuser cho Cart Service
```bash
cd cart-service
python manage.py createsuperuser --username admin --email admin@bookstore.com
# Password: admin123
```

#### Populate sách vào Book Service
```bash
cd book-service
python populate_books.py
```
Hoặc thủ công:
```bash
python manage.py shell
```
```python
from books.models import Book

books_data = [
    {'title': 'Clean Code', 'author': 'Robert C. Martin', 'price': 32.00, 'stock': 10},
    {'title': 'Design Patterns', 'author': 'Gang of Four', 'price': 45.00, 'stock': 8},
    {'title': 'The Pragmatic Programmer', 'author': 'Andrew Hunt', 'price': 40.00, 'stock': 12},
    {'title': 'Introduction to Algorithms', 'author': 'Thomas H. Cormen', 'price': 65.00, 'stock': 5},
    {'title': 'Head First Design Patterns', 'author': 'Eric Freeman', 'price': 38.00, 'stock': 15},
    {'title': 'Refactoring', 'author': 'Martin Fowler', 'price': 42.00, 'stock': 9},
    {'title': 'Python Crash Course', 'author': 'Eric Matthes', 'price': 30.00, 'stock': 20},
    {'title': 'Effective Python', 'author': 'Brett Slatkin', 'price': 35.00, 'stock': 11},
    {'title': 'JavaScript: The Good Parts', 'author': 'Douglas Crockford', 'price': 28.00, 'stock': 14},
    {'title': "You Don't Know JS", 'author': 'Kyle Simpson', 'price': 25.00, 'stock': 18},
    {'title': 'Eloquent JavaScript', 'author': 'Marijn Haverbeke', 'price': 30.00, 'stock': 16},
    {'title': 'The Art of Computer Programming', 'author': 'Donald Knuth', 'price': 80.00, 'stock': 3},
]

for book in books_data:
    Book.objects.create(**book)

print("Created 12 books!")
exit()
```

## Truy cập

### Web Application (Gateway)
**URL**: http://localhost:8005/
- Trang chủ, đăng ký, đăng nhập, xem sách, giỏ hàng

### Django Admin Panels
- **Customer Service**: http://localhost:8002/admin/
  - Username: admin@bookstore.com
  - Password: admin123
  - Quản lý: Customers

- **Book Service**: http://localhost:8003/admin/
  - Username: admin
  - Password: admin123
  - Quản lý: Books

- **Cart Service**: http://localhost:8004/admin/
  - Username: admin
  - Password: admin123
  - Quản lý: Carts, Cart Items

### REST APIs
- **Customer API**: http://localhost:8002/api/customers/
- **Book API**: http://localhost:8003/api/books/
- **Cart API**: http://localhost:8004/api/carts/

## API Documentation

### Customer Service (Port 8002)

#### Register
```http
POST /api/customers/register/
Content-Type: application/json

{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepass123"
}
```

#### Login
```http
POST /api/customers/login/
Content-Type: application/json

{
    "email": "john@example.com",
    "password": "securepass123"
}
```

#### Get Customer
```http
GET /api/customers/{customer_id}/
```

#### List Customers
```http
GET /api/customers/
```

### Book Service (Port 8003)

#### List Books
```http
GET /api/books/
```

#### Get Book Detail
```http
GET /api/books/{book_id}/
```

#### Update Stock
```http
PUT /api/books/{book_id}/stock/
Content-Type: application/json

{
    "quantity": 5
}
```

### Cart Service (Port 8004)

#### View Cart
```http
GET /api/carts/{customer_id}/
```

#### Add to Cart
```http
POST /api/carts/{customer_id}/
Content-Type: application/json

{
    "book_id": 1,
    "quantity": 2
}
```

#### Remove Item
```http
DELETE /api/carts/items/{item_id}/
```

#### Update Item Quantity
```http
PUT /api/carts/items/{item_id}/update/
Content-Type: application/json

{
    "quantity": 3
}
```

## Đặc điểm Microservices
- ✅ Mỗi service có database riêng
- ✅ Giao tiếp qua REST API
- ✅ Có thể scale độc lập
- ✅ Có thể deploy riêng lẻ
- ✅ Loosely coupled architecture
- ✅ Technology independence (mỗi service có thể dùng tech khác nhau)

## Troubleshooting

### Service không khởi động
- Kiểm tra port đã được sử dụng chưa
- Kiểm tra MySQL đã chạy chưa
- Kiểm tra database đã tạo chưa

### Lỗi kết nối giữa Gateway và Services
- Đảm bảo tất cả 4 services đang chạy
- Kiểm tra port trong `gateway/web/views.py`:
  - Customer: localhost:8002
  - Book: localhost:8003
  - Cart: localhost:8004

### Reset database
```bash
# Cho từng service
cd <service-folder>
python manage.py flush
python manage.py migrate
```

## Technology Stack
- **Framework**: Django 5.2.10, Django REST Framework 3.16.1
- **Database**: MySQL 8.0 (3 separate databases)
- **Communication**: REST API (requests library)
- **Gateway Pattern**: API Gateway for web interface
- **Session Storage**: SQLite (gateway only)
