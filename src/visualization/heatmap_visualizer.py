import numpy as np
from scipy.ndimage import gaussian_filter
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
        
        # Улучшаем отображение
        self.fig.tight_layout(pad=0)
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    def update(self, data: List[Tuple[int, int, Any]]) -> None:
        """Обновить данные для визуализации."""
        self.positions = [(x, y) for x, y, _ in data]
        # Сбрасываем кэш при обновлении данных
        self._cached_heatmap = None

    def _calculate_heatmap(self) -> Tuple[np.ndarray, List[float]]:
        """Вычислить тепловую карту."""
        if not self.positions:
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

    def render(self) -> np.ndarray:
        """Рендерит текущую тепловую карту и возвращает изображение."""
        try:
            # Если есть фоновое изображение и данные хитмапа
            if hasattr(self, 'background_image') and self.positions:
                # Если фон - пустой массив, создаем его
                if self.background_image is None:
                    self._update_figure_size()
                    # Создаем пустой фон
                    self.background_image = np.ones((self.background_image.shape[0], self.background_image.shape[1], 3), dtype=np.uint8) * 255
                
                # Рассчитываем данные для тепловой карты
                heatmap, extent = self._calculate_heatmap()
                
                # Очищаем предыдущий график
                self.ax.clear()
                
                # Отображаем фоновое изображение
                self.ax.imshow(self.background_image, aspect='auto')
                
                # Отображаем тепловую карту поверх
                self.heatmap = self.ax.imshow(
                    heatmap, 
                    alpha=0.6, 
                    cmap=self.config['colormap'],
                    extent=extent,
                    interpolation='bilinear',
                    aspect='auto'
                )
                
                # Убираем оси
                self.ax.axis('off')
                
                # Добавляем цветовую шкалу, если требуется
                if self.show_colorbar:
                    if hasattr(self, 'colorbar'):
                        self.colorbar.remove()
                    self.colorbar = self.fig.colorbar(
                        self.heatmap, 
                        ax=self.ax, 
                        orientation='vertical',
                        fraction=0.05,
                        pad=0.01
                    )
                    
                    # Устанавливаем границы осей точно по размеру изображения
                    if self.background_image is not None:
                        self.ax.set_xlim(0, self.background_image.shape[1])
                        self.ax.set_ylim(self.background_image.shape[0], 0)

            # Обновляем холст
            self.fig.canvas.draw()
            
            # Получаем размеры холста
            width, height = self.fig.canvas.get_width_height()
            
            try:
                # Пробуем новый метод (для новых версий matplotlib)
                buf = self.fig.canvas.buffer_rgba()
                data = np.asarray(buf)
                # Конвертируем RGBA в RGB
                data = data[:, :, :3]
            except (AttributeError, TypeError):
                try:
                    # Пробуем старый метод (для старых версий matplotlib)
                    data = np.frombuffer(self.fig.canvas.tostring_rgb(), dtype=np.uint8)
                    expected_size = width * height * 3
                    
                    # Проверяем соответствие размеров
                    if len(data) != expected_size:
                        # Если размеры не совпадают, масштабируем данные
                        data = data[:expected_size]
                    
                    # Преобразуем в нужную форму
                    data = data.reshape(height, width, 3)
                except Exception as inner_e:
                    print(f"Ошибка при обработке данных изображения: {inner_e}")
                    # Третий вариант - использование renderer
                    from matplotlib.backends.backend_agg import FigureCanvasAgg
                    canvas = FigureCanvasAgg(self.fig)
                    canvas.draw()
                    renderer = canvas.get_renderer()
                    raw_data = renderer.buffer_rgba()
                    data = np.frombuffer(raw_data, dtype=np.uint8).reshape((height, width, 4))
                    # Конвертируем RGBA в RGB
                    data = data[:, :, :3]
            
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