#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для создания портативного архива HeatMapCAD.
"""

import os
import sys
import shutil
import zipfile
import datetime

def create_portable_archive():
    """Создает портативный архив HeatMapCAD."""
    print("Создание портативного архива HeatMapCAD...")
    
    # Текущая директория
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Имя архива
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    archive_name = f"HeatMapCAD_Portable_{date_str}.zip"
    
    # Список файлов и директорий для включения в архив
    include_files = [
        "launch_heatmap.py",
        "start_heatmap.bat",
        "start_heatmap.sh",
        "requirements.txt",
        "README_PORTABLE.md",
        "LICENSE.txt",
        "USER_GUIDE.txt"
    ]
    
    include_dirs = [
        "src",
        "config",
        "data"
    ]
    
    # Проверяем наличие всех необходимых файлов и директорий
    missing_files = []
    for file in include_files:
        if not os.path.exists(os.path.join(current_dir, file)):
            missing_files.append(file)
    
    missing_dirs = []
    for dir_name in include_dirs:
        if not os.path.exists(os.path.join(current_dir, dir_name)):
            missing_dirs.append(dir_name)
    
    if missing_files or missing_dirs:
        print("ОШИБКА: Не найдены следующие файлы или директории:")
        for file in missing_files:
            print(f"  - {file}")
        for dir_name in missing_dirs:
            print(f"  - {dir_name}/")
        return False
    
    # Создаем архив
    try:
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Добавляем файлы
            for file in include_files:
                if os.path.exists(os.path.join(current_dir, file)):
                    print(f"Добавление файла: {file}")
                    zipf.write(os.path.join(current_dir, file), file)
            
            # Добавляем директории
            for dir_name in include_dirs:
                dir_path = os.path.join(current_dir, dir_name)
                if os.path.exists(dir_path):
                    print(f"Добавление директории: {dir_name}/")
                    for root, dirs, files in os.walk(dir_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, current_dir)
                            print(f"  - {arcname}")
                            zipf.write(file_path, arcname)
        
        print(f"Архив успешно создан: {archive_name}")
        print(f"Размер архива: {os.path.getsize(archive_name) / (1024*1024):.2f} МБ")
        return True
    
    except Exception as e:
        print(f"Ошибка при создании архива: {e}")
        return False

def main():
    """Основная функция."""
    print("=" * 50)
    print("Создание портативного архива HeatMapCAD")
    print("=" * 50)
    
    if create_portable_archive():
        print("Архив успешно создан.")
        return 0
    else:
        print("Не удалось создать архив.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 