#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для запуска HeatMapCAD.
Автоматически устанавливает необходимые зависимости и запускает приложение.
"""

import os
import sys
import subprocess
import time
import traceback

def check_python_version():
    """Проверяет версию Python."""
    print("Проверка версии Python...")
    
    # Минимальная требуемая версия Python
    min_version = (3, 8)
    
    # Получаем текущую версию Python
    current_version = sys.version_info[:2]
    
    # Проверяем, соответствует ли текущая версия требованиям
    if current_version < min_version:
        print(f"Ошибка: Требуется Python {min_version[0]}.{min_version[1]} или выше.")
        print(f"Текущая версия: {current_version[0]}.{current_version[1]}")
        return False
    
    print(f"Версия Python: {current_version[0]}.{current_version[1]}")
    return True

def install_dependencies():
    """Устанавливает необходимые зависимости."""
    print("Проверка и установка зависимостей...")
    
    # Путь к файлу с зависимостями
    requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    
    # Проверяем наличие файла с зависимостями
    if not os.path.exists(requirements_file):
        print(f"Ошибка: Файл {requirements_file} не найден.")
        return False
    
    # Устанавливаем зависимости
    try:
        print("Установка зависимостей...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("Зависимости успешно установлены.")
        return True
    except Exception as e:
        print(f"Ошибка при установке зависимостей: {e}")
        return False

def check_src_directory():
    """Проверяет наличие директории src и основных файлов."""
    print("Проверка структуры проекта...")
    
    # Путь к директории src
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
    
    # Проверяем наличие директории src
    if not os.path.exists(src_dir):
        print(f"Ошибка: Директория {src_dir} не найдена")
        return False
    
    # Проверяем наличие основных файлов
    main_file = os.path.join(src_dir, "main.py")
    if not os.path.exists(main_file):
        print(f"Ошибка: Файл {main_file} не найден")
        return False
    
    print("Структура проекта в порядке")
    return True

def run_application():
    """Запускает приложение."""
    print("Запуск приложения HeatMapCAD...")
    
    # Добавляем путь к исходному коду в PYTHONPATH
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
    
    try:
        # Импортируем и запускаем приложение
        from src.main import Application
        app = Application()
        app.run()
        return True
    except Exception as e:
        error_msg = f"Ошибка при запуске приложения: {e}\n\n"
        error_msg += traceback.format_exc()
        
        print(error_msg)
        
        # Записываем ошибку в лог-файл
        with open("error_log.txt", "w", encoding="utf-8") as log:
            log.write(error_msg)
        
        # Показываем диалоговое окно с ошибкой
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Ошибка", f"Произошла ошибка при запуске приложения:\n{e}\n\nПодробности записаны в файл error_log.txt")
        except:
            # Если не удалось показать диалоговое окно, просто ждем ввода
            input("Нажмите Enter для выхода...")
        
        return False

def main():
    """Основная функция."""
    print("=" * 50)
    print("Запуск HeatMapCAD")
    print("=" * 50)
    
    # Создаем лог-файл для записи ошибок
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "launch_log.txt")
    
    try:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"Запуск HeatMapCAD: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"Путь к Python: {sys.executable}\n")
            f.write(f"Рабочая директория: {os.getcwd()}\n")
            f.write(f"Директория скрипта: {os.path.dirname(os.path.abspath(__file__))}\n\n")
        
        print(f"Запуск HeatMapCAD...")
        print(f"Python: {sys.version}")
        print(f"Путь к Python: {sys.executable}")
        print(f"Рабочая директория: {os.getcwd()}")
        print(f"Директория скрипта: {os.path.dirname(os.path.abspath(__file__))}")
        
        # Проверяем версию Python
        if not check_python_version():
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("Ошибка: Неподходящая версия Python\n")
            input("Нажмите Enter для выхода...")
            return 1
        
        # Проверяем структуру проекта
        if not check_src_directory():
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("Ошибка: Структура проекта нарушена\n")
            input("Нажмите Enter для выхода...")
            return 1
        
        # Устанавливаем зависимости
        if not install_dependencies():
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("Ошибка: Не удалось установить зависимости\n")
            input("Нажмите Enter для выхода...")
            return 1
        
        # Запускаем приложение
        if not run_application():
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("Ошибка: Не удалось запустить приложение\n")
            return 1
        
        return 0
    
    except Exception as e:
        # Если произошла ошибка при запуске, записываем её в лог-файл
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"Критическая ошибка: {e}\n")
                f.write(traceback.format_exc())
        except:
            pass
        
        print(f"Критическая ошибка: {e}")
        print(traceback.format_exc())
        input("Нажмите Enter для выхода...")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 