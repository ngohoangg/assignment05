# Cart Service Sequence Diagram

## Overview

Base route: `/api/carts/`

Actors:
- Client
- Django URL Router
- Cart Views
- Serializer
- Cart DB
- Book Service

## 1. Get Cart By Customer

Endpoint: `GET /api/carts/{customer_id}/`

```mermaid
sequenceDiagram
    actor Client
    participant Router as Django URL Router
    participant View as cart_view
    participant DB as MySQL (Cart + CartItem)
    participant Serializer as CartSerializer

    Client->>Router: GET /api/carts/{customer_id}/
    Router->>View: cart_view(request, customer_id)
    View->>DB: Cart.objects.get(customer_id=customer_id)

    alt Cart exists
        DB-->>View: Cart + related items
        View->>Serializer: CartSerializer(cart)
        Serializer-->>View: serialized data
        View-->>Client: 200 OK + cart JSON
    else Cart does not exist
        DB-->>View: Cart.DoesNotExist
        View-->>Client: 200 OK + {"items": []}
    end
```

## 2. Initialize Empty Cart Or Add Item

Endpoint: `POST /api/carts/{customer_id}/`

```mermaid
sequenceDiagram
    actor Client
    participant Router as Django URL Router
    participant View as cart_view
    participant Serializer as AddCartItemSerializer
    participant BookSvc as Book Service
    participant DB as MySQL (Cart + CartItem)
    participant ResponseSerializer as CartSerializer

    Client->>Router: POST /api/carts/{customer_id}/
    Router->>View: cart_view(request, customer_id)
    View->>View: book_id = request.data.get("book_id")

    alt Empty body or no book_id
        alt request.data is not empty but missing book_id
            View-->>Client: 400 Bad Request
        else empty body
            View->>DB: Cart.objects.get_or_create(customer_id)
            DB-->>View: Cart
            View->>ResponseSerializer: CartSerializer(cart)
            ResponseSerializer-->>View: serialized data
            View-->>Client: 201 Created + empty cart JSON
        end
    else book_id is provided
        View->>Serializer: validate(request.data)
        alt Invalid payload
            Serializer-->>View: validation error
            View-->>Client: 400 Bad Request
        else Valid payload
            View->>BookSvc: GET /api/books/{book_id}/
            alt Book exists
                BookSvc-->>View: 200 OK
                View->>DB: Cart.objects.get_or_create(customer_id)
                DB-->>View: Cart
                View->>DB: CartItem.objects.get_or_create(cart, book_id, defaults={quantity})
                alt Item already exists
                    DB-->>View: existing CartItem
                    View->>DB: increase quantity and save()
                else New item
                    DB-->>View: new CartItem created
                end
                View->>ResponseSerializer: CartSerializer(cart)
                ResponseSerializer-->>View: serialized data
                View-->>Client: 201 Created + updated cart JSON
            else Book not found
                BookSvc-->>View: 404 Not Found
                View-->>Client: 400 Bad Request + {"book_id": ["Book does not exist."]}
            else Book service unavailable
                BookSvc-->>View: network error / no usable response
                View-->>Client: 503 Service Unavailable
            end
        end
    end
```

## 3. Update Item Quantity

Endpoint: `PUT /api/carts/items/{item_id}/update/`

```mermaid
sequenceDiagram
    actor Client
    participant Router as Django URL Router
    participant View as update_item
    participant Serializer as UpdateCartItemQuantitySerializer
    participant DB as MySQL (CartItem)
    participant ResponseSerializer as CartItemSerializer

    Client->>Router: PUT /api/carts/items/{item_id}/update/
    Router->>View: update_item(request, item_id)
    View->>DB: CartItem.objects.get(id=item_id)

    alt Item exists
        DB-->>View: CartItem
        View->>Serializer: validate(request.data)
        alt Invalid quantity
            Serializer-->>View: validation error
            View-->>Client: 400 Bad Request
        else Valid quantity
            View->>DB: save(quantity)
            DB-->>View: updated CartItem
            View->>ResponseSerializer: CartItemSerializer(cart_item)
            ResponseSerializer-->>View: serialized data
            View-->>Client: 200 OK + item JSON
        end
    else Item not found
        DB-->>View: CartItem.DoesNotExist
        View-->>Client: 404 Not Found
    end
```

## 4. Remove Item

Endpoint: `DELETE /api/carts/items/{item_id}/`

```mermaid
sequenceDiagram
    actor Client
    participant Router as Django URL Router
    participant View as remove_item
    participant DB as MySQL (CartItem)

    Client->>Router: DELETE /api/carts/items/{item_id}/
    Router->>View: remove_item(request, item_id)
    View->>DB: CartItem.objects.get(id=item_id)

    alt Item exists
        DB-->>View: CartItem
        View->>DB: delete()
        View-->>Client: 200 OK + {"message": "Item removed"}
    else Item not found
        DB-->>View: CartItem.DoesNotExist
        View-->>Client: 404 Not Found
    end
```

## Code Mapping

- Route entry: `cart_service/urls.py` and `carts/urls.py`
- Business logic: `carts/views.py`
- Request validation and response serialization: `carts/serializers.py`
- Persistence model: `carts/models.py`
