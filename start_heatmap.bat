@echo off
chcp 65001 > nul
echo Запуск HeatMapCAD...
echo.

REM Создаем файл для отладки
echo Начало отладки > debug_launch.log
echo Время: %date% %time% >> debug_launch.log

REM Ищем Python в системе
echo Поиск Python в системе... >> debug_launch.log

REM Пробуем использовать py.exe лаунчер (если установлен Python Launcher)
set PYTHON_PATH=
WHERE py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python Launcher найден >> debug_launch.log
    set "PYTHON_CMD=py -3"
    goto PYTHON_FOUND
)

REM Пробуем найти python.exe через where
WHERE python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python найден через where команду >> debug_launch.log
    set "PYTHON_CMD=python"
    goto PYTHON_FOUND
)

REM Пробуем наиболее распространенные пути установки Python
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    echo Python найден в %LOCALAPPDATA%\Programs\Python\Python311 >> debug_launch.log
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    echo Python найден в %LOCALAPPDATA%\Programs\Python\Python310 >> debug_launch.log
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    goto PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" (
    echo Python найден в %LOCALAPPDATA%\Programs\Python\Python39 >> debug_launch.log
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    goto PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python38\python.exe" (
    echo Python найден в %LOCALAPPDATA%\Programs\Python\Python38 >> debug_launch.log
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python38\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files\Python311\python.exe" (
    echo Python найден в C:\Program Files\Python311 >> debug_launch.log
    set "PYTHON_CMD=C:\Program Files\Python311\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files\Python310\python.exe" (
    echo Python найден в C:\Program Files\Python310 >> debug_launch.log
    set "PYTHON_CMD=C:\Program Files\Python310\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files\Python39\python.exe" (
    echo Python найден в C:\Program Files\Python39 >> debug_launch.log
    set "PYTHON_CMD=C:\Program Files\Python39\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files\Python38\python.exe" (
    echo Python найден в C:\Program Files\Python38 >> debug_launch.log
    set "PYTHON_CMD=C:\Program Files\Python38\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files (x86)\Python311\python.exe" (
    echo Python найден в C:\Program Files (x86)\Python311 >> debug_launch.log
    set "PYTHON_CMD=C:\Program Files (x86)\Python311\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files (x86)\Python310\python.exe" (
    echo Python найден в C:\Program Files (x86)\Python310 >> debug_launch.log
    set "PYTHON_CMD=C:\Program Files (x86)\Python310\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files (x86)\Python39\python.exe" (
    echo Python найден в C:\Program Files (x86)\Python39 >> debug_launch.log
    set "PYTHON_CMD=C:\Program Files (x86)\Python39\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files (x86)\Python38\python.exe" (
    echo Python найден в C:\Program Files (x86)\Python38 >> debug_launch.log
    set "PYTHON_CMD=C:\Program Files (x86)\Python38\python.exe"
    goto PYTHON_FOUND
)

REM Если мы здесь, значит Python не найден
echo ОШИБКА: Python не найден в системе >> debug_launch.log
echo ОШИБКА: Python не найден.
echo Пожалуйста, установите Python 3.8 или выше.
echo Вы можете скачать Python с официального сайта: https://www.python.org/downloads/
echo При установке отметьте опцию "Add Python to PATH".
pause
exit /b 1

:PYTHON_FOUND
echo Используемая команда Python: %PYTHON_CMD% >> debug_launch.log

REM Проверяем версию Python
echo Проверка версии Python... >> debug_launch.log
%PYTHON_CMD% --version >> debug_launch.log 2>&1

REM Проверяем наличие файла launch_heatmap.py
if not exist "launch_heatmap.py" (
    echo ОШИБКА: Файл launch_heatmap.py не найден >> debug_launch.log
    echo ОШИБКА: Файл launch_heatmap.py не найден.
    pause
    exit /b 1
)

REM Запускаем приложение с перенаправлением вывода в лог
echo Запуск приложения... >> debug_launch.log
echo Запуск команды: %PYTHON_CMD% launch_heatmap.py >> debug_launch.log
%PYTHON_CMD% launch_heatmap.py >> debug_launch.log 2>&1
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