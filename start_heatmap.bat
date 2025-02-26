@echo off
echo Запуск HeatMapCAD...
echo.

REM Проверяем наличие Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА: Python не найден.
    echo Пожалуйста, установите Python 3.8 или выше.
    echo Вы можете скачать Python с официального сайта: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Запускаем приложение
python launch_heatmap.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Произошла ошибка при запуске приложения.
    pause
    exit /b 1
)

exit /b 0 