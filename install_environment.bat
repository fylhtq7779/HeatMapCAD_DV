@echo off
chcp 65001 > nul
echo ===================================================
echo Установка окружения и библиотек для HeatMapCAD
echo ===================================================
echo.

REM Создаем файл для отладки
echo Начало установки > install_debug.log
echo Время: %date% %time% >> install_debug.log

REM Ищем Python в системе
echo Поиск Python в системе...
echo Поиск Python в системе... >> install_debug.log

REM Пробуем использовать py.exe лаунчер (если установлен Python Launcher)
set PYTHON_PATH=
WHERE py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python Launcher найден
    echo Python Launcher найден >> install_debug.log
    set "PYTHON_CMD=py -3"
    goto PYTHON_FOUND
)

REM Пробуем найти python.exe через where
WHERE python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python найден через where команду
    echo Python найден через where команду >> install_debug.log
    set "PYTHON_CMD=python"
    goto PYTHON_FOUND
)

REM Пробуем наиболее распространенные пути установки Python
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    echo Python найден в %LOCALAPPDATA%\Programs\Python\Python311 >> install_debug.log
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    echo Python найден в %LOCALAPPDATA%\Programs\Python\Python310 >> install_debug.log
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    goto PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" (
    echo Python найден в %LOCALAPPDATA%\Programs\Python\Python39 >> install_debug.log
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    goto PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python38\python.exe" (
    echo Python найден в %LOCALAPPDATA%\Programs\Python\Python38 >> install_debug.log
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python38\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files\Python311\python.exe" (
    echo Python найден в C:\Program Files\Python311 >> install_debug.log
    set "PYTHON_CMD=C:\Program Files\Python311\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files\Python310\python.exe" (
    echo Python найден в C:\Program Files\Python310 >> install_debug.log
    set "PYTHON_CMD=C:\Program Files\Python310\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files\Python39\python.exe" (
    echo Python найден в C:\Program Files\Python39 >> install_debug.log
    set "PYTHON_CMD=C:\Program Files\Python39\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files\Python38\python.exe" (
    echo Python найден в C:\Program Files\Python38 >> install_debug.log
    set "PYTHON_CMD=C:\Program Files\Python38\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files (x86)\Python311\python.exe" (
    echo Python найден в C:\Program Files (x86)\Python311 >> install_debug.log
    set "PYTHON_CMD=C:\Program Files (x86)\Python311\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files (x86)\Python310\python.exe" (
    echo Python найден в C:\Program Files (x86)\Python310 >> install_debug.log
    set "PYTHON_CMD=C:\Program Files (x86)\Python310\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files (x86)\Python39\python.exe" (
    echo Python найден в C:\Program Files (x86)\Python39 >> install_debug.log
    set "PYTHON_CMD=C:\Program Files (x86)\Python39\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files (x86)\Python38\python.exe" (
    echo Python найден в C:\Program Files (x86)\Python38 >> install_debug.log
    set "PYTHON_CMD=C:\Program Files (x86)\Python38\python.exe"
    goto PYTHON_FOUND
)

REM Если мы здесь, значит Python не найден
echo ОШИБКА: Python не найден в системе >> install_debug.log
echo ОШИБКА: Python не найден.
echo Пожалуйста, установите Python 3.8 или выше.
echo Вы можете скачать Python с официального сайта: https://www.python.org/downloads/
echo При установке отметьте опцию "Add Python to PATH".
pause
exit /b 1

:PYTHON_FOUND
echo Используемая команда Python: %PYTHON_CMD%
echo Используемая команда Python: %PYTHON_CMD% >> install_debug.log

REM Проверяем версию Python
echo Проверка версии Python...
echo Проверка версии Python... >> install_debug.log
%PYTHON_CMD% --version 
%PYTHON_CMD% --version >> install_debug.log 2>&1

REM Проверяем наличие файла launch_heatmap.py
if not exist "launch_heatmap.py" (
    echo ОШИБКА: Файл launch_heatmap.py не найден
    echo ОШИБКА: Файл launch_heatmap.py не найден >> install_debug.log
    pause
    exit /b 1
)

REM Запускаем установку виртуального окружения и зависимостей
echo.
echo Установка виртуального окружения и зависимостей...
echo Установка виртуального окружения и зависимостей... >> install_debug.log

REM Запускаем Python для установки виртуального окружения и зависимостей
%PYTHON_CMD% -u launch_heatmap.py --install-only

if %ERRORLEVEL% NEQ 0 (
    echo Произошла ошибка при установке (код %ERRORLEVEL%)
    echo Произошла ошибка при установке (код %ERRORLEVEL%) >> install_debug.log
    echo.
    echo Подробности в файле python_debug.log
    pause
    exit /b 1
)

echo.
echo Окружение и библиотеки успешно установлены!
echo Окружение и библиотеки успешно установлены! >> install_debug.log
echo.
echo Теперь вы можете запустить приложение HeatMapCAD с помощью run_heatmap.bat
echo.
pause
exit /b 0 