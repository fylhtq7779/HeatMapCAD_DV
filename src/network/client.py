import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime
import threading
import time
import base64
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
        self.server_url = config.get('server_url', '')
        self.auto_upload = config.get('auto_upload', False)
        self.sync_interval = config.get('sync_interval', 300)
        self.sync_thread: Optional[threading.Thread] = None
        self.is_running = False
        
        # GitHub Pages configuration
        github_config = config.get('github', {})
        self.github_repo = github_config.get('repo', '')
        self.github_branch = github_config.get('branch', 'gh-pages')
        self.data_path = github_config.get('data_directory', 'data')

    def _datetime_to_str(self, obj: Any) -> str:
        """Преобразовать datetime в строку."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f'Object of type {type(obj)} is not JSON serializable')

    def upload_to_github_pages(self, data: Dict[str, Any], filename: str, user_data: Dict[str, Any]) -> bool:
        """
        Загрузить данные на GitHub Pages.
        
        Args:
            data: Данные для загрузки
            filename: Имя файла
            user_data: Информация о пользователе
        """
        if not self.github_repo:
            return False

        try:
            # Создаем уникальное имя файла с временной меткой
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"{filename}_{timestamp}.json"
            
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
                <title>HeatMap Data</title>
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
            
            # Сохраняем файлы локально в папке data
            os.makedirs(self.data_path, exist_ok=True)
            
            # Сохраняем JSON
            json_path = os.path.join(self.data_path, json_filename)
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            # Сохраняем HTML
            html_filename = f"{filename}_{timestamp}.html"
            html_path = os.path.join(self.data_path, html_filename)
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
                'html_file': html_filename,
                'json_file': json_filename
            })
            
            # Сохраняем обновленный index.json
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Ошибка при загрузке на GitHub Pages: {e}")
            return False

    def _create_index_html(self) -> str:
        """Создать index.html со списком всех карт."""
        files = [f for f in os.listdir(self.data_path) if f.endswith('.html') and f != 'index.html']
        files.sort(reverse=True)  # Сортируем по убыванию (новые файлы сверху)
        
        links = '\n'.join([
            f'<li><a href="{f}">{f}</a></li>'
            for f in files
        ])
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>HeatMap Data List</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    color: #333;
                }}
                ul {{
                    list-style: none;
                    padding: 0;
                }}
                li {{
                    margin: 10px 0;
                    padding: 10px;
                    background: #f5f5f5;
                    border-radius: 4px;
                }}
                a {{
                    color: #0366d6;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <h1>Список тепловых карт</h1>
            <ul>
                {links}
            </ul>
        </body>
        </html>
        """

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
                # В новой версии нет необходимости в постоянной синхронизации
                time.sleep(self.sync_interval)
            except Exception as e:
                print(f"Ошибка синхронизации: {e}")

    def upload_tracking_data(self, data: Dict[str, Any]) -> bool:
        """Загрузить данные трекинга."""
        success = True
        
        # Загружаем на GitHub Pages
        filename = f"heatmap"
        if not self.upload_to_github_pages(data, filename, data['user']):
            success = False
            print("Ошибка загрузки на GitHub Pages")
        
        # Если настроен server_url, загружаем и туда
        if self.server_url:
            try:
                response = requests.post(
                    f"{self.server_url}/upload_tracking_data",
                    json=data
                )
                if response.status_code != 200:
                    success = False
                    print(f"Ошибка загрузки на сервер: {response.status_code}")
            except Exception as e:
                success = False
                print(f"Ошибка загрузки данных на сервер: {e}")
        
        return success 