import numpy as np
from scipy.ndimage import gaussian_filter
import matplotlib
# Явно устанавливаем backend перед импортом pyplot
matplotlib.use('Agg')  # Используем Agg backend, который не требует GUI
import matplotlib.pyplot as plt
from typing import List, Tuple, Any, Optional

from .base_visualizer import BaseVisualizer


class HeatmapVisualizer(BaseVisualizer):
    """Класс для визуализации тепловой карты."""

    def __init__(self):
        super().__init__()
        self.positions = []
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

    def update(self, data: List[Tuple[int, int, Any]]) -> None:
        """Обновить данные для визуализации."""
        self.positions = [(x, y) for x, y, _ in data]
        # Сбрасываем кэш при обновлении данных
        self._cached_heatmap = None
        # Сбрасываем флаг отображения фона при обновлении данных
        self._background_image_shown = False

    def _calculate_heatmap(self) -> Tuple[np.ndarray, List[float]]:
        """Вычислить тепловую карту."""
        if not self.positions or self.background_image is None:
            return None, None

        x, y = zip(*self.positions)
        x = np.array(x)
        y = np.array(y)

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
        return heatmap.T, extent

    def _update_figure_size(self) -> None:
        """Обновить размер фигуры в соответствии с размером окна."""
        current_size = self.fig.canvas.get_width_height()
        if self._last_window_size != current_size:
            width, height = current_size
            # Устанавливаем размер в дюймах (1 дюйм = 100 пикселей)
            self.fig.set_size_inches(width/100, height/100)
            self._last_window_size = current_size
            
            # Обновляем компоновку для правильного центрирования
            self.fig.tight_layout(pad=0)
            self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
            # Сбрасываем флаг отображения фона при изменении размера
            self._background_image_shown = False

    def render(self) -> np.ndarray:
        """Отрендерить тепловую карту."""
        try:
            # Добавляем отладочный вывод
            print("Начало рендеринга тепловой карты")
            print(f"Размер фонового изображения: {self.background_image.shape if self.background_image is not None else 'None'}")
            print(f"Количество позиций для тепловой карты: {len(self.positions)}")
            
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
            
            # Отображаем фоновое изображение
            print("Отображение фонового изображения")
            self.ax.imshow(self.background_image, extent=[0, self.background_image.shape[1], 
                                                        self.background_image.shape[0], 0])
            # Устанавливаем границы осей точно по размеру изображения
            self.ax.set_xlim(0, self.background_image.shape[1])
            self.ax.set_ylim(self.background_image.shape[0], 0)
            self._background_image_shown = True
            
            # Если есть позиции, создаем или используем кэшированную тепловую карту
            if self.positions:
                print("Рисуем тепловую карту поверх фона")
                if self._cached_heatmap is None:
                    print("Вычисление новой тепловой карты")
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
            
            # Обновляем холст
            print("Обновление холста фигуры")
            self.fig.canvas.draw()
            
            # Получаем размеры холста
            width, height = self.fig.canvas.get_width_height()
            print(f"Размеры холста: {width}x{height}")
            
            # Получаем данные изображения
            try:
                # Для новых версий matplotlib (3.5+)
                print("Попытка получения буфера RGBA")
                buf = self.fig.canvas.buffer_rgba()
                data = np.asarray(buf)
                # Конвертируем RGBA в RGB
                data = data[:, :, :3]
                print("Успешно получен RGBA буфер")
            except (AttributeError, TypeError) as e:
                print(f"Ошибка buffer_rgba: {e}, попытка использовать tostring_rgb")
                try:
                    # Для версий matplotlib 3.1 - 3.4
                    data = np.frombuffer(self.fig.canvas.tostring_rgb(), dtype=np.uint8)
                    expected_size = width * height * 3
                    
                    # Проверяем соответствие размеров
                    if len(data) != expected_size:
                        print(f"Предупреждение: Размер данных не соответствует ожидаемому ({len(data)} vs {expected_size})")
                        # Если размеры не совпадают, масштабируем данные
                        data = data[:expected_size]
                    
                    # Преобразуем в нужную форму
                    data = data.reshape(height, width, 3)
                    print("Успешно получен RGB буфер")
                except Exception as e:
                    print(f"Ошибка при получении данных изображения: {e}, последняя попытка с FigureCanvasAgg")
                    # Последняя попытка - использовать устаревший метод
                    from matplotlib.backends.backend_agg import FigureCanvasAgg
                    canvas = FigureCanvasAgg(self.fig)
                    canvas.draw()
                    data = np.array(canvas.renderer.buffer_rgba())[:, :, :3]
                    print("Успешно получен буфер через FigureCanvasAgg")
            
            print(f"Размер итогового изображения: {data.shape}")
            return data
            
        except Exception as e:
            print(f"Ошибка при рендеринге тепловой карты: {e}")
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
        self.fig.savefig(filepath, dpi=dpi, bbox_inches='tight') 