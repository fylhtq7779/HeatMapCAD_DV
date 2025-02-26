#!/bin/bash

echo "Запуск HeatMapCAD..."

# Проверяем наличие Python
if command -v python3 &>/dev/null; then
    echo "Python найден, запуск приложения..."
    python3 launch_heatmap.py
    exit $?
fi

if command -v python &>/dev/null; then
    # Проверяем версию Python
    python_version=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1)
    if [ "$python_version" -ge 3 ]; then
        echo "Python найден, запуск приложения..."
        python launch_heatmap.py
        exit $?
    else
        echo "ОШИБКА: Найден Python $python_version, но требуется Python 3.8 или выше."
    fi
fi

echo "ОШИБКА: Python не найден. Пожалуйста, установите Python 3.8 или выше."
echo "Вы можете установить Python с помощью менеджера пакетов вашей системы или скачать с официального сайта: https://www.python.org/downloads/"
read -p "Нажмите Enter для выхода..."
exit 1 