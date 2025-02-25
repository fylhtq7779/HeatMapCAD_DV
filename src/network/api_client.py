import requests
from typing import Dict, Any
import json
from datetime import datetime
import os


class APIClient:
    """Класс для отправки данных на API сервер."""
    
    def __init__(self):
        """Инициализация клиента."""
        self.api_url = "https://packsandmods.ru/heatmap/api/heatmap/upload"

    def _datetime_to_str(self, obj: Any) -> str:
        """Преобразовать datetime в строку."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f'Object of type {type(obj)} is not JSON serializable')

    def send_heatmap_data(self, data: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
        """
        Отправить данные тепловой карты на сервер.
        
        Args:
            data: Данные тепловой карты
            user_data: Информация о пользователе
            
        Returns:
            bool: True если отправка успешна, False в противном случае
        """
        try:
            print("\nПроверка входящих данных:")
            print("Movements:", len(data.get('movements', [])))
            print("Clicks:", len(data.get('clicks', [])))
            print("Sample movement:", data.get('movements', [])[:1])
            print("Sample click:", data.get('clicks', [])[:1])
            
            # Получаем разрешение экрана
            resolution = data.get('screen_resolution', data.get('resolution', {'width': 1920, 'height': 1080}))
            if isinstance(resolution, tuple) and len(resolution) == 2:
                resolution = {'width': resolution[0], 'height': resolution[1]}
            
            # Создаем структуру данных для JSON файла
            heatmap_data = {
                "metadata": {
                    "fio": user_data.get('fullname', ''),
                    "group": user_data.get('group', ''),
                    "program": user_data.get('selected_program', user_data.get('program', 'AutoCAD')),
                    "timestamp": datetime.now().isoformat(),
                    "session_duration": data.get('session_duration', ''),
                    "version": "1.0"
                },
                "tracking_data": {
                    "resolution": resolution,
                    "movements": data.get('movements', []),
                    "clicks": data.get('clicks', [])
                }
            }

            print("\nПроверка подготовленных данных:")
            print("Movements in heatmap_data:", len(heatmap_data['tracking_data']['movements']))
            print("Clicks in heatmap_data:", len(heatmap_data['tracking_data']['clicks']))

            # Создаем временный файл для отправки
            temp_file_path = os.path.join('data', 'temp_heatmap.json')
            os.makedirs('data', exist_ok=True)

            # Сохраняем данные во временный файл
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                json.dump(heatmap_data, f, ensure_ascii=False, indent=2, default=self._datetime_to_str)

            # Проверяем содержимое файла перед отправкой
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                file_content = json.load(f)
                print("\nПроверка данных в файле:")
                print("Movements in file:", len(file_content['tracking_data']['movements']))
                print("Clicks in file:", len(file_content['tracking_data']['clicks']))

            # Отправляем файл
            with open(temp_file_path, 'rb') as f:
                files = {
                    'file': ('data.json', f, 'application/json')
                }
                response = requests.post(self.api_url, files=files)

            # Удаляем временный файл
            try:
                os.remove(temp_file_path)
            except:
                pass

            # Проверка статуса ответа
            if response.status_code == 200:
                print("Данные успешно отправлены на сервер")
                return True
            else:
                print(f"Ошибка при отправке данных: {response.status_code}")
                if response.text:
                    print(f"Ответ сервера: {response.text}")
                return False
                
        except Exception as e:
            print(f"Ошибка при отправке данных: {str(e)}")
            return False 