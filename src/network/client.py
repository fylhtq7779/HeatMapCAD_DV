import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime
import threading
import time
import os
from .api_client import APIClient


class NetworkClient:
    """Класс для сетевого взаимодействия."""

    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация клиента.
        
        Args:
            config: Конфигурация сетевого взаимодействия
        """
        self.config = config
        self.data_path = 'data'  # Локальная директория для данных
        self.auto_upload = config.get('auto_upload', False)
        self.sync_interval = config.get('sync_interval', 300)
        self.sync_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.api_client = APIClient()
        self.start_time = datetime.now()

    def _datetime_to_str(self, obj: Any) -> str:
        """Преобразовать datetime в строку."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f'Object of type {type(obj)} is not JSON serializable')

    def _calculate_session_duration(self) -> str:
        """Вычислить длительность сессии."""
        duration = datetime.now() - self.start_time
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        return f"{hours}h {minutes}m"

    def save_locally(self, data: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
        """
        Сохранить данные локально.
        
        Args:
            data: Данные для сохранения
            user_data: Информация о пользователе
        """
        try:
            # Создаем уникальное имя файла с временной меткой
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"heatmap_{timestamp}.json"
            
            # Создаем структуру данных
            heatmap_data = {
                "metadata": {
                    "fio": user_data.get('fullname', ''),
                    "group": user_data.get('group', ''),
                    "program": user_data.get('selected_program', user_data.get('program', 'AutoCAD')),
                    "timestamp": datetime.now().isoformat(),
                    "session_duration": self._calculate_session_duration(),
                    "version": "1.0"
                },
                "tracking_data": {
                    "resolution": data.get('resolution', {'width': 1920, 'height': 1080}),
                    "movements": data.get('movements', []),
                    "clicks": data.get('clicks', [])
                }
            }
            
            # Создаем директории если их нет
            os.makedirs(self.data_path, exist_ok=True)
            os.makedirs(os.path.join(self.data_path, 'maps'), exist_ok=True)
            
            # Сохраняем JSON
            json_path = os.path.join(self.data_path, 'maps', json_filename)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(heatmap_data, f, ensure_ascii=False, indent=2, default=self._datetime_to_str)
            
            return True
            
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            return False

    def upload_tracking_data(self, data: Dict[str, Any]) -> bool:
        """
        Загрузить данные трекинга.
        
        Args:
            data: Данные для загрузки
            
        Returns:
            bool: True если загрузка успешна, False в противном случае
        """
        print("\nПроверка данных в NetworkClient:")
        
        # Проверяем формат данных
        movements = []
        if 'tracking_data' in data and isinstance(data['tracking_data'], list):
            # Данные в формате [x, y, timestamp]
            movements = [
                {"x": pos[0], "y": pos[1], "timestamp": pos[2], "event_type": "move"}
                for pos in data['tracking_data']
            ]
            print(f"Найдено {len(movements)} движений мыши в формате tracking_data")
        elif 'movements' in data and isinstance(data['movements'], list):
            # Данные уже в нужном формате
            movements = data['movements']
            print(f"Найдено {len(movements)} движений мыши в формате movements")
        
        # Обновляем данные
        data['movements'] = movements
        data['clicks'] = data.get('clicks', [])
        
        print("Movements:", len(data.get('movements', [])))
        print("Clicks:", len(data.get('clicks', [])))
        print("Sample movement:", data.get('movements', [])[:1])
        print("Sample click:", data.get('clicks', [])[:1])
        
        user_data = data.get('user', {})
        
        # Добавляем длительность сессии и обновляем данные
        data['session_duration'] = self._calculate_session_duration()
        
        # Сначала сохраняем локально
        if not self.save_locally(data, user_data):
            print("Ошибка при локальном сохранении данных")
            return False
            
        # Затем отправляем на сервер
        return self.api_client.send_heatmap_data(data, user_data)

    def start_auto_sync(self) -> None:
        """Запустить автоматическую синхронизацию."""
        if self.auto_upload and not self.is_running:
            self.is_running = True
            self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
            self.sync_thread.start()

    def stop_auto_sync(self) -> None:
        """Остановить автоматическую синхронизацию."""
        self.is_running = False
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=1.0)

    def _sync_loop(self) -> None:
        """Цикл автоматической синхронизации."""
        while self.is_running:
            try:
                # В этой версии нет необходимости в синхронизации
                time.sleep(self.sync_interval)
            except Exception as e:
                print(f"Ошибка синхронизации: {e}") 