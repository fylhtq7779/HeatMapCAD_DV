import os
import sys
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis

block_cipher = None

# Полный путь к текущему каталогу
root_path = os.getcwd()

# Поиск Python DLL
def find_python_dll():
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
    
    return None

python_dll_path = find_python_dll()
binaries = []

if python_dll_path:
    print(f"Найден Python DLL: {python_dll_path}")
    binaries.append((python_dll_path, '.'))

# Содержимое, которое нужно включить в сборку
datas = [
    ('config', 'config'),              # Конфигурационные файлы
    ('src', '.'),                      # Исходный код (ставим в корень для корректной работы импортов)
    ('LICENSE.txt', '.'),              # Лицензия
    ('USER_GUIDE.txt', '.'),           # Руководство пользователя
    ('assets', 'assets')               # Ресурсы приложения
]

# Создаем анализ зависимостей
a = Analysis(
    ['src/main.py'],                   # Напрямую используем main.py как точку входа
    pathex=[root_path, 
           os.path.join(root_path, 'src'),
           os.path.join(root_path, 'src/core'),
           os.path.join(root_path, 'src/visualization'),
           os.path.join(root_path, 'src/data'),
           os.path.join(root_path, 'src/network'),
           os.path.join(root_path, 'src/utils'),
           os.path.join(root_path, 'src/ui')
    ],  # Добавляем пути для разрешения модулей
    binaries=binaries,                 # Явное добавление DLL
    datas=datas,
    hiddenimports=[
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'numpy',
        'pynput',
        'ttkbootstrap',
        'PIL',
        'PIL.Image',
        'PIL._tkinter_finder',
        'scipy',
        'pyautogui',
        'tkinter',
        'tkinter.ttk',
        'pkg_resources.py2_warn',
        'core.mouse_tracker',
        'visualization.heatmap_visualizer',
        'data.data_manager',
        'network.client',
        'utils.config',
        'utils.sound',
        'ui.main_window',
        'ui.first_launch_dialog'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Создаем PYZ архив
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Путь к иконке
icon_path = os.path.join(root_path, 'assets', 'icon.ico')
if not os.path.exists(icon_path):
    icon_path = None

# Создаем исполняемый файл
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HeatMapCAD',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Используем консоль для отладки, потом можно будет изменить на False
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)

# Собираем все файлы в папку
collect = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HeatMapCAD',
) 