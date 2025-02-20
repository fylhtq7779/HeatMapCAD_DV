import json
import os
from typing import Dict, Any, Optional


class Config:
    """Класс для управления конфигурацией приложения."""

    DEFAULT_CONFIG = {
        'storage': {
            'directory': 'mouse_tracks',
            'max_files': 100
        },
        'visualization': {
            'resolution': 100,
            'brightness': 1.0,
            'size_factor': 1.0,
            'sensitivity': 1.0,
            'colormap': 'hot'
        },
        'tracking': {
            'min_movement': 1,  # минимальное перемещение мыши в пикселях
            'sample_rate': 60,  # частота сэмплирования в Гц
        },
        'network': {
            'server_url': '',
            'auto_upload': False,
            'sync_interval': 300  # интервал синхронизации в секундах
        },
        'updates': {
            'check_on_startup': True,
            'auto_update': False
        },
        'ui': {
            'theme': 'darkly',
            'window_size': (1200, 800),
            'min_window_size': (800, 600)
        }
    }

    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = config_path
        self.config = self.DEFAULT_CONFIG.copy()
        self._ensure_config_dir()
        self.load()

    def _ensure_config_dir(self) -> None:
        """Убедиться, что директория конфигурации существует."""
        config_dir = os.path.dirname(self.config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

    def load(self) -> None:
        """Загрузить конфигурацию из файла."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self._update_recursive(self.config, loaded_config)
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}")

    def save(self) -> None:
        """Сохранить конфигурацию в файл."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")

    def _update_recursive(self, base: Dict, update: Dict) -> None:
        """Рекурсивно обновить конфигурацию."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._update_recursive(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение конфигурации по ключу."""
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Установить значение конфигурации по ключу."""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save() 