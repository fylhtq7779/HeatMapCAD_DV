#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Точка входа для исполняемого файла HeatMapCAD.
Этот файл загружает и запускает основное приложение.
"""

import os
import sys
import traceback
from pathlib import Path

# Настраиваем корректные пути
def setup_paths():
    # Определяем, запущены ли мы как исполняемый файл или как обычный Python скрипт
    if getattr(sys, 'frozen', False):
        # Если мы запущены как frozen приложение
        application_path = os.path.dirname(sys.executable)
    else:
        # Если мы запущены как обычный Python скрипт
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # Добавляем основной каталог и src в путь Python
    if application_path not in sys.path:
        sys.path.insert(0, application_path)
    
    src_path = os.path.join(application_path, 'src')
    if os.path.exists(src_path) and src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Добавляем пути к подмодулям (core, visualization и т.д.)
    for submodule in ['core', 'visualization', 'data', 'network', 'utils', 'ui']:
        mod_path = os.path.join(src_path, submodule)
        if os.path.exists(mod_path) and mod_path not in sys.path:
            sys.path.insert(0, mod_path)
    
    return application_path

def main():
    try:
        # Настраиваем пути
        app_path = setup_paths()
        
        # Выводим пути для отладки
        if getattr(sys, 'frozen', False):
            print("Запущен как замороженное приложение")
            print(f"Исполняемый файл: {sys.executable}")
        else:
            print("Запущен как Python скрипт")
        
        print("Python paths:")
        for path in sys.path:
            print(f"- {path}")
        
        # Импортируем и запускаем основное приложение
        from src.main import Application
        
        # Создаем и запускаем приложение
        app = Application()
        app.run()
    
    except Exception as e:
        # Обработка ошибок
        error_message = f"Ошибка при запуске приложения: {str(e)}\n"
        error_message += traceback.format_exc()
        
        # Записываем ошибку в лог
        try:
            log_path = os.path.join(app_path, "error_log.txt")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(error_message)
            print(f"Подробности об ошибке записаны в файл: {log_path}")
        except Exception as log_error:
            print(f"Не удалось записать лог ошибки: {log_error}")
            print(error_message)
        
        # Показываем сообщение об ошибке
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Ошибка", f"Произошла ошибка при запуске приложения:\n{str(e)}\n\nПодробности записаны в файл error_log.txt")
            root.destroy()
        except:
            print(error_message)
        
        sys.exit(1)

if __name__ == "__main__":
    main() 