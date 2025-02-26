#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для запуска HeatMapCAD.
Автоматически создает виртуальное окружение, устанавливает необходимые зависимости и запускает приложение.
"""

import os
import sys
import subprocess
import time
import traceback
import platform

# Создаем отладочный лог-файл
debug_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "python_debug.log")
def log_debug(message):
    """Записывает отладочное сообщение в лог-файл."""
    try:
        with open(debug_log_path, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except PermissionError:
        # Если нет доступа к файлу, пытаемся создать лог в другом месте
        alternate_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alternative_debug.log")
        try:
            with open(alternate_log_path, "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - [ALTERNATE LOG] {message}\n")
        except Exception:
            # Если и это не сработало, выводим сообщение на экран
            print(f"ОТЛАДКА: {message}")

# Записываем начальную информацию
log_debug("=" * 50)
log_debug("Запуск скрипта launch_heatmap.py")
log_debug(f"Python: {sys.version}")
log_debug(f"Путь к Python: {sys.executable}")
log_debug(f"Рабочая директория: {os.getcwd()}")
log_debug(f"Директория скрипта: {os.path.dirname(os.path.abspath(__file__))}")

# Проверяем наличие модуля venv
try:
    import venv
    log_debug("Модуль venv успешно импортирован")
except ImportError as e:
    log_debug(f"Ошибка импорта модуля venv: {e}")
    print(f"Ошибка: Не удалось импортировать модуль venv: {e}")
    sys.exit(1)

def check_python_version():
    """Проверяет версию Python."""
    print("Проверка версии Python...")
    log_debug("Проверка версии Python...")
    
    # Минимальная требуемая версия Python
    min_version = (3, 8)
    
    # Получаем текущую версию Python
    current_version = sys.version_info[:2]
    
    # Проверяем, соответствует ли текущая версия требованиям
    if current_version < min_version:
        error_msg = f"Ошибка: Требуется Python {min_version[0]}.{min_version[1]} или выше. Текущая версия: {current_version[0]}.{current_version[1]}"
        print(error_msg)
        log_debug(error_msg)
        return False
    
    log_debug(f"Версия Python: {current_version[0]}.{current_version[1]} - OK")
    print(f"Версия Python: {current_version[0]}.{current_version[1]}")
    return True

def create_virtual_environment():
    """Создает виртуальное окружение, если оно не существует."""
    print("Проверка виртуального окружения...")
    log_debug("Проверка виртуального окружения...")
    
    # Путь к директории виртуального окружения
    venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv")
    log_debug(f"Путь к виртуальному окружению: {venv_dir}")
    
    # Проверяем, существует ли виртуальное окружение
    if os.path.exists(venv_dir):
        log_debug(f"Виртуальное окружение найдено: {venv_dir}")
        print(f"Виртуальное окружение найдено: {venv_dir}")
        return venv_dir
    
    # Создаем виртуальное окружение
    try:
        log_debug(f"Создание виртуального окружения в {venv_dir}...")
        print(f"Создание виртуального окружения в {venv_dir}...")
        venv.create(venv_dir, with_pip=True)
        log_debug("Виртуальное окружение успешно создано.")
        print("Виртуальное окружение успешно создано.")
        return venv_dir
    except Exception as e:
        error_msg = f"Ошибка при создании виртуального окружения: {e}"
        log_debug(error_msg)
        log_debug(traceback.format_exc())
        print(error_msg)
        return None

def get_venv_python_path(venv_dir):
    """Возвращает путь к интерпретатору Python в виртуальном окружении."""
    if platform.system() == "Windows":
        python_path = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        python_path = os.path.join(venv_dir, "bin", "python")
    
    log_debug(f"Путь к Python в виртуальном окружении: {python_path}")
    log_debug(f"Существует: {os.path.exists(python_path)}")
    return python_path

def install_dependencies(venv_dir):
    """Устанавливает необходимые зависимости в виртуальное окружение."""
    print("Проверка и установка зависимостей...")
    log_debug("Проверка и установка зависимостей...")
    
    # Путь к файлу с зависимостями
    requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    log_debug(f"Путь к файлу с зависимостями: {requirements_file}")
    
    # Проверяем наличие файла с зависимостями
    if not os.path.exists(requirements_file):
        error_msg = f"Ошибка: Файл {requirements_file} не найден."
        log_debug(error_msg)
        print(error_msg)
        return False
    
    # Путь к интерпретатору Python в виртуальном окружении
    venv_python = get_venv_python_path(venv_dir)
    
    # Устанавливаем зависимости
    try:
        log_debug("Установка зависимостей...")
        print("Установка зависимостей...")
        
        # Обновляем pip
        log_debug("Обновление pip...")
        pip_upgrade_cmd = [venv_python, "-m", "pip", "install", "--upgrade", "pip"]
        log_debug(f"Команда: {' '.join(pip_upgrade_cmd)}")
        subprocess.check_call(pip_upgrade_cmd)
        
        # Устанавливаем зависимости
        log_debug("Установка зависимостей из requirements.txt...")
        install_cmd = [venv_python, "-m", "pip", "install", "-r", requirements_file]
        log_debug(f"Команда: {' '.join(install_cmd)}")
        subprocess.check_call(install_cmd)
        
        log_debug("Зависимости успешно установлены.")
        print("Зависимости успешно установлены.")
        return True
    except Exception as e:
        error_msg = f"Ошибка при установке зависимостей: {e}"
        log_debug(error_msg)
        log_debug(traceback.format_exc())
        print(error_msg)
        return False

def check_src_directory():
    """Проверяет наличие директории src и основных файлов."""
    print("Проверка структуры проекта...")
    log_debug("Проверка структуры проекта...")
    
    # Путь к директории src
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
    log_debug(f"Путь к директории src: {src_dir}")
    
    # Проверяем наличие директории src
    if not os.path.exists(src_dir):
        error_msg = f"Ошибка: Директория {src_dir} не найдена"
        log_debug(error_msg)
        print(error_msg)
        return False
    
    # Проверяем наличие основных файлов
    main_file = os.path.join(src_dir, "main.py")
    log_debug(f"Путь к main.py: {main_file}")
    log_debug(f"Существует: {os.path.exists(main_file)}")
    
    if not os.path.exists(main_file):
        error_msg = f"Ошибка: Файл {main_file} не найден"
        log_debug(error_msg)
        print(error_msg)
        return False
    
    # Проверяем содержимое директории src
    try:
        src_contents = os.listdir(src_dir)
        log_debug(f"Содержимое директории src: {src_contents}")
    except Exception as e:
        log_debug(f"Ошибка при чтении содержимого директории src: {e}")
    
    log_debug("Структура проекта в порядке")
    print("Структура проекта в порядке")
    return True

def run_application(venv_dir):
    """Запускает приложение из виртуального окружения."""
    print("Запуск приложения HeatMapCAD...")
    log_debug("Запуск приложения HeatMapCAD...")
    
    # Путь к интерпретатору Python в виртуальном окружении
    venv_python = get_venv_python_path(venv_dir)
    
    # Путь к основному файлу приложения
    main_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "main.py")
    log_debug(f"Путь к основному файлу приложения: {main_file}")
    
    try:
        # Запускаем приложение из виртуального окружения
        log_debug(f"Запуск команды: {venv_python} {main_file}")
        subprocess.check_call([venv_python, main_file])
        log_debug("Приложение успешно запущено")
        return True
    except Exception as e:
        error_msg = f"Ошибка при запуске приложения: {e}\n\n"
        error_msg += traceback.format_exc()
        
        log_debug(error_msg)
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
        except Exception as dialog_error:
            log_debug(f"Не удалось показать диалоговое окно с ошибкой: {dialog_error}")
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
    log_debug("Создан лог-файл: " + log_file)
    
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
            log_debug("Ошибка: Неподходящая версия Python")
            input("Нажмите Enter для выхода...")
            return 1
        
        # Проверяем структуру проекта
        if not check_src_directory():
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("Ошибка: Структура проекта нарушена\n")
            log_debug("Ошибка: Структура проекта нарушена")
            input("Нажмите Enter для выхода...")
            return 1
        
        # Создаем виртуальное окружение
        venv_dir = create_virtual_environment()
        if not venv_dir:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("Ошибка: Не удалось создать виртуальное окружение\n")
            log_debug("Ошибка: Не удалось создать виртуальное окружение")
            input("Нажмите Enter для выхода...")
            return 1
        
        # Устанавливаем зависимости
        if not install_dependencies(venv_dir):
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("Ошибка: Не удалось установить зависимости\n")
            log_debug("Ошибка: Не удалось установить зависимости")
            input("Нажмите Enter для выхода...")
            return 1
        
        # Запускаем приложение
        if not run_application(venv_dir):
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("Ошибка: Не удалось запустить приложение\n")
            log_debug("Ошибка: Не удалось запустить приложение")
            return 1
        
        log_debug("Приложение успешно запущено и завершено")
        return 0
    
    except Exception as e:
        # Если произошла ошибка при запуске, записываем её в лог-файл
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"Критическая ошибка: {e}\n")
                f.write(traceback.format_exc())
            log_debug(f"Критическая ошибка: {e}")
            log_debug(traceback.format_exc())
        except:
            pass
        
        print(f"Критическая ошибка: {e}")
        print(traceback.format_exc())
        input("Нажмите Enter для выхода...")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 