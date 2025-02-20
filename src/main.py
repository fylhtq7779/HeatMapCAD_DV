import tkinter as tk
import ttkbootstrap as ttkb
from typing import Optional
import os

from core.mouse_tracker import MouseTracker
from visualization.heatmap_visualizer import HeatmapVisualizer
from data.data_manager import DataManager
from network.client import NetworkClient
from utils.config import Config
from utils.sound import play_start_sound, play_stop_sound
from ui.main_window import MainWindow


class Application:
    """Главный класс приложения."""

    def __init__(self):
        # Инициализация конфигурации
        self.config = Config()

        # Инициализация компонентов
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

        # Создание главного окна
        self.root = ttkb.Window(
            themename=self.config.get('ui.theme')
        )
        
        # Инициализация UI
        self.main_window = MainWindow(
            root=self.root,
            config=self.config,
            mouse_tracker=self.mouse_tracker,
            visualizer=self.visualizer,
            data_manager=self.data_manager,
            network_client=self.network_client
        )

        # Настройка обработчиков событий
        self._setup_event_handlers()

        # Проверка обновлений при запуске
        if self.config.get('updates.check_on_startup'):
            self._check_updates()

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
            # Очищаем предыдущую визуализацию
            self.visualizer.update([])
            # Воспроизводим звук начала отслеживания
            play_start_sound()
        elif event_type == "position_updated":
            # Только собираем данные, не обновляем визуализацию
            pass
        elif event_type == "tracking_stopped":
            # Сохраняем данные
            if self.mouse_tracker.tracking_data:
                # Обновляем визуализацию
                self.visualizer.update(self.mouse_tracker.tracking_data)
                self.main_window.update_visualization()
                
                # Сохраняем трек
                filename = self.data_manager.save_tracking_data(
                    self.mouse_tracker.tracking_data,
                    self.mouse_tracker.screen_resolution
                )
                
                # Обновляем список треков и выбираем последний
                self.main_window.update_track_list()
                self.main_window.track_combobox.set(os.path.basename(filename))
                
                # Воспроизводим звук завершения отслеживания
                play_stop_sound()

                # Отправляем данные на сервер, если включена автозагрузка
                if self.config.get('network.auto_upload'):
                    data = self.data_manager.load_tracking_data(filename)
                    self.network_client.upload_tracking_data(data)

    def _check_updates(self) -> None:
        """Проверка обновлений."""
        update_info = self.network_client.check_for_updates()
        if update_info and self.config.get('updates.auto_update'):
            self.network_client.download_update(update_info['version'])
            # TODO: Реализовать установку обновления

    def _on_close(self) -> None:
        """Обработчик закрытия приложения."""
        self.mouse_tracker.stop_tracking()
        self.network_client.stop_auto_sync()
        self.root.destroy()

    def run(self) -> None:
        """Запуск приложения."""
        # Запуск автоматической синхронизации
        if self.config.get('network.auto_upload'):
            self.network_client.start_auto_sync()

        # Запуск главного цикла
        self.root.mainloop()


if __name__ == "__main__":
    app = Application()
    app.run() 