@echo off
setlocal

echo Stopping Docker services...
docker compose down

echo.
echo Done.
pause
