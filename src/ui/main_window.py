import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttkb
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Any, Dict, Optional
import os

from core.mouse_tracker import MouseTracker
from visualization.heatmap_visualizer import HeatmapVisualizer
from data.data_manager import DataManager
from network.client import NetworkClient
from utils.config import Config
from utils.sound import play_start_sound


class MainWindow:
    """Класс главного окна приложения."""

    def __init__(
        self,
        root: ttkb.Window,
        config: Config,
        mouse_tracker: MouseTracker,
        visualizer: HeatmapVisualizer,
        data_manager: DataManager,
        network_client: NetworkClient
    ):
        # Сохраняем ссылки на объекты
        self.root = root
        self.config = config
        self.mouse_tracker = mouse_tracker
        self.visualizer = visualizer
        self.data_manager = data_manager
        self.network_client = network_client

        # Настройка главного окна
        window_size = self.config.get('ui.window_size', [1200, 800])
        min_window_size = self.config.get('ui.min_window_size', [800, 600])
        self.root.geometry(f"{window_size[0]}x{window_size[1]}")
        self.root.minsize(min_window_size[0], min_window_size[1])
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Инициализация UI компонентов
        self.main_frame: Optional[ttkb.Frame] = None
        self.settings_frame: Optional[ttkb.Frame] = None
        self.canvas: Optional[FigureCanvasTkAgg] = None
        self.canvas_widget: Optional[tk.Widget] = None
        self.track_combobox: Optional[ttkb.Combobox] = None
        self.slider_resolution: Optional[ttkb.Scale] = None
        self.slider_brightness: Optional[ttkb.Scale] = None
        self.slider_size: Optional[ttkb.Scale] = None
        self.slider_sensitivity: Optional[ttkb.Scale] = None
        self.cmap_combobox: Optional[ttkb.Combobox] = None

        # Добавляем переменные для debounce
        self._update_timer = None
        self._is_updating = False

        # Настройка окна
        self.root.title("Тепловая карта движений мыши")

        # Создание UI
        self.create_ui()

    def create_ui(self) -> None:
        """Создание пользовательского интерфейса."""
        # Создание основного фрейма
        self.main_frame = ttkb.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        # Создание фрейма для области визуализации с фоном
        visualization_frame = ttkb.Frame(self.main_frame, bootstyle="secondary")
        visualization_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, padx=10, pady=10)

        # Создание области визуализации
        self.canvas = FigureCanvasTkAgg(self.visualizer.fig, master=visualization_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=1, padx=2, pady=2)

        # Создание панели настроек
        self.settings_frame = ttkb.Frame(self.main_frame, width=300)
        self.settings_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.settings_frame.pack_propagate(False)  # Запрещаем изменение размера

        # Создание элементов управления
        self.create_control_buttons()
        self.create_track_selector()
        self.create_visualization_controls()
        self.create_save_button()

        # Обновление списка треков
        self.update_track_list()

    def create_control_buttons(self) -> None:
        """Создание кнопок управления."""
        button_style = {'bootstyle': 'success', 'padding': 10, 'takefocus': 0}

        ttkb.Button(
            self.settings_frame,
            text="Начать отслеживание",
            command=self.start_tracking,
            **button_style
        ).pack(anchor=tk.N, fill=tk.X, pady=10)

        ttkb.Button(
            self.settings_frame,
            text="Завершить отслеживание",
            command=self.stop_tracking,
            bootstyle='danger',
            padding=10,
            takefocus=0
        ).pack(anchor=tk.N, fill=tk.X, pady=10)

    def create_track_selector(self) -> None:
        """Создание селектора треков."""
        ttkb.Label(
            self.settings_frame,
            text="Выберите маршрут",
            font=("Segoe UI", 10)
        ).pack(anchor=tk.N)

        self.track_combobox = ttkb.Combobox(
            self.settings_frame,
            state='readonly',
            takefocus=0
        )
        self.track_combobox.pack(anchor=tk.N, fill=tk.X, pady=10)
        self.track_combobox.bind("<<ComboboxSelected>>", self.load_selected_track)

    def create_visualization_controls(self) -> None:
        """Создание элементов управления визуализацией."""
        slider_style = {'bootstyle': 'info', 'orient': tk.HORIZONTAL, 'takefocus': 0}

        # Цветовая карта (создаем первым)
        ttkb.Label(self.settings_frame, text="Цветовая карта", font=("Segoe UI", 10)).pack(anchor=tk.N)
        self.cmap_combobox = ttkb.Combobox(
            self.settings_frame,
            values=['hot', 'cool', 'viridis', 'plasma', 'inferno', 'magma', 'cividis'],
            state='readonly',
            takefocus=0
        )
        self.cmap_combobox.set(self.config.get('visualization.colormap'))
        self.cmap_combobox.pack(anchor=tk.N, fill=tk.X, pady=10)

        # Разрешение
        ttkb.Label(self.settings_frame, text="Разрешение", font=("Segoe UI", 10)).pack(anchor=tk.N)
        self.slider_resolution = ttkb.Scale(
            self.settings_frame,
            from_=10,
            to=500,
            **slider_style
        )
        self.slider_resolution.set(self.config.get('visualization.resolution'))
        self.slider_resolution.pack(anchor=tk.N, fill=tk.X, pady=10)

        # Яркость
        ttkb.Label(self.settings_frame, text="Яркость", font=("Segoe UI", 10)).pack(anchor=tk.N)
        self.slider_brightness = ttkb.Scale(
            self.settings_frame,
            from_=0.1,
            to=3.0,
            **slider_style
        )
        self.slider_brightness.set(self.config.get('visualization.brightness'))
        self.slider_brightness.pack(anchor=tk.N, fill=tk.X, pady=10)

        # Размер
        ttkb.Label(self.settings_frame, text="Размер", font=("Segoe UI", 10)).pack(anchor=tk.N)
        self.slider_size = ttkb.Scale(
            self.settings_frame,
            from_=0.1,
            to=3.0,
            **slider_style
        )
        self.slider_size.set(self.config.get('visualization.size_factor'))
        self.slider_size.pack(anchor=tk.N, fill=tk.X, pady=10)

        # Чувствительность
        ttkb.Label(self.settings_frame, text="Чувствительность", font=("Segoe UI", 10)).pack(anchor=tk.N)
        self.slider_sensitivity = ttkb.Scale(
            self.settings_frame,
            from_=0.1,
            to=5.0,
            **slider_style
        )
        self.slider_sensitivity.set(self.config.get('visualization.sensitivity'))
        self.slider_sensitivity.pack(anchor=tk.N, fill=tk.X, pady=10)

        # Привязываем обработчики событий
        self.cmap_combobox.bind("<<ComboboxSelected>>", lambda _: self._schedule_update())
        self.slider_resolution.configure(command=lambda _: self._schedule_update())
        self.slider_brightness.configure(command=lambda _: self._schedule_update())
        self.slider_size.configure(command=lambda _: self._schedule_update())
        self.slider_sensitivity.configure(command=lambda _: self._schedule_update())

    def create_save_button(self) -> None:
        """Создание кнопок сохранения и загрузки."""
        button_style = {'bootstyle': 'primary', 'padding': 10, 'takefocus': 0}

        # Кнопка сохранения тепловой карты
        ttkb.Button(
            self.settings_frame,
            text="Сохранить тепловую карту",
            command=self.save_heatmap,
            **button_style
        ).pack(anchor=tk.S, fill=tk.X, pady=(20, 5))

        # Кнопка загрузки на GitHub Pages
        if self.config.get('network.github.token'):
            ttkb.Button(
                self.settings_frame,
                text="Опубликовать на сайте",
                command=self.upload_to_github,
                bootstyle='info',
                padding=10,
                takefocus=0
            ).pack(anchor=tk.S, fill=tk.X, pady=5)

    def start_tracking(self) -> None:
        """Начать отслеживание мыши."""
        delay_seconds = 5
        messagebox.showinfo(
            "Информация",
            f"У вас есть {delay_seconds} секунд, чтобы свернуть окна и подготовить экран для скриншота..."
        )
        # Запускаем отслеживание с задержкой и звуком
        self.root.after(delay_seconds * 1000, lambda: [play_start_sound(), self.mouse_tracker.start_tracking()])

    def stop_tracking(self) -> None:
        """Остановить отслеживание мыши."""
        self.mouse_tracker.stop_tracking()

    def update_track_list(self) -> None:
        """Обновить список доступных треков."""
        if self.track_combobox is not None:
            files = self.data_manager.list_tracking_files()
            self.track_combobox['values'] = files

    def load_selected_track(self, event: Any) -> None:
        """Загрузить выбранный трек."""
        if self.track_combobox is None:
            return

        selected_file = self.track_combobox.get()
        if selected_file:
            try:
                data = self.data_manager.load_tracking_data(selected_file)
                self.visualizer.update(data['positions'])
                self.update_visualization()
                messagebox.showinfo(
                    "Информация",
                    f"Выбранный маршрут загружен: {selected_file}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Ошибка",
                    f"Не удалось загрузить трек: {e}"
                )

    def _schedule_update(self) -> None:
        """Запланировать обновление визуализации с задержкой."""
        if self._update_timer is not None:
            self.root.after_cancel(self._update_timer)
        
        if not self._is_updating:
            self._update_timer = self.root.after(50, self._update_visualization_debounced)

    def _update_visualization_debounced(self) -> None:
        """Обновить визуализацию с защитой от частых обновлений."""
        self._is_updating = True
        self._update_timer = None
        
        try:
            self.update_visualization_settings()
        finally:
            self._is_updating = False

    def update_visualization_settings(self) -> None:
        """Обновить настройки визуализации."""
        if any(x is None for x in [
            self.slider_resolution,
            self.slider_brightness,
            self.slider_size,
            self.slider_sensitivity,
            self.cmap_combobox
        ]):
            return

        config = {
            'resolution': int(float(self.slider_resolution.get())),
            'brightness': self.slider_brightness.get(),
            'size_factor': self.slider_size.get(),
            'sensitivity': self.slider_sensitivity.get(),
            'colormap': self.cmap_combobox.get()
        }
        
        self.visualizer.set_config(config)
        self.update_visualization()

        # Сохраняем настройки в конфигурацию
        for key, value in config.items():
            self.config.set(f'visualization.{key}', value)

    def update_visualization(self) -> None:
        """Обновить визуализацию."""
        if self.canvas is not None:
            self.visualizer.render()
            self.canvas.draw()
            self.canvas.flush_events()

    def save_heatmap(self) -> None:
        """Сохранить тепловую карту."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filepath:
            try:
                self.visualizer.export(filepath)
                messagebox.showinfo(
                    "Информация",
                    f"Тепловая карта сохранена в: {filepath}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Ошибка",
                    f"Не удалось сохранить тепловую карту: {e}"
                )

    def upload_to_github(self) -> None:
        """Загрузить текущий трек на GitHub Pages."""
        if not self.track_combobox or not self.track_combobox.get():
            messagebox.showwarning(
                "Предупреждение",
                "Сначала выберите трек для загрузки"
            )
            return

        selected_file = self.track_combobox.get()
        file_path = os.path.join(self.data_manager.storage_dir, selected_file)

        try:
            from network.github_client import GitHubClient
            
            client = GitHubClient(
                token=self.config.get('network.github.token'),
                repo_name=self.config.get('network.github.repo')
            )
            
            metadata = client.upload_heatmap(file_path)
            url = client.get_heatmap_url(metadata['id'])
            
            messagebox.showinfo(
                "Успех",
                f"Тепловая карта опубликована!\nID: {metadata['id']}\nURL: {url}"
            )

        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось загрузить данные: {str(e)}"
            )

    def _on_close(self) -> None:
        """Обработчик закрытия окна."""
        try:
            # Останавливаем отслеживание
            if self.mouse_tracker:
                self.mouse_tracker.stop_tracking()
            
            # Останавливаем синхронизацию
            if self.network_client:
                self.network_client.stop_auto_sync()
            
            # Сохраняем текущие настройки
            if self.config:
                self.config.save()
            
            # Закрываем окно
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Ошибка при закрытии приложения: {e}")
            self.root.destroy() 