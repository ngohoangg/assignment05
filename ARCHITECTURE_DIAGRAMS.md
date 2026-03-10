# Architecture Diagram for Each Service

Project: `c:\micro`  
Style: Django microservices + API Gateway + separate DB schema per service

## 1) Gateway Service (`gateway`, port `8005`)

```mermaid
flowchart LR
    U[User Browser]
    URL[web/urls.py]
    V[web/views.py]
    T[templates/*.html]
    S[(Gateway Session DB<br/>sqlite3)]

    CS[Customer Service<br/>:8002]
    BS[Book Service<br/>:8003]
    CAS[Cart Service<br/>:8004]
    OS[Order Service<br/>:8006]
    SS[Staff Service<br/>:8007]
    CLS[Catalog Service<br/>:8008]

    U --> URL --> V
    V --> T
    V --> S
    V --> CS
    V --> BS
    V --> CAS
    V --> OS
    V --> SS
    V --> CLS
```

Main responsibility:
- Render web UI and orchestrate calls to all backend services.

## 2) Customer Service (`customer-service`, port `8002`)

```mermaid
flowchart LR
    API[api/customers/*]
    V[customers/views.py]
    SR[RegisterSerializer / LoginSerializer / Update*Serializer]
    M[Customer + FullName + Address models]
    DB[(customer_db)]
    CAS[Cart Service<br/>/api/carts/:customer_id/]

    API --> V --> SR --> M --> DB
    V --> CAS
```

Main responsibility:
- Customer register/login/profile/address.
- On register, initialize cart by calling Cart Service.

## 3) Book Service (`book-service`, port `8003`)

```mermaid
flowchart LR
    API[api/books/*]
    V[books/views.py]
    S[BookSerializer]
    M[Book model]
    DB[(book_db)]

    API --> V --> S --> M --> DB
```

Main responsibility:
- CRUD books and update stock (`stock_change`).

## 4) Catalog Service (`catalog-service`, port `8008`)

```mermaid
flowchart LR
    API[api/catalog/*]
    V[catalogs/views.py]
    S[CategorySerializer / BookCategorySerializer]
    M[Category + BookCategory models]
    DB[(catalog_db)]
    BS[Book Service<br/>/api/books/*]

    API --> V --> S --> M --> DB
    V --> BS
```

Main responsibility:
- Manage categories.
- Enrich/filter/sort book list with category data.
- Sync `category_id` to Book Service.

## 5) Cart Service (`cart-service`, port `8004`)

```mermaid
flowchart LR
    API[api/carts/*]
    V[carts/views.py]
    S[Add/Update/Cart serializers]
    M[Cart + CartItem models]
    DB[(cart_db)]
    BS[Book Service<br/>/api/books/:book_id/]

    API --> V --> S --> M --> DB
    V --> BS
```

Main responsibility:
- Create/get cart by customer.
- Add/update/remove cart item.
- Validate `book_id` by calling Book Service.

## 6) Order Service (`order-service`, port `8006`)

```mermaid
flowchart LR
    API[api/orders/*]
    V[orders/views.py]
    S[CreateOrderSerializer / OrderSerializer]
    M[Order + OrderItem models]
    DB[(order_db)]

    API --> V --> S --> M --> DB
```

Main responsibility:
- Create order from cart items and shipping address.
- List orders (per customer/all) and update order status.

## 7) Staff Service (`staff-service`, port `8007`)

```mermaid
flowchart LR
    API[api/staff/*]
    V[staffs/views.py]
    S[StaffSerializer / RegisterSerializer / LoginSerializer]
    M[Staff model]
    DB[(staff_db)]

    API --> V --> S --> M --> DB
```

Main responsibility:
- Staff register/login and staff listing/profile lookup.

## Inter-service Communication Summary

```mermaid
flowchart LR
    GW[Gateway]
    CUS[Customer Service]
    BOOK[Book Service]
    CAT[Catalog Service]
    CART[Cart Service]
    ORD[Order Service]
    STF[Staff Service]

    GW --> CUS
    GW --> BOOK
    GW --> CAT
    GW --> CART
    GW --> ORD
    GW --> STF

    CUS --> CART
    CART --> BOOK
    CAT --> BOOK
```
