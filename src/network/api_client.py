import requests
import json
from typing import Dict, Any, Optional
from pathlib import Path


class APIClient:
    """Класс для взаимодействия с API сайта."""

    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url.rstrip('/')
        self.chunk_size = 1024 * 1024  # 1MB

    def upload_heatmap_data(self, file_path: str, callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Загрузить данные тепловой карты на сервер.
        
        Args:
            file_path: Путь к JSON файлу с данными
            callback: Функция обратного вызова для отображения прогресса (принимает значение от 0 до 100)
        
        Returns:
            Dict с ответом от сервера
        """
        file_size = Path(file_path).stat().st_size
        uploaded = 0

        with open(file_path, 'rb') as f:
            # Инициализация загрузки
            init_response = requests.post(
                f"{self.base_url}/api/heatmap/init",
                json={"filename": Path(file_path).name, "size": file_size}
            )
            init_response.raise_for_status()
            upload_id = init_response.json()['upload_id']

            # Загрузка чанками
            chunk_number = 0
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break

                response = requests.post(
                    f"{self.base_url}/api/heatmap/chunk",
                    files={
                        'chunk': (f'chunk_{chunk_number}', chunk),
                        'upload_id': (None, upload_id),
                        'chunk_number': (None, str(chunk_number))
                    }
                )
                response.raise_for_status()

                uploaded += len(chunk)
                if callback:
                    progress = int((uploaded / file_size) * 100)
                    callback(progress)

                chunk_number += 1

            # Завершение загрузки
            finish_response = requests.post(
                f"{self.base_url}/api/heatmap/finish",
                json={"upload_id": upload_id}
            )
            finish_response.raise_for_status()
            return finish_response.json()

    def get_heatmap_list(self) -> list:
        """Получить список всех тепловых карт на сервере."""
        response = requests.get(f"{self.base_url}/api/heatmap/list")
        response.raise_for_status()
        return response.json()

    def get_heatmap_data(self, heatmap_id: str) -> Dict[str, Any]:
        """Получить данные конкретной тепловой карты."""
        response = requests.get(f"{self.base_url}/api/heatmap/{heatmap_id}")
        response.raise_for_status()
        return response.json() 