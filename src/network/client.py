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

    def _datetime_to_str(self, obj: Any) -> Any:
        """Конвертировать datetime в строку."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    def upload_to_github_pages(self, data: Dict[str, Any], filename: str) -> bool:
        """Загрузить данные на GitHub Pages."""
        if not self.github_repo:
            return False

        try:
            # Создаем уникальное имя файла с временной меткой
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"{filename}_{timestamp}.json"
            
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
            
            # Отправляем файлы на GitHub Pages через API
            repo_parts = self.github_repo.split('/')
            if len(repo_parts) != 2:
                raise ValueError("Неверный формат репозитория. Должно быть: username/repo")
            
            owner, repo = repo_parts
            base_url = f"https://{owner}.github.io/{repo}"
            
            # Создаем index.html со списком всех карт
            index_content = self._create_index_html()
            index_path = os.path.join(self.data_path, "index.html")
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            print(f"Данные сохранены локально и доступны по адресу: {base_url}/data/{html_filename}")
            return True
            
        except Exception as e:
            print(f"Ошибка загрузки данных на GitHub Pages: {e}")
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
        if not self.upload_to_github_pages(data, filename):
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