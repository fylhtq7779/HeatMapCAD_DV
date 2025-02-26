@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

REM Проверяем наличие маркера первого запуска
set FIRST_RUN=0
if not exist ".first_run_completed" set FIRST_RUN=1

REM Проверяем, существует ли VBS файл для скрытого запуска
if exist "HeatMapCAD.vbs" (
    echo Запуск HeatMapCAD в скрытом режиме...
    start "" "HeatMapCAD.vbs"
    exit /b 0
)

REM Если это первый запуск или нет VBS файла, запускаем обычным способом
echo Запуск HeatMapCAD...

REM Пробуем использовать py.exe лаунчер (если установлен Python Launcher)
set PYTHON_PATH=
WHERE py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=py -3"
    goto PYTHON_FOUND
)

REM Пробуем найти python.exe через where
WHERE python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=python"
    goto PYTHON_FOUND
)

REM Пробуем наиболее распространенные пути установки Python
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    goto PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    goto PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python38\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python38\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files\Python311\python.exe" (
    set "PYTHON_CMD=C:\Program Files\Python311\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files\Python310\python.exe" (
    set "PYTHON_CMD=C:\Program Files\Python310\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files\Python39\python.exe" (
    set "PYTHON_CMD=C:\Program Files\Python39\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files\Python38\python.exe" (
    set "PYTHON_CMD=C:\Program Files\Python38\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files (x86)\Python311\python.exe" (
    set "PYTHON_CMD=C:\Program Files (x86)\Python311\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files (x86)\Python310\python.exe" (
    set "PYTHON_CMD=C:\Program Files (x86)\Python310\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files (x86)\Python39\python.exe" (
    set "PYTHON_CMD=C:\Program Files (x86)\Python39\python.exe"
    goto PYTHON_FOUND
)

if exist "C:\Program Files (x86)\Python38\python.exe" (
    set "PYTHON_CMD=C:\Program Files (x86)\Python38\python.exe"
    goto PYTHON_FOUND
)

REM Если мы здесь, значит Python не найден
echo ОШИБКА: Python не найден.
echo Пожалуйста, запустите install_environment.bat для установки окружения.
pause
exit /b 1

:PYTHON_FOUND
REM Проверяем наличие виртуального окружения
if not exist "venv" (
    echo ОШИБКА: Виртуальное окружение не найдено.
    echo Пожалуйста, запустите install_environment.bat для установки окружения.
    pause
    exit /b 1
)

REM Запускаем приложение
%PYTHON_CMD% -u launch_heatmap.py

REM Проверяем, создан ли маркер первого запуска
if %FIRST_RUN%==1 (
    if exist ".first_run_completed" (
        echo Создание VBS файла для скрытого запуска...
        
        REM Создаем VBS файл для скрытого запуска
        echo Set WshShell = CreateObject("WScript.Shell") > HeatMapCAD.vbs
        echo WshShell.Run """cmd /c %~dp0run_heatmap.bat --hidden""", 0, False >> HeatMapCAD.vbs
        
        echo VBS файл создан. В следующий раз программа запустится в скрытом режиме.
        echo Для видимого запуска используйте run_heatmap.bat
        echo Для скрытого запуска используйте HeatMapCAD.vbs
        pause
    )
)

REM Если запуск с параметром --hidden, то не показываем сообщение о завершении
echo %* | findstr /C:"--hidden" >nul
if %ERRORLEVEL% EQU 0 exit /b 0

echo Программа завершена.
exit /b 0 