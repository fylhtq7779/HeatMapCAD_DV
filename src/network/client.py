import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime
import threading
import time
import os


class NetworkClient:
    """Класс для сетевого взаимодействия."""

    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация клиента.
        
        Args:
            config: Конфигурация сетевого взаимодействия
        """
        self.config = config
        self.server_url = "https://fylhtq7779.github.io/HeatMapCAD_DV"  # URL нашего сайта
        self.data_path = 'data'  # Локальная директория для данных
        self.auto_upload = config.get('auto_upload', False)
        self.sync_interval = config.get('sync_interval', 300)
        self.sync_thread: Optional[threading.Thread] = None
        self.is_running = False

    def _datetime_to_str(self, obj: Any) -> str:
        """Преобразовать datetime в строку."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f'Object of type {type(obj)} is not JSON serializable')

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
            html_filename = f"heatmap_{timestamp}.html"
            
            # Добавляем информацию о пользователе в данные
            data['user'] = {
                'fullname': user_data.get('fullname', ''),
                'group': user_data.get('group', ''),
                'program': user_data.get('program', 'Компас 3D')
            }
            
            # Преобразуем данные в JSON с обработкой datetime
            json_data = json.dumps(data, ensure_ascii=False, indent=2, default=self._datetime_to_str)
            
            # Создаем HTML файл с данными
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Тепловая карта - {user_data.get('fullname', '')}</title>
                <script type="application/json" id="heatmap-data">
                {json_data}
                </script>
            </head>
            <body>
                <div id="heatmap-container"></div>
                <script>
                    // Данные будут доступны через document.getElementById('heatmap-data').textContent
                    console.log('HeatMap data loaded');
                </script>
            </body>
            </html>
            """
            
            # Создаем директории если их нет
            os.makedirs(self.data_path, exist_ok=True)
            os.makedirs(os.path.join(self.data_path, 'maps'), exist_ok=True)
            
            # Сохраняем JSON
            json_path = os.path.join(self.data_path, 'maps', json_filename)
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            # Сохраняем HTML
            html_path = os.path.join(self.data_path, 'maps', html_filename)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Обновляем index.json
            index_path = os.path.join(self.data_path, 'index.json')
            index_data = {"heatmaps": []}
            
            if os.path.exists(index_path):
                try:
                    with open(index_path, 'r', encoding='utf-8') as f:
                        index_data = json.load(f)
                except:
                    pass
            
            # Добавляем информацию о новой карте
            index_data['heatmaps'].append({
                'date': datetime.now().isoformat(),
                'user_fullname': user_data.get('fullname', ''),
                'user_group': user_data.get('group', ''),
                'program': user_data.get('program', 'Компас 3D'),
                'html_file': f"maps/{html_filename}",
                'json_file': f"maps/{json_filename}"
            })
            
            # Сохраняем обновленный index.json
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            return False

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

    def upload_tracking_data(self, data: Dict[str, Any]) -> bool:
        """Загрузить данные трекинга."""
        return self.save_locally(data, data.get('user', {})) 