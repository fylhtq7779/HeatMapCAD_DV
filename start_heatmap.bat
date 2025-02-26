@echo off
echo Запуск HeatMapCAD...

REM Проверяем наличие Python
python --version > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python найден, запуск приложения...
    python launch_heatmap.py
    goto :eof
)

REM Проверяем наличие Python через py launcher
py --version > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python Launcher найден, запуск приложения...
    py launch_heatmap.py
    goto :eof
)

echo ОШИБКА: Python не найден. Пожалуйста, установите Python 3.8 или выше.
echo Вы можете скачать Python с официального сайта: https://www.python.org/downloads/
pause
exit /b 1

:eof
exit /b 0 