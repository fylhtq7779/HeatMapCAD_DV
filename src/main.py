import tkinter as tk
import ttkbootstrap as ttkb
from typing import Optional
import os
import json

from core.mouse_tracker import MouseTracker
from visualization.heatmap_visualizer import HeatmapVisualizer
from data.data_manager import DataManager
from network.client import NetworkClient
from utils.config import Config
from utils.sound import play_start_sound, play_stop_sound
from ui.main_window import MainWindow
from ui.first_launch_dialog import FirstLaunchDialog


class Application:
    """Главный класс приложения."""

    def __init__(self):
        print("Инициализация приложения...")
        # Инициализация конфигурации
        self.config = Config()
        print("Конфигурация загружена")
        
        # Создание главного окна с темой
        print("Создание главного окна...")
        self.root = ttkb.Window(themename=self.config.get('ui.theme', 'darkly'))
        self.root.withdraw()  # Скрываем окно до получения данных пользователя
        
        # Проверяем первый запуск и получаем данные пользователя
        self.user_config_path = "config/user_config.json"
        print("Проверка первого запуска...")
        self.user_data = self._check_first_launch()
        if not self.user_data:
            print("Нет данных пользователя - завершение работы")
            self.root.destroy()
            return  # Пользователь закрыл диалог

        print("Данные пользователя получены")
        print(f"Пользователь: {self.user_data}")
        
        # Инициализация компонентов
        print("Инициализация компонентов...")
        self.data_manager = DataManager(
            storage_dir=self.config.get('storage.directory')
        )
        
        self.network_client = NetworkClient(
            config=self.config.get('network')
        )

        self.mouse_tracker = MouseTracker()
        self.visualizer = HeatmapVisualizer()

        # Настройка визуализатора
        self.visualizer.set_config(self.config.get('visualization'))
        
        # Инициализация UI с передачей данных пользователя
        print("Создание главного окна...")
        self.main_window = MainWindow(
            root=self.root,
            config=self.config,
            mouse_tracker=self.mouse_tracker,
            visualizer=self.visualizer,
            data_manager=self.data_manager,
            network_client=self.network_client,
            user_data=self.user_data
        )

        # Настройка обработчиков событий
        self._setup_event_handlers()
        print("Инициализация приложения завершена")
        
        # Показываем главное окно
        self.root.deiconify()

    def _check_first_launch(self) -> Optional[dict]:
        """Проверить первый запуск и получить данные пользователя."""
        try:
            print("Проверка наличия конфигурационного файла...")
            # Создаем конфигурацию по умолчанию, если файла нет
            if not os.path.exists(self.user_config_path):
                print("Создание конфигурационного файла по умолчанию...")
                default_config = {
                    "user": {
                        "fullname": "",
                        "group": "",
                        "selected_program": "Компас 3D"
                    },
                    "is_first_launch": True,
                    "available_programs": [
                        "Компас 3D"
                    ]
                }
                os.makedirs(os.path.dirname(self.user_config_path), exist_ok=True)
                with open(self.user_config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=4)

            # Загружаем конфигурацию
            print("Загрузка конфигурации...")
            with open(self.user_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Показываем диалог при первом запуске или если данные пользователя неполные
            user_data = config.get("user", {})
            if config.get('is_first_launch', True) or not user_data.get('fullname') or not user_data.get('group'):
                print("Открытие диалога первого запуска...")
                try:
                    # Создаем диалог
                    dialog = FirstLaunchDialog(None, self.user_config_path)
                    user_data = dialog.show()
                    
                    if not user_data:
                        print("Диалог был закрыт без ввода данных")
                        return None
                        
                except Exception as e:
                    print(f"Ошибка при создании диалога: {e}")
                    return None

            print(f"Данные пользователя загружены: {user_data}")
            return user_data

        except Exception as e:
            print(f"Ошибка при проверке первого запуска: {e}")
            return None

    def _setup_event_handlers(self) -> None:
        """Настройка обработчиков событий."""
        # Обработчики событий трекера
        self.mouse_tracker.add_listener(self._on_tracking_event)

        # Настройка закрытия приложения
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_tracking_event(self, event_type: str, data: dict) -> None:
        """Обработчик событий трекинга."""
        if event_type == "tracking_started":
            self.visualizer.set_background(self.mouse_tracker.current_screenshot)
            self.visualizer.update([])
            play_start_sound()
        elif event_type == "position_updated":
            pass
        elif event_type == "tracking_stopped":
            if self.mouse_tracker.tracking_data:
                # Обновляем визуализацию
                self.visualizer.update(self.mouse_tracker.tracking_data)
                self.main_window.update_visualization()
                
                # Добавляем информацию о пользователе к данным
                track_data = {
                    'user': self.user_data,
                    'tracking_data': self.mouse_tracker.tracking_data,
                    'screen_resolution': self.mouse_tracker.screen_resolution
                }
                
                # Сохраняем трек
                filename = self.data_manager.save_tracking_data(
                    track_data['tracking_data'],
                    track_data['screen_resolution']
                )
                
                # Обновляем список треков и выбираем последний
                self.main_window.update_track_list()
                if hasattr(self.main_window, 'track_combobox'):
                    self.main_window.track_combobox.set(filename)
                
                play_stop_sound()

                # Отправляем данные на сервер, если включена автозагрузка
                if self.config.get('network.auto_upload'):
                    self.network_client.upload_tracking_data(track_data)

    def _on_close(self) -> None:
        """Обработчик закрытия приложения."""
        self.mouse_tracker.stop_tracking()
        self.network_client.stop_auto_sync()
        self.root.destroy()

    def run(self) -> None:
        """Запуск приложения."""
        if not self.user_data:
            return  # Не запускаем приложение, если нет данных пользователя
            
        # Запуск автоматической синхронизации
        if self.config.get('network.auto_upload'):
            self.network_client.start_auto_sync()

        # Запуск главного цикла
        self.root.mainloop()


if __name__ == "__main__":
    app = Application()
    app.run() 