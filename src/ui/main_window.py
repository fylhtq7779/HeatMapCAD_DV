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
        network_client: NetworkClient,
        user_data: Dict[str, Any]
    ):
        # Сохраняем ссылки на объекты
        self.root = root
        self.config = config
        self.mouse_tracker = mouse_tracker
        self.visualizer = visualizer
        self.data_manager = data_manager
        self.network_client = network_client
        self.user_data = user_data

        # Настройка главного окна
        window_size = self.config.get('ui.window_size', [1800, 950])  # Значительно увеличиваем размер окна
        min_window_size = self.config.get('ui.min_window_size', [1600, 800])  # Увеличиваем минимальный размер
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
        self.tracking_button: Optional[ttkb.Button] = None  # Добавляем переменную для кнопки отслеживания
        self.is_tracking: bool = False  # Добавляем флаг для отслеживания состояния

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
        
        # Создаем фрейм с фиксированной шириной для правой панели
        right_panel_width = 300  # Устанавливаем ширину 300 пикселей
        self.settings_frame = ttkb.Frame(self.main_frame, width=right_panel_width)
        self.settings_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        # Важно: устанавливаем фиксированную ширину и запрещаем изменение размера
        self.settings_frame.pack_propagate(False)
        
        # Создание фрейма для области визуализации с фоном
        # Размещаем его после правой панели, чтобы он занимал оставшееся пространство
        visualization_frame = ttkb.Frame(self.main_frame, bootstyle="secondary")
        visualization_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, padx=10, pady=10)

        # Создание области визуализации
        self.canvas = FigureCanvasTkAgg(self.visualizer.fig, master=visualization_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=1, padx=2, pady=2)
        
        # Добавляем обработчик изменения размера окна
        self.root.bind("<Configure>", self._on_window_resize)

        # Создание элементов управления
        self.create_control_buttons()
        self.create_track_selector()
        self.create_visualization_controls()
        self.create_save_button()
        self.create_user_info_panel()  # Добавляем панель с информацией о пользователе

        # Обновление списка треков
        self.update_track_list()

    def create_control_buttons(self) -> None:
        """Создание кнопок управления."""
        # Создаем одну кнопку для управления отслеживанием
        self.tracking_button = ttkb.Button(
            self.settings_frame,
            text="Начать отслеживание",
            command=self.toggle_tracking,
            bootstyle='success',
            padding=10,
            takefocus=0
        )
        self.tracking_button.pack(anchor=tk.N, fill=tk.X, pady=10)

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

    def toggle_tracking(self) -> None:
        """Переключение режима отслеживания."""
        if self.is_tracking:
            self.stop_tracking()
        else:
            self.start_tracking()

    def start_tracking(self) -> None:
        """Начать отслеживание мыши."""
        delay_seconds = 5
        messagebox.showinfo(
            "Информация",
            f"У вас есть {delay_seconds} секунд, чтобы свернуть окна и подготовить экран для скриншота..."
        )
        
        # Изменяем состояние кнопки на серую (неактивную) во время таймера
        self.tracking_button.config(text="Подготовка... (5 сек)", bootstyle='secondary', state='disabled')
        
        # Функция для запуска отслеживания после задержки
        def start_after_delay():
            # Активируем кнопку и меняем её цвет на красный
            self.is_tracking = True
            self.tracking_button.config(text="Завершить отслеживание", bootstyle='danger', state='normal')
            # Запускаем отслеживание со звуком
            play_start_sound()
            self.mouse_tracker.start_tracking()
        
        # Запускаем отслеживание с задержкой
        self.root.after(delay_seconds * 1000, start_after_delay)

    def stop_tracking(self) -> None:
        """Остановить отслеживание мыши."""
        self.mouse_tracker.stop_tracking()
        
        # Изменяем состояние кнопки
        self.is_tracking = False
        self.tracking_button.config(text="Начать отслеживание", bootstyle='success')
        
        # Обновляем список треков после остановки отслеживания
        self.update_track_list()

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

        # Проверяем, не отключена ли отправка данных в настройках
        if not self.config.get('network.send_data', True):
            if not messagebox.askyesno(
                "Отправка данных отключена",
                "Отправка данных на сервер отключена в настройках. Вы хотите отправить данные однократно?",
                icon='warning'
            ):
                return  # Пользователь отказался отправлять данные

        selected_file = self.track_combobox.get()
        file_path = os.path.join(self.data_manager.storage_dir, selected_file)

        try:
            # Загружаем данные трека
            track_data = self.data_manager.load_tracking_data(selected_file)
            
            # Добавляем информацию о пользователе
            track_data['user'] = self.user_data
            
            # Загружаем на GitHub
            self.network_client.upload_tracking_data(track_data)
            
            messagebox.showinfo(
                "Успех",
                "Тепловая карта успешно опубликована на сайте!"
            )

        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось загрузить данные: {str(e)}"
            )

    def create_user_info_panel(self) -> None:
        """Создание панели с информацией о пользователе."""
        # Создаем рамку для информации о пользователе
        user_frame = ttkb.LabelFrame(
            self.settings_frame,
            text="Информация о пользователе",
            padding=10,
            bootstyle="info"
        )
        user_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        # ФИО
        ttkb.Label(
            user_frame,
            text=f"ФИО: {self.user_data.get('fullname', '')}",
            wraplength=300,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=2)

        # Группа
        ttkb.Label(
            user_frame,
            text=f"Группа: {self.user_data.get('group', '')}",
            wraplength=300,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=2)

        # Программа
        ttkb.Label(
            user_frame,
            text=f"Программа: {self.user_data.get('selected_program', '')}",
            wraplength=300,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=2)
        
        # Добавляем разделитель
        ttkb.Separator(user_frame, bootstyle="info").pack(fill=tk.X, pady=5)
        
        # Создаем переменную для чекбокса
        self.send_data_var = tk.BooleanVar(value=self.config.get('network.send_data', True))
        
        # Добавляем чекбокс для включения/отключения отправки данных
        send_data_check = ttkb.Checkbutton(
            user_frame,
            text="Отправлять данные на сервер",
            variable=self.send_data_var,
            command=self._on_send_data_changed,
            bootstyle="info-round-toggle"
        )
        send_data_check.pack(anchor=tk.W, pady=5)
        
        # Добавляем кнопку настроек пользователя
        config_button = ttkb.Button(
            user_frame,
            text="Изменить настройки пользователя",
            command=self._open_user_config,
            bootstyle="info-outline"
        )
        config_button.pack(anchor=tk.W, pady=5, fill=tk.X)

    def _on_send_data_changed(self) -> None:
        """Обработчик изменения настройки отправки данных."""
        # Сохраняем настройку в конфигурацию
        self.config.set('network.send_data', self.send_data_var.get())
        
        # Выводим информационное сообщение
        state = "включена" if self.send_data_var.get() else "отключена"
        print(f"Отправка данных на сервер {state}")

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

    def _on_window_resize(self, event: Any) -> None:
        """Обработчик изменения размера окна."""
        # Проверяем, что событие пришло от главного окна, а не от дочерних виджетов
        if event.widget == self.root:
            # Используем debounce для предотвращения слишком частых обновлений
            if self._update_timer is not None:
                self.root.after_cancel(self._update_timer)
                
            # Планируем обновление через небольшую задержку
            self._update_timer = self.root.after(100, self.update_visualization)
            
    def _open_user_config(self) -> None:
        """Открывает диалог настроек пользователя."""
        from ui.first_launch_dialog import FirstLaunchDialog
        
        try:
            # Путь к конфигурационному файлу пользователя
            user_config_path = "config/user_config.json"
            
            # Создаем и показываем диалог настроек
            dialog = FirstLaunchDialog(self.root, user_config_path)
            new_user_data = dialog.show()
            
            # Если пользователь подтвердил изменения
            if new_user_data:
                # Обновляем данные пользователя
                self.user_data = new_user_data
                
                # Обновляем панель с информацией о пользователе
                # Сначала удаляем старую панель
                for widget in self.settings_frame.winfo_children():
                    if widget.winfo_class() == 'TLabelframe' and widget.cget('text') == "Информация о пользователе":
                        widget.destroy()
                
                # Создаем новую панель
                self.create_user_info_panel()
                
                # Показываем сообщение об успешном обновлении
                ttkb.messagebox.showinfo(
                    "Успешно",
                    "Настройки пользователя обновлены!"
                )
        except Exception as e:
            # В случае ошибки показываем сообщение
            ttkb.messagebox.showerror(
                "Ошибка",
                f"Не удалось обновить настройки пользователя: {str(e)}"
            ) 