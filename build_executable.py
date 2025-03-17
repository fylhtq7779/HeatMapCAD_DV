#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для создания исполняемого файла HeatMapCAD.
Использует PyInstaller для создания .exe файла.
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

def create_icon():
    """Создает простую иконку приложения, если она не существует."""
    icon_path = os.path.join('assets', 'icon.ico')
    
    if os.path.exists(icon_path):
        print(f"Иконка уже существует по пути: {icon_path}")
        return
    
    try:
        # Попробуем создать иконку с помощью Pillow
        from PIL import Image, ImageDraw
        
        # Создаем директорию, если она не существует
        os.makedirs('assets', exist_ok=True)
        
        # Создаем простую иконку
        size = 256
        img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Рисуем фон
        draw.ellipse((0, 0, size, size), fill=(30, 144, 255))
        
        # Рисуем градиентные круги для тепловой карты
        colors = [
            (255, 0, 0, 180),    # Красный
            (255, 165, 0, 150),  # Оранжевый
            (255, 255, 0, 120)   # Желтый
        ]
        
        centers = [
            (size * 0.4, size * 0.4),
            (size * 0.6, size * 0.6),
            (size * 0.5, size * 0.5)
        ]
        
        for i, (center, color) in enumerate(zip(centers, colors)):
            radius = size * (0.3 - i * 0.05)
            x0, y0 = center[0] - radius, center[1] - radius
            x1, y1 = center[0] + radius, center[1] + radius
            draw.ellipse((x0, y0, x1, y1), fill=color)
        
        # Сохраняем как .ico
        img.save(icon_path, format='ICO')
        print(f"Иконка создана по пути: {icon_path}")
    
    except Exception as e:
        print(f"Не удалось создать иконку: {e}")
        print("Приложение будет создано без иконки")

def clean_build_directories():
    """Очищает директории сборки для нового процесса."""
    directories = ['build', 'dist']
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"Очистка директории: {directory}")
            try:
                shutil.rmtree(directory)
            except Exception as e:
                print(f"Ошибка при очистке {directory}: {e}")
    
    # Также удаляем автоматически созданный .spec файл для одиночного файла
    spec_file = 'HeatMapCAD_Single.spec'
    if os.path.exists(spec_file):
        print(f"Удаление файла спецификации: {spec_file}")
        try:
            os.remove(spec_file)
        except Exception as e:
            print(f"Ошибка при удалении {spec_file}: {e}")
    
    # Очищаем кэш PyInstaller
    cache_dir = os.path.expanduser(os.path.join('~', '.pyinstaller'))
    if os.path.exists(cache_dir):
        print(f"Очистка кэша PyInstaller: {cache_dir}")
        try:
            for item in os.listdir(cache_dir):
                item_path = os.path.join(cache_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
        except Exception as e:
            print(f"Ошибка при очистке кэша: {e}")

def find_python_dll_path():
    """Находит путь к python DLL в системе."""
    import sys
    python_path = os.path.dirname(sys.executable)
    python_version = f"{sys.version_info.major}{sys.version_info.minor}"
    dll_name = f"python{python_version}.dll"
    
    # Проверяем в директории Python
    dll_path = os.path.join(python_path, dll_name)
    if os.path.exists(dll_path):
        return dll_path
    
    # Проверяем в системной директории Windows
    system32_path = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32', dll_name)
    if os.path.exists(system32_path):
        return system32_path
    
    # Проверяем в SysWOW64 для 64-битных систем
    syswow64_path = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'SysWOW64', dll_name)
    if os.path.exists(syswow64_path):
        return syswow64_path
    
    print(f"ВНИМАНИЕ: Не удалось найти {dll_name}. Сборка может не работать корректно.")
    return None

def build_executable():
    """Запускает процесс сборки с использованием PyInstaller."""
    print("Запуск сборки исполняемого файла...")
    
    # Находим путь к Python DLL
    python_dll_path = find_python_dll_path()
    if python_dll_path:
        print(f"Найден Python DLL: {python_dll_path}")
    
    # Команда для запуска PyInstaller с дополнительными опциями
    pyinstaller_cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',  # Не спрашивать подтверждения при перезаписи файлов
        '--log-level=INFO',  # Подробный вывод для диагностики
        'heatmap.spec'
    ]
    
    # Запускаем процесс сборки
    try:
        subprocess.run(pyinstaller_cmd, check=True)
        print("Сборка завершена успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при сборке: {e}")
        return False

def create_single_file_executable():
    """Создает одиночный исполняемый файл, который включает в себя все зависимости."""
    print("Создание единого исполняемого файла...")
    
    # Удаляем существующий файл, если он есть
    output_file = os.path.join('dist', 'HeatMapCAD_Single.exe')
    if os.path.exists(output_file):
        print(f"Удаление существующего файла: {output_file}")
        try:
            os.remove(output_file)
        except Exception as e:
            print(f"Ошибка при удалении {output_file}: {e}")
            print("Продолжаем сборку...")
    
    # Находим путь к Python DLL
    python_dll_path = find_python_dll_path()
    bin_option = []
    
    # Если мы нашли DLL, явно добавляем его в сборку
    if python_dll_path:
        bin_path = f"{python_dll_path};."
        bin_option = ['--add-binary', bin_path]
        print(f"Добавляем Python DLL в сборку: {python_dll_path}")
    
    # Команда для создания одиночного файла с дополнительными опциями
    pyinstaller_cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',  # Не спрашивать подтверждения при перезаписи файлов
        '--log-level=INFO',  # Подробный вывод для диагностики
        '--onefile',
        '--windowed',  # Без консоли
        '--add-data', f'config{os.pathsep}config',
        '--add-data', f'src{os.pathsep}.',  # Перемещаем src в корень для корректной работы импортов
        '--add-data', f'LICENSE.txt{os.pathsep}.',
        '--add-data', f'USER_GUIDE.txt{os.pathsep}.',
        '--add-data', f'assets{os.pathsep}assets',
        '--icon', os.path.join('assets', 'icon.ico'),
        '--paths', os.path.join(os.getcwd(), 'src'),
        '--paths', os.path.join(os.getcwd(), 'src', 'core'),
        '--paths', os.path.join(os.getcwd(), 'src', 'visualization'),
        '--paths', os.path.join(os.getcwd(), 'src', 'data'),
        '--paths', os.path.join(os.getcwd(), 'src', 'network'),
        '--paths', os.path.join(os.getcwd(), 'src', 'utils'),
        '--paths', os.path.join(os.getcwd(), 'src', 'ui'),
        '--name', 'HeatMapCAD_Single',
        *bin_option,  # Добавляем опцию бинарного файла, если нашли DLL
        # Явное указание скрытых зависимостей для корректной сборки
        '--hidden-import', 'matplotlib.backends.backend_tkagg',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'PIL.Image',
        '--hidden-import', 'core.mouse_tracker',
        '--hidden-import', 'visualization.heatmap_visualizer',
        '--hidden-import', 'data.data_manager',
        '--hidden-import', 'network.client',
        '--hidden-import', 'utils.config',
        '--hidden-import', 'utils.sound',
        '--hidden-import', 'ui.main_window',
        '--hidden-import', 'ui.first_launch_dialog',
        'src/main.py'  # Напрямую используем main.py как точку входа
    ]
    
    # Запускаем процесс сборки
    try:
        subprocess.run(pyinstaller_cmd, check=True)
        
        # Проверяем, что файл был создан
        if os.path.exists(output_file):
            print(f"Одиночный файл успешно создан: {output_file}")
            print(f"Размер файла: {os.path.getsize(output_file) / (1024*1024):.2f} МБ")
            return True
        else:
            print(f"Ошибка: файл {output_file} не был создан!")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при создании одиночного файла: {e}")
        return False

def main():
    """Основная функция для сборки исполняемого файла."""
    print("=== Сборка исполняемого файла HeatMapCAD ===")
    print(f"Текущий каталог: {os.getcwd()}")
    print(f"Версия Python: {sys.version}")
    
    # Шаг 1: Создание иконки
    create_icon()
    
    # Шаг 2: Очистка директорий сборки
    clean_build_directories()
    
    # Шаг 3: Сборка исполняемого файла в папке dist
    build_successful = build_executable()
    
    # Шаг 4: Создание одиночного файла
    if build_successful:
        single_file_successful = create_single_file_executable()
        if single_file_successful:
            dist_path = os.path.abspath('dist')
            print(f"\nИсполняемые файлы созданы в: {dist_path}")
            print("- HeatMapCAD/ - каталог с исполняемым файлом и зависимостями")
            print("- HeatMapCAD_Single.exe - одиночный исполняемый файл со всеми зависимостями")
    
    print("\nПроцесс сборки завершен")

if __name__ == "__main__":
    main() 