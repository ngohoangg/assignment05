@echo off
setlocal

echo ===================================
echo Docker start for Microservices
echo ===================================
echo.

docker info >nul 2>&1
if errorlevel 1 (
    echo Docker Engine chua san sang.
    echo Hay mo Docker Desktop va doi den khi Engine running, sau do chay lai file nay.
    pause
    exit /b 1
)

echo Dang build va khoi dong containers...
docker compose up --build -d
if errorlevel 1 (
    echo.
    echo Khoi dong that bai. Xem log bang lenh:
    echo docker compose logs -f
    pause
    exit /b 1
)

echo.
echo He thong da khoi dong.
echo Gateway: http://localhost:8005/
echo.
echo Neu can seed du lieu sach:
echo docker compose exec book-service python populate_books.py
echo.
pause
