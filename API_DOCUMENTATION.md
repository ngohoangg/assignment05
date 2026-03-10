# API Documentation

Project: `c:\micro`  
Architecture: Django microservices + gateway

## 1. Base URLs

- Customer Service: `http://localhost:8002/api/customers`
- Book Service: `http://localhost:8003/api/books`
- Cart Service: `http://localhost:8004/api/carts`
- Gateway (web app): `http://localhost:8005`
- Order Service: `http://localhost:8006/api/orders`
- Staff Service: `http://localhost:8007/api/staff`
- Catalog Service: `http://localhost:8008/api/catalog`

## 2. Common Notes

- Response format is JSON unless stated otherwise.
- No JWT/session auth is enforced at microservice API layer.
- `token` returned by login endpoints is a simple string (`customer_<id>`, `staff_<id>`), used by gateway UI logic only.

## 3. Customer Service (`/api/customers`)

### 3.1 Register customer

- Method: `POST`
- Path: `/register/`
- Body:

```json
{
  "name": "Nguyen Van A",
  "email": "a@example.com",
  "password": "123456"
}
```

- Success `201`:

```json
{
  "id": 1,
  "name": "Nguyen Van A",
  "email": "a@example.com",
  "address": null
}
```

- Errors:
- `400`: serializer validation errors
- `502`: `{"error":"Failed to initialize customer cart"}` (cart-service init failed)

### 3.2 Customer login

- Method: `POST`
- Path: `/login/`
- Body:

```json
{
  "email": "a@example.com",
  "password": "123456"
}
```

- Success `200`:

```json
{
  "id": 1,
  "name": "Nguyen Van A",
  "email": "a@example.com",
  "token": "customer_1"
}
```

- Errors:
- `400`: invalid payload format
- `401`: `{"error":"Invalid credentials"}`

### 3.3 Get or update customer profile

- Method: `GET`, `PUT`
- Path: `/{customer_id}/`

`GET` success `200`:

```json
{
  "id": 1,
  "name": "Nguyen Van A",
  "email": "a@example.com",
  "address": {
    "line1": "123 Main St",
    "line2": "",
    "city": "HCM",
    "state": "",
    "postal_code": "",
    "country": "VN"
  },
  "date_joined": "2026-03-10T10:00:00Z"
}
```

`PUT` body (partial update allowed):

```json
{
  "name": "Nguyen Van B",
  "address": {
    "line1": "456 New St",
    "city": "HCM",
    "country": "VN"
  }
}
```

- Errors:
- `400`: invalid payload or empty body (`No data provided to update.`)
- `404`: `{"error":"Customer not found"}`

### 3.4 Update customer shipping address

- Method: `PUT`
- Path: `/{customer_id}/address/`
- Body (all fields optional, blank allowed):

```json
{
  "line1": "123 Main St",
  "line2": "",
  "city": "HCM",
  "state": "",
  "postal_code": "",
  "country": "VN"
}
```

- Success `200`: updated customer profile
- Errors:
- `400`: validation errors
- `404`: customer not found

### 3.5 List customers

- Method: `GET`
- Path: `/`
- Success `200`: array of customer profiles

## 4. Staff Service (`/api/staff`)

### 4.1 Register staff

- Method: `POST`
- Path: `/register/`
- Body:

```json
{
  "name": "Staff 1",
  "email": "staff1@example.com",
  "password": "123456",
  "role": "STAFF"
}
```

- `role` values: `STAFF`, `MANAGER`
- Success `201`: `{id, name, email, role}`
- Errors: `400` validation errors

### 4.2 Staff login

- Method: `POST`
- Path: `/login/`
- Body:

```json
{
  "email": "staff1@example.com",
  "password": "123456"
}
```

- Success `200`: `{id, name, email, role, token}`
- Errors:
- `400`: invalid payload
- `401`: invalid credentials

### 4.3 Get staff by id

- Method: `GET`
- Path: `/{staff_id}/`
- Success `200`: `{id, name, email, role, date_joined}`
- Errors: `404` if not found

### 4.4 List staff

- Method: `GET`
- Path: `/`
- Success `200`: array of staff

## 5. Book Service (`/api/books`)

### 5.1 List books

- Method: `GET`
- Path: `/`
- Query params:
- `category_id` (integer, optional)
- `sort` (optional): `title`, `-title`, `author`, `-author`, `price`, `-price`, `stock`, `-stock`, `category_id`, `-category_id`
- Success `200`: array of:

```json
{
  "id": 1,
  "title": "Book A",
  "author": "Author A",
  "price": "10.00",
  "stock": 20,
  "category_id": 1
}
```

- Errors:
- `400`: invalid `category_id` or invalid `sort`

### 5.2 Create book

- Method: `POST`
- Path: `/create/`
- Body:

```json
{
  "title": "Book A",
  "author": "Author A",
  "price": "10.00",
  "stock": 20,
  "category_id": 1
}
```

- Rules:
- `price >= 0`
- `stock >= 0`
- `category_id` must be positive integer or `null`
- Success `201`: created book object
- Errors: `400` validation errors

### 5.3 Get book

- Method: `GET`
- Path: `/{book_id}/`
- Success `200`: book object
- Errors: `404` with `{"error":"Book not found"}`

### 5.4 Update book (partial allowed)

- Method: `PUT`
- Path: `/{book_id}/update/`
- Body: any subset of book fields
- Success `200`: updated book object
- Errors:
- `400`: validation errors
- `404`: book not found

### 5.5 Delete book

- Method: `DELETE`
- Path: `/{book_id}/delete/`
- Success `200`: `{"message":"Book deleted successfully"}`
- Errors: `404` book not found

### 5.6 Update stock

- Method: `PUT`
- Path: `/{book_id}/stock/`
- Body:

```json
{
  "stock_change": -2
}
```

- Behavior: increases/decreases current stock by `stock_change`
- Success `200`: updated book object
- Errors:
- `400`: invalid integer or insufficient stock
- `404`: book not found

## 6. Catalog Service (`/api/catalog`)

### 6.1 List catalog books (enriched)

- Method: `GET`
- Path: `/books/`
- Query params:
- `category_id` (optional integer)
- `sort` (optional): `title`, `-title`, `author`, `-author`, `price`, `-price`, `stock`, `-stock`
- Success `200`: books from book-service enriched with category details:

```json
{
  "id": 1,
  "title": "Book A",
  "author": "Author A",
  "price": "10.00",
  "stock": 20,
  "category_id": 1,
  "category": {
    "id": 1,
    "name": "Novel",
    "description": "Fiction books"
  }
}
```

- Errors:
- `400`: invalid `category_id` or invalid `sort`
- `502` or upstream non-200 when cannot fetch books

### 6.2 List or create categories

- Method: `GET`, `POST`
- Path: `/categories/`

`POST` body:

```json
{
  "name": "Novel",
  "description": "Fiction books"
}
```

- Success `200` (`GET`) or `201` (`POST`)
- Errors: `400` validation errors

### 6.3 Category detail/update/delete

- Method: `GET`, `PUT`, `DELETE`
- Path: `/categories/{category_id}/`

`PUT` body (partial allowed):

```json
{
  "name": "Updated category name",
  "description": "Updated description"
}
```

- `DELETE` behavior: tries to clear `category_id` for related books in book-service, then deletes category
- Success:
- `200` for `GET`, `PUT`, `DELETE`
- Errors:
- `404`: category not found
- `400`: validation errors for `PUT`

### 6.4 Set or remove book category mapping

- Method: `PUT`
- Path: `/books/{book_id}/category/`
- Body set category:

```json
{
  "category_id": 1
}
```

- Body remove category:

```json
{
  "category_id": null
}
```

- Success:
- set: `200` with `BookCategorySerializer` payload
- remove: `200` with `{message, book_id, category_id: null}`
- Errors:
- `400`: invalid `category_id` type
- `404`: category not found
- `502`: cannot update book-service

## 7. Cart Service (`/api/carts`)

### 7.1 Get cart by customer

- Method: `GET`
- Path: `/{customer_id}/`
- Success:
- if cart exists: full cart
- if not exists: `{"items":[]}` with `200`

Response shape:

```json
{
  "id": 1,
  "customer_id": 1,
  "created_at": "2026-03-10T10:00:00Z",
  "items": [
    {
      "id": 1,
      "cart": 1,
      "book_id": 2,
      "quantity": 3
    }
  ]
}
```

### 7.2 Add item to cart or initialize empty cart

- Method: `POST`
- Path: `/{customer_id}/`

Initialize empty cart:

```json
{}
```

Add item:

```json
{
  "book_id": 2,
  "quantity": 3
}
```

- Rules:
- `book_id >= 1`
- `quantity >= 1`
- book existence is validated via book-service
- Success `201`: current cart payload
- Errors:
- `400`: missing/invalid fields, non-existing book
- `503`: cannot validate book because book-service unavailable

### 7.3 Remove cart item

- Method: `DELETE`
- Path: `/items/{item_id}/`
- Success `200`: `{"message":"Item removed"}`
- Errors: `404` item not found

### 7.4 Update cart item quantity

- Method: `PUT`
- Path: `/items/{item_id}/update/`
- Body:

```json
{
  "quantity": 5
}
```

- Success `200`: updated cart item
- Errors:
- `400`: invalid quantity
- `404`: item not found

## 8. Order Service (`/api/orders`)

### 8.1 List orders by customer or create order

- Method: `GET`, `POST`
- Path: `/{customer_id}/`

`GET` success `200`: array of orders (newest first)

`POST` body:

```json
{
  "items": [
    {
      "book_id": 2,
      "book_title": "Book A",
      "quantity": 2,
      "unit_price": "10.00"
    }
  ],
  "shipping_address": {
    "line1": "123 Main St",
    "line2": "",
    "city": "HCM",
    "state": "",
    "postal_code": "",
    "country": "VN"
  }
}
```

- Rules:
- `items` must not be empty
- `quantity >= 1`
- `unit_price >= 0.01`
- shipping required: `line1`, `city`, `country`
- Success `201`: created order payload
- Errors: `400` validation or missing items

Order response shape:

```json
{
  "id": 1,
  "customer_id": 1,
  "shipping_address": {
    "line1": "123 Main St",
    "line2": "",
    "city": "HCM",
    "state": "",
    "postal_code": "",
    "country": "VN"
  },
  "total_amount": "20.00",
  "status": "PENDING",
  "created_at": "2026-03-10T10:00:00Z",
  "items": [
    {
      "id": 1,
      "book_id": 2,
      "book_title": "Book A",
      "quantity": 2,
      "unit_price": "10.00",
      "subtotal": "20.00"
    }
  ]
}
```

### 8.2 List all orders

- Method: `GET`
- Path: `/all/`
- Success `200`: array of orders

### 8.3 Get order detail

- Method: `GET`
- Path: `/detail/{order_id}/`
- Success `200`: order payload
- Errors: `404` order not found

### 8.4 Update order status

- Method: `PUT`
- Path: `/detail/{order_id}/status/`
- Body:

```json
{
  "status": "CONFIRMED"
}
```

- Allowed status values: `PENDING`, `CONFIRMED`, `CANCELLED`
- Success `200`: updated order
- Errors:
- `400`: invalid status
- `404`: order not found

## 9. Gateway Web Routes (`http://localhost:8005`)

Gateway routes are server-rendered pages and form endpoints, not pure REST APIs. Main paths:

- Public/auth: `/`, `/register/`, `/login/`, `/logout/`
- Customer pages: `/books/`, `/books/{book_id}/`, `/cart/`, `/orders/`, `/profile/`
- Cart actions: `/cart/add/{book_id}/`, `/cart/remove/{item_id}/`, `/cart/update/{item_id}/`
- Checkout: `/checkout/`
- Staff pages/actions:
- `/staff/login/`, `/staff/dashboard/`
- `/staff/orders/{order_id}/status/`
- `/staff/books/create/`, `/staff/books/{book_id}/update/`, `/staff/books/{book_id}/delete/`, `/staff/books/{book_id}/stock/`
- `/staff/categories/create/`, `/staff/categories/{category_id}/update/`, `/staff/categories/{category_id}/delete/`

## 10. Quick Flow Reference

- Customer registration: customer-service creates customer and calls cart-service to initialize empty cart.
- Book browsing in UI: gateway calls catalog-service `/books/` and `/categories/`.
- Checkout in UI:
- gateway updates customer address
- reads cart and books
- creates order
- decreases book stock
- clears cart items
