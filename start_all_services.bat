@echo off
set "BASE_DIR=%~dp0"

echo ===================================
echo Starting Microservices Architecture
echo ===================================
echo.

echo Starting Customer Service (port 8002)...
start "Customer Service" cmd /k "cd /d %BASE_DIR%customer-service && python manage.py runserver 8002"
timeout /t 2 /nobreak > nul

echo Starting Book Service (port 8003)...
start "Book Service" cmd /k "cd /d %BASE_DIR%book-service && python manage.py runserver 8003"
timeout /t 2 /nobreak > nul

echo Starting Catalog Service (port 8008)...
start "Catalog Service" cmd /k "cd /d %BASE_DIR%catalog-service && python manage.py runserver 8008"
timeout /t 2 /nobreak > nul

echo Starting Cart Service (port 8004)...
start "Cart Service" cmd /k "cd /d %BASE_DIR%cart-service && python manage.py runserver 8004"
timeout /t 2 /nobreak > nul

echo Starting Order Service (port 8006)...
start "Order Service" cmd /k "cd /d %BASE_DIR%order-service && python manage.py runserver 8006"
timeout /t 2 /nobreak > nul

echo Starting Staff Service (port 8007)...
start "Staff Service" cmd /k "cd /d %BASE_DIR%staff-service && python manage.py runserver 8007"
timeout /t 2 /nobreak > nul

echo Starting Gateway (port 8005)...
start "Gateway" cmd /k "cd /d %BASE_DIR%gateway && python manage.py runserver 8005"

echo.
echo ===================================
echo All services started!
echo ===================================
echo.
echo Customer Service: http://localhost:8002/api/customers/
echo Book Service:     http://localhost:8003/api/books/
echo Catalog Service:  http://localhost:8008/api/catalog/
echo Cart Service:     http://localhost:8004/api/carts/
echo Order Service:    http://localhost:8006/api/orders/
echo Staff Service:    http://localhost:8007/api/staff/
echo Gateway Web:      http://localhost:8005/
echo.
echo Press any key to exit...
pause > nul
