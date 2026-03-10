# Huong dan chay he thong bang Docker (Windows)

## 1) Dieu kien can
- Da cai Docker Desktop.
- Bat Docker Desktop va doi den khi status la "Engine running".

## 2) Mo terminal tai thu muc du an
Trong PowerShell:

```powershell
cd C:\micro
```

## 3) Build va chay toan bo he thong
Chay lenh:

```powershell
docker compose up --build -d
```

Lenh nay se:
- Build image Python cho cac service.
- Khoi dong MySQL.
- Tu tao 5 database: `customer_db`, `book_db`, `cart_db`, `order_db`, `staff_db`.
- Chay migration cho tung service.
- Khoi dong 6 service Django.

## 4) Kiem tra container dang chay

```powershell
docker compose ps
```

Neu tat ca on, ban se thay cac cong:
- Gateway: http://localhost:8005/
- Customer API: http://localhost:8002/api/customers/
- Book API: http://localhost:8003/api/books/
- Cart API: http://localhost:8004/api/carts/
- Order API: http://localhost:8006/api/orders/
- Staff API: http://localhost:8007/api/staff/

## 5) Xem log khi gap loi

```powershell
docker compose logs -f
```

Xem rieng 1 service:

```powershell
docker compose logs -f gateway
docker compose logs -f customer-service
```

## 6) Populate sach mau (book-service)
Sau khi he thong da chay:

```powershell
docker compose exec book-service python populate_books.py
```

## 7) Dung he thong

```powershell
docker compose down
```

## 8) Dung va xoa ca database volume (reset toan bo du lieu)

```powershell
docker compose down -v
```

Sau do muon chay lai tu dau:

```powershell
docker compose up --build -d
```
