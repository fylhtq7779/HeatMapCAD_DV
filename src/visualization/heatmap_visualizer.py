import numpy as np
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from typing import List, Tuple, Any, Optional
import os
import sys

from .base_visualizer import BaseVisualizer


class HeatmapVisualizer(BaseVisualizer):
    """Класс для визуализации тепловой карты."""

    def __init__(self):
        super().__init__()
        self.positions = []
        print(f"Инициализация HeatmapVisualizer")
        
        # Устанавливаем аппаратно-независимый бэкенд для matplotlib
        try:
            print(f"Текущий бэкенд matplotlib: {plt.get_backend()}")
            plt.switch_backend('Agg')
            print(f"Переключен на бэкенд: {plt.get_backend()}")
        except Exception as e:
            print(f"Ошибка при переключении бэкенда matplotlib: {e}")
        
        # Создаем фигуру и оси
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.axis('off')
        
        # Настройки по умолчанию
        self.config.update({
            'resolution': 100,
            'brightness': 1.0,
            'size_factor': 1.0,
            'sensitivity': 1.0,
            'colormap': 'hot'
        })
        
        # Кэш для оптимизации
        self._cached_heatmap = None
        self._cached_extent = None
        self._background_image_shown = False
        self._last_window_size = None
        
        # Добавляем атрибут show_colorbar
        self.show_colorbar = False
        
        # Улучшаем отображение
        self.fig.tight_layout(pad=0)
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        # Печатаем информацию о пути и версии Python
        print(f"Текущая директория: {os.getcwd()}")
        print(f"Версия Python: {sys.version}")
        print(f"Путь к Python: {sys.executable}")
        print(f"Версия matplotlib: {plt.__version__}")

    def update(self, data: List[Tuple[int, int, Any]]) -> None:
        """Обновить данные для визуализации."""
        print(f"Обновление данных визуализатора: {len(data)} точек")
        self.positions = [(x, y) for x, y, _ in data]
        # Сбрасываем кэш при обновлении данных
        self._cached_heatmap = None
        # Сбрасываем флаг отображения фона при обновлении данных
        self._background_image_shown = False

    def set_background(self, image):
        """Установить фоновое изображение."""
        print(f"Установка фонового изображения. Тип: {type(image)}, Форма: {image.shape if hasattr(image, 'shape') else 'неизвестно'}")
        super().set_background(image)
        # Сбрасываем кэш и флаг при изменении фона
        self._cached_heatmap = None
        self._background_image_shown = False

    def _calculate_heatmap(self) -> Tuple[np.ndarray, List[float]]:
        """Вычислить тепловую карту."""
        if not self.positions or self.background_image is None:
            print("Невозможно рассчитать тепловую карту: нет позиций или фонового изображения")
            return None, None

        print(f"Расчет тепловой карты из {len(self.positions)} точек")
        x, y = zip(*self.positions)
        x = np.array(x)
        y = np.array(y)

        # Проверяем наличие отрицательных координат
        if np.min(x) < 0 or np.min(y) < 0:
            print(f"Предупреждение: обнаружены отрицательные координаты! x_min={np.min(x)}, y_min={np.min(y)}")
            # Нормализуем координаты
            x = np.clip(x, 0, self.background_image.shape[1])
            y = np.clip(y, 0, self.background_image.shape[0])

        heatmap, xedges, yedges = np.histogram2d(
            x, y,
            bins=[self.config['resolution'], self.config['resolution']],
            range=[[0, self.background_image.shape[1]], [0, self.background_image.shape[0]]]
        )

        # Применяем настройки
        heatmap = heatmap ** self.config['sensitivity']
        heatmap = gaussian_filter(heatmap, sigma=3 * self.config['size_factor'])
        
        if np.max(heatmap) != 0:
            heatmap /= np.max(heatmap)
        
        heatmap *= self.config['brightness']
        heatmap = np.clip(heatmap, 0, 1)

        extent = [0, self.background_image.shape[1], self.background_image.shape[0], 0]
        print(f"Расчет тепловой карты завершен. Размер: {heatmap.shape}, Диапазон: {extent}")
        return heatmap.T, extent

    def _update_figure_size(self) -> None:
        """Обновить размер фигуры в соответствии с размером окна."""
        try:
            current_size = self.fig.canvas.get_width_height()
            if self._last_window_size != current_size:
                width, height = current_size
                print(f"Обновление размера фигуры до {width}x{height} пикселей")
                # Устанавливаем размер в дюймах (1 дюйм = 100 пикселей)
                self.fig.set_size_inches(width/100, height/100)
                self._last_window_size = current_size
                
                # Обновляем компоновку для правильного центрирования
                self.fig.tight_layout(pad=0)
                self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
                # Сбрасываем флаг отображения фона при изменении размера
                self._background_image_shown = False
        except Exception as e:
            print(f"Ошибка при обновлении размера фигуры: {e}")

    def render(self) -> np.ndarray:
        """Отрендерить тепловую карту."""
        print("Начало рендеринга тепловой карты")
        try:
            # Обновляем размер фигуры
            self._update_figure_size()
            
            # Всегда очищаем оси для перерисовки
            self.ax.clear()
            self.ax.axis('off')
            
            # Проверяем наличие фонового изображения
            if self.background_image is None:
                print("Ошибка: Фоновое изображение (скриншот) отсутствует")
                width, height = self.fig.canvas.get_width_height()
                return np.zeros((height, width, 3), dtype=np.uint8)
            
            # Проверяем тип и форму фонового изображения
            print(f"Фоновое изображение: тип={type(self.background_image)}, форма={self.background_image.shape}")
            
            # Отображаем фоновое изображение
            self.ax.imshow(self.background_image, extent=[0, self.background_image.shape[1], 
                                                        self.background_image.shape[0], 0])
            # Устанавливаем границы осей точно по размеру изображения
            self.ax.set_xlim(0, self.background_image.shape[1])
            self.ax.set_ylim(self.background_image.shape[0], 0)
            self._background_image_shown = True
            print("Фоновое изображение отображено")
            
            # Если есть позиции, создаем или используем кэшированную тепловую карту
            if self.positions:
                print(f"Отображение тепловой карты из {len(self.positions)} точек")
                if self._cached_heatmap is None:
                    self._cached_heatmap, self._cached_extent = self._calculate_heatmap()
                
                if self._cached_heatmap is not None:
                    # Отображаем тепловую карту поверх фона
                    heatmap_img = self.ax.imshow(
                        self._cached_heatmap,
                        extent=self._cached_extent,
                        origin='upper',
                        cmap=self.config['colormap'],
                        alpha=self._cached_heatmap
                    )
                    
                    # Добавляем цветовую шкалу если нужно
                    if self.show_colorbar:
                        self.fig.colorbar(heatmap_img, ax=self.ax)
                    print("Тепловая карта отображена")
            
            # Обновляем холст
            print("Обновление canvas")
            self.fig.canvas.draw()
            
            # Получаем размеры холста
            width, height = self.fig.canvas.get_width_height()
            
            # Получаем данные изображения
            print(f"Получение данных изображения с размерами {width}x{height}")
            try:
                # Для новых версий matplotlib (3.5+)
                print("Попытка использования buffer_rgba")
                buf = self.fig.canvas.buffer_rgba()
                data = np.asarray(buf)
                # Конвертируем RGBA в RGB
                data = data[:, :, :3]
                print(f"Данные изображения получены, форма: {data.shape}")
            except (AttributeError, TypeError) as e:
                print(f"Ошибка buffer_rgba: {e}, пробуем tostring_rgb")
                try:
                    # Для версий matplotlib 3.1 - 3.4
                    data = np.frombuffer(self.fig.canvas.tostring_rgb(), dtype=np.uint8)
                    expected_size = width * height * 3
                    
                    # Проверяем соответствие размеров
                    if len(data) != expected_size:
                        print(f"Несоответствие размеров: ожидалось {expected_size}, получено {len(data)}")
                        # Если размеры не совпадают, масштабируем данные
                        data = data[:expected_size]
                    
                    # Преобразуем в нужную форму
                    data = data.reshape(height, width, 3)
                    print(f"Данные преобразованы, форма: {data.shape}")
                except Exception as e:
                    print(f"Ошибка при получении данных изображения: {e}, пробуем FigureCanvasAgg")
                    # Последняя попытка - использовать устаревший метод
                    from matplotlib.backends.backend_agg import FigureCanvasAgg
                    print("Создание FigureCanvasAgg")
                    canvas = FigureCanvasAgg(self.fig)
                    canvas.draw()
                    buffer = canvas.buffer_rgba()
                    data = np.asarray(buffer)[:, :, :3]
                    print(f"Данные получены с помощью FigureCanvasAgg, форма: {data.shape}")
            
            print("Рендеринг завершен успешно")
            return data
            
        except Exception as e:
            print(f"Ошибка при рендеринге тепловой карты: {e}")
            import traceback
            traceback.print_exc()
            # Возвращаем пустое изображение в случае ошибки
            width, height = self.fig.canvas.get_width_height()
            return np.zeros((height, width, 3), dtype=np.uint8)

    def set_config(self, config: dict) -> None:
        """Установить конфигурацию визуализатора."""
        super().set_config(config)
        # Сбрасываем кэш при изменении конфигурации
        self._cached_heatmap = None

    def export(self, filepath: str, dpi: int = 300) -> None:
        """Экспортировать тепловую карту в файл."""
        print(f"Экспорт тепловой карты в {filepath}")
        self.fig.savefig(filepath, dpi=dpi, bbox_inches='tight') 