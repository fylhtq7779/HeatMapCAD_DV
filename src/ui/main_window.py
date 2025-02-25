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
from network.api_client import APIClient
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
        self.api_client = APIClient(config.get('network.server_url'))

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
        self.upload_progress: Optional[ttkb.Progressbar] = None
        self.upload_label: Optional[ttkb.Label] = None

        # Добавляем переменные для debounce
        self._update_timer = None
        self._is_updating = False

        # Настройка окна
        window_size = self.config.get('ui.window_size')
        min_window_size = self.config.get('ui.min_window_size')
        
        self.root.title("Тепловая карта движений мыши")
        self.root.geometry(f"{window_size[0]}x{window_size[1]}")
        self.root.minsize(width=min_window_size[0], height=min_window_size[1])

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
        visualization_frame.pack_propagate(False)  # Запрещаем изменение размера фрейма
        visualization_frame.configure(width=400)  # Устанавливаем минимальную ширину

        # Создание области визуализации
        self.canvas = FigureCanvasTkAgg(self.visualizer.fig, master=visualization_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=1, padx=2, pady=2)

        # Создание панели настроек
        self.settings_frame = ttkb.Frame(self.main_frame, width=250, padding=10)
        self.settings_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.settings_frame.pack_propagate(False)  # Запрещаем изменение размера фрейма

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

        # Кнопка загрузки на сервер
        ttkb.Button(
            self.settings_frame,
            text="Загрузить на сервер",
            command=self.upload_to_server,
            bootstyle='info',
            padding=10,
            takefocus=0
        ).pack(anchor=tk.S, fill=tk.X, pady=5)

        # Прогресс-бар загрузки
        self.upload_label = ttkb.Label(
            self.settings_frame,
            text="",
            font=("Segoe UI", 9)
        )
        self.upload_label.pack(anchor=tk.S, fill=tk.X, pady=(5, 0))

        self.upload_progress = ttkb.Progressbar(
            self.settings_frame,
            mode='determinate',
            bootstyle='info'
        )
        self.upload_progress.pack(anchor=tk.S, fill=tk.X, pady=(0, 20))
        self.upload_progress.pack_forget()  # Скрываем до начала загрузки

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

    def upload_to_server(self) -> None:
        """Загрузить текущий трек на сервер."""
        if not self.track_combobox or not self.track_combobox.get():
            messagebox.showwarning(
                "Предупреждение",
                "Сначала выберите трек для загрузки"
            )
            return

        selected_file = self.track_combobox.get()
        file_path = os.path.join(self.data_manager.storage_dir, selected_file)

        def update_progress(progress: int) -> None:
            """Обновить прогресс-бар."""
            self.upload_label.configure(text=f"Загрузка: {progress}%")
            self.upload_progress['value'] = progress
            if progress >= 100:
                self.upload_progress.pack_forget()
                self.upload_label.configure(text="Загрузка завершена")
                self.root.after(2000, lambda: self.upload_label.configure(text=""))

        try:
            # Показываем прогресс-бар
            self.upload_progress['value'] = 0
            self.upload_progress.pack(anchor=tk.S, fill=tk.X, pady=(0, 20))
            self.upload_label.configure(text="Подготовка к загрузке...")

            # Загружаем файл
            response = self.api_client.upload_heatmap_data(file_path, update_progress)
            
            messagebox.showinfo(
                "Успех",
                f"Данные успешно загружены на сервер\nID: {response.get('id', 'unknown')}"
            )

        except Exception as e:
            self.upload_progress.pack_forget()
            self.upload_label.configure(text="")
            messagebox.showerror(
                "Ошибка",
                f"Не удалось загрузить данные на сервер: {str(e)}"
            ) 