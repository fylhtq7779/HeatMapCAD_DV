@echo off
chcp 65001 > nul
echo Запуск HeatMapCAD...
echo.

REM Создаем файл для отладки
echo Начало отладки > debug_launch.log
echo Время: %date% %time% >> debug_launch.log

REM Проверяем наличие Python
where python >> debug_launch.log 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА: Python не найден. >> debug_launch.log
    echo ОШИБКА: Python не найден.
    echo Пожалуйста, установите Python 3.8 или выше.
    echo Вы можете скачать Python с официального сайта: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python найден >> debug_launch.log
python --version >> debug_launch.log 2>&1

REM Запускаем приложение с перенаправлением вывода в лог
echo Запуск приложения... >> debug_launch.log
python launch_heatmap.py >> debug_launch.log 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Произошла ошибка при запуске приложения (код %ERRORLEVEL%) >> debug_launch.log
    echo.
    echo Произошла ошибка при запуске приложения.
    echo Подробности в файле debug_launch.log
    pause
    exit /b 1
)

echo Приложение успешно запущено >> debug_launch.log
exit /b 0 