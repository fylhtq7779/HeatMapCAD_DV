"""
Скрипт для запуска приложения HeatMapCAD.
"""

import os
import sys

# Добавляем путь к исходному коду в PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

if __name__ == "__main__":
    try:
        from src.main import Application
        app = Application()
        app.run()
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        import traceback
        traceback.print_exc() 