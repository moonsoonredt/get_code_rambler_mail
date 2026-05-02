@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

if not exist "get_code.py" (
    echo ❌ Ошибка: Файл get_code.py не найден в текущей папке.
    pause
    exit /b
)

echo.
set /p "CONN=📧 Введите email:пароль (пример: user@rambler.ru:pass123) > "
if "%CONN%"=="" (
    echo ❌ Ввод пустой. Отмена.
    pause
    exit /b
)

echo.
echo ⏳ Подключение и поиск кода...
python get_code.py "%CONN%"
echo.
pause