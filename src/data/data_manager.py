import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np


class DataManager:
    """Класс для управления данными трекинга."""

    def __init__(self, storage_dir: str = "mouse_tracks"):
        self.storage_dir = storage_dir
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        """Убедиться, что директория для хранения существует."""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def _get_full_path(self, filename: str) -> str:
        """Получить полный путь к файлу."""
        # Если путь уже содержит storage_dir, возвращаем как есть
        if os.path.dirname(filename) == self.storage_dir:
            return filename
        # Иначе добавляем storage_dir
        return os.path.join(self.storage_dir, filename)

    def save_tracking_data(self, data: List[tuple], resolution: tuple) -> str:
        """Сохранить данные трекинга в файл."""
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"track_{current_time}.json"
        filepath = self._get_full_path(filename)

        # Преобразуем datetime объекты в строки
        formatted_data = [
            (x, y, t.isoformat()) for x, y, t in data
        ]

        track_data = {
            'resolution': {
                'width': resolution[0],
                'height': resolution[1]
            },
            'positions': formatted_data,
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'points_count': len(data)
            }
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(track_data, f, ensure_ascii=False, indent=2)

        return filename  # Возвращаем только имя файла без пути

    def load_tracking_data(self, filename: str) -> Dict[str, Any]:
        """Загрузить данные трекинга из файла."""
        filepath = self._get_full_path(filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Файл {filepath} не найден")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Преобразуем строки обратно в datetime
        data['positions'] = [
            (x, y, datetime.fromisoformat(t)) for x, y, t in data['positions']
        ]

        return data

    def list_tracking_files(self) -> List[str]:
        """Получить список всех файлов с данными трекинга."""
        return [
            f for f in os.listdir(self.storage_dir)
            if f.endswith('.json')
        ]

    def delete_tracking_file(self, filename: str) -> None:
        """Удалить файл с данными трекинга."""
        filepath = self._get_full_path(filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    def get_tracking_metadata(self, filename: str) -> Dict[str, Any]:
        """Получить метаданные файла трекинга."""
        data = self.load_tracking_data(filename)
        return data.get('metadata', {}) 