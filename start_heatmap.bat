@echo off
chcp 65001 > nul
echo Запуск HeatMapCAD...
echo.

REM Путь к маркерному файлу для определения первого запуска
set FIRST_RUN_MARKER=.first_run_completed

REM Параметр для скрытого запуска
set SILENT_MODE=%1

REM Проверяем, существует ли маркерный файл (первый запуск завершен)
if exist "%FIRST_RUN_MARKER%" (
    set FIRST_RUN=0
) else (
    set FIRST_RUN=1
)

REM Если это не первый запуск и запрошен скрытый режим, переходим к скрытому запуску
if "%FIRST_RUN%"=="0" if "%SILENT_MODE%"=="silent" goto SILENT_LAUNCH

REM Создаем файл для отладки
echo Начало отладки > debug_launch.log
echo Время: %date% %time% >> debug_launch.log

REM Ищем Python в системе
echo Поиск Python в системе...
echo Поиск Python в системе... >> debug_launch.log

REM Пробуем использовать py.exe лаунчер (если установлен Python Launcher)
set PYTHON_PATH=
WHERE py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python Launcher найден
    echo Python Launcher найден >> debug_launch.log
    set "PYTHON_CMD=py -3"
    goto PYTHON_FOUND
)

REM Пробуем найти python.exe через where
WHERE python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python найден через where команду
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
echo Используемая команда Python: %PYTHON_CMD%
echo Используемая команда Python: %PYTHON_CMD% >> debug_launch.log

REM Проверяем версию Python
echo Проверка версии Python...
echo Проверка версии Python... >> debug_launch.log
%PYTHON_CMD% --version 
%PYTHON_CMD% --version >> debug_launch.log 2>&1

REM Проверяем наличие файла launch_heatmap.py
if not exist "launch_heatmap.py" (
    echo ОШИБКА: Файл launch_heatmap.py не найден
    echo ОШИБКА: Файл launch_heatmap.py не найден >> debug_launch.log
    pause
    exit /b 1
)

REM Запускаем приложение - ИЗМЕНЕНО: вывод в консоль
echo Запуск приложения...
echo Запуск приложения... >> debug_launch.log
echo Запуск команды: %PYTHON_CMD% -u launch_heatmap.py
echo Запуск команды: %PYTHON_CMD% -u launch_heatmap.py >> debug_launch.log

REM Сохраняем вывод Python в переменную, чтобы проверить на маркер первого запуска
set FIRST_RUN_COMPLETED=0
for /f "tokens=*" %%a in ('%PYTHON_CMD% -u launch_heatmap.py') do (
    echo %%a
    if "%%a"=="[FIRST_RUN_COMPLETED]" set FIRST_RUN_COMPLETED=1
)

if %ERRORLEVEL% NEQ 0 (
    echo Произошла ошибка при запуске приложения (код %ERRORLEVEL%)
    echo Произошла ошибка при запуске приложения (код %ERRORLEVEL%) >> debug_launch.log
    echo.
    echo Подробности в файле python_debug.log
    pause
    exit /b 1
)

echo Приложение успешно запущено
echo Приложение успешно запущено >> debug_launch.log

REM Если это был первый запуск и он успешно завершен, предлагаем нажать любую клавишу
if "%FIRST_RUN%"=="1" if "%FIRST_RUN_COMPLETED%"=="1" (
    echo.
    echo Первый запуск успешно завершен. При следующем запуске консоль не будет отображаться.
    echo.
    echo Создаем ярлык для бесшумного запуска...
    
    REM Создаем ярлык для скрытого запуска
    echo @echo off > HeatMapCAD.bat
    echo start "" /b cmd /c "start_heatmap.bat silent" >> HeatMapCAD.bat
    
    echo Ярлык HeatMapCAD.bat создан в текущей директории.
    echo.
    pause
)

exit /b 0

:SILENT_LAUNCH
REM Скрытый запуск приложения для последующих запусков
%PYTHON_CMD% -u launch_heatmap.py > nul 2>&1
exit /b 0 