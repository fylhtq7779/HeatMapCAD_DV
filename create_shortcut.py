#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для создания ярлыка HeatMapCAD на рабочем столе.
"""

import os
import sys
import platform
import subprocess

def create_windows_shortcut():
    """Создает ярлык для Windows."""
    print("Создание ярлыка для Windows...")
    
    # Получаем путь к рабочему столу
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(desktop_path):
        # Проверяем русскую локализацию
        desktop_path = os.path.join(os.path.expanduser("~"), "Рабочий стол")
        if not os.path.exists(desktop_path):
            desktop_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Рабочий стол")
            if not os.path.exists(desktop_path):
                print("Не удалось найти путь к рабочему столу.")
                return False
    
    # Путь к текущей директории
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Путь к Python
    python_path = sys.executable
    
    # Путь к скрипту запуска
    launch_script = os.path.join(current_dir, "launch_heatmap.py")
    
    # Создаем BAT-файл для запуска
    bat_path = os.path.join(desktop_path, "HeatMapCAD.bat")
    
    with open(bat_path, "w", encoding="utf-8") as bat_file:
        bat_file.write(f'@echo off\n')
        bat_file.write(f'echo Запуск HeatMapCAD...\n')
        bat_file.write(f'cd /d "{current_dir}"\n')
        bat_file.write(f'"{python_path}" "{launch_script}"\n')
        bat_file.write(f'if errorlevel 1 pause\n')
    
    print(f"Ярлык создан: {bat_path}")
    return True

def create_linux_shortcut():
    """Создает ярлык для Linux."""
    print("Создание ярлыка для Linux...")
    
    # Получаем путь к рабочему столу
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # Путь к текущей директории
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Путь к скрипту запуска
    launch_script = os.path.join(current_dir, "start_heatmap.sh")
    
    # Делаем скрипт запуска исполняемым
    os.chmod(launch_script, 0o755)
    
    # Создаем .desktop файл
    desktop_file_path = os.path.join(desktop_path, "HeatMapCAD.desktop")
    
    with open(desktop_file_path, "w", encoding="utf-8") as desktop_file:
        desktop_file.write("[Desktop Entry]\n")
        desktop_file.write("Type=Application\n")
        desktop_file.write("Name=HeatMapCAD\n")
        desktop_file.write("Comment=Тепловая карта активности в САПР системах\n")
        desktop_file.write(f"Exec={launch_script}\n")
        desktop_file.write("Terminal=false\n")
        desktop_file.write("Categories=Utility;\n")
    
    # Делаем .desktop файл исполняемым
    os.chmod(desktop_file_path, 0o755)
    
    print(f"Ярлык создан: {desktop_file_path}")
    return True

def create_macos_shortcut():
    """Создает ярлык для macOS."""
    print("Создание ярлыка для macOS...")
    
    # Получаем путь к рабочему столу
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # Путь к текущей директории
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Путь к скрипту запуска
    launch_script = os.path.join(current_dir, "start_heatmap.sh")
    
    # Делаем скрипт запуска исполняемым
    os.chmod(launch_script, 0o755)
    
    # Создаем AppleScript для запуска
    applescript_path = os.path.join(desktop_path, "HeatMapCAD.scpt")
    
    applescript = f'''
    tell application "Terminal"
        do script "cd {current_dir} && {launch_script}"
    end tell
    '''
    
    # Сохраняем AppleScript
    try:
        subprocess.run(["osascript", "-e", applescript], check=True)
        print(f"Ярлык создан: {applescript_path}")
        return True
    except subprocess.CalledProcessError:
        print("Не удалось создать ярлык для macOS.")
        return False

def main():
    """Основная функция."""
    print("=" * 50)
    print("Создание ярлыка HeatMapCAD")
    print("=" * 50)
    
    # Определяем операционную систему
    system = platform.system()
    
    if system == "Windows":
        create_windows_shortcut()
    elif system == "Linux":
        create_linux_shortcut()
    elif system == "Darwin":  # macOS
        create_macos_shortcut()
    else:
        print(f"Неподдерживаемая операционная система: {system}")
        return 1
    
    print("Ярлык успешно создан.")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 