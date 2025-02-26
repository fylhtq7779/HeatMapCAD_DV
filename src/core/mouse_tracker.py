from datetime import datetime
from pynput import mouse
import pyautogui
import numpy as np
from typing import Optional, Tuple
import time
from threading import Lock

from .input_tracker import InputTracker


class MouseTracker(InputTracker):
    """Класс для отслеживания движений мыши."""

    def __init__(self):
        super().__init__()
        self.listener: Optional[mouse.Listener] = None
        self.screen_resolution: Optional[Tuple[int, int]] = None
        self.screenshot: Optional[np.ndarray] = None
        
        # Параметры оптимизации
        self.last_update_time = 0
        self.update_interval = 1/60  # 60 Hz
        self.last_x = 0
        self.last_y = 0
        self.min_distance = 1  # Минимальное расстояние для записи
        self.lock = Lock()

    def start_tracking(self) -> None:
        """Начать отслеживание мыши."""
        if self.is_tracking:
            return

        print("Начинаем отслеживание мыши...")
        
        # Получаем скриншот и разрешение экрана
        try:
            print("Пытаемся создать скриншот...")
            screenshot = pyautogui.screenshot()
            print(f"Скриншот успешно создан, размер: {screenshot.width}x{screenshot.height}")
            
            self.screenshot = np.array(screenshot)
            print(f"Преобразование в numpy массив: форма {self.screenshot.shape}, тип {self.screenshot.dtype}")
            
            self.screen_resolution = (self.screenshot.shape[1], self.screenshot.shape[0])
            print(f"Установлено разрешение экрана: {self.screen_resolution}")
        except Exception as e:
            print(f"ОШИБКА при создании скриншота: {e}")
            print("Попытка создать пустой скриншот...")
            try:
                # Создаем пустой скриншот если не удалось сделать настоящий
                width, height = pyautogui.size()
                print(f"Размер экрана по pyautogui.size(): {width}x{height}")
                self.screenshot = np.zeros((height, width, 3), dtype=np.uint8)
                self.screen_resolution = (width, height)
                print(f"Создан пустой скриншот: {self.screenshot.shape}")
            except Exception as e2:
                print(f"КРИТИЧЕСКАЯ ОШИБКА при создании пустого скриншота: {e2}")
                # Установка предполагаемого разрешения
                self.screenshot = np.zeros((1080, 1920, 3), dtype=np.uint8)
                self.screen_resolution = (1920, 1080)
                print("Установлен аварийный пустой скриншот 1920x1080")

        # Очищаем предыдущие данные
        self.clear_data()
        
        # Сбрасываем параметры оптимизации
        self.last_update_time = 0
        self.last_x = 0
        self.last_y = 0

        # Создаем и запускаем слушателя событий мыши
        self.listener = mouse.Listener(on_move=self._on_move)
        self.listener.start()
        self.is_tracking = True
        print("Отслеживание мыши запущено")
        
        # Уведомляем слушателей о начале отслеживания
        self.notify_listeners("tracking_started", {
            "resolution": self.screen_resolution,
            "timestamp": datetime.now()
        })

    def _calculate_distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """Вычислить расстояние между двумя точками."""
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    def _on_move(self, x: int, y: int) -> None:
        """Обработчик события движения мыши."""
        if not self.is_tracking:
            return

        current_time = time.time()
        
        # Нормализуем координаты, чтобы избежать отрицательных значений
        x = max(0, x)
        y = max(0, y)
        
        # Проверяем, что координаты не выходят за пределы экрана
        if self.screen_resolution:
            width, height = self.screen_resolution
            x = min(x, width - 1)
            y = min(y, height - 1)
        
        # Проверяем интервал обновления и расстояние
        if (current_time - self.last_update_time >= self.update_interval and 
            self._calculate_distance(x, y, self.last_x, self.last_y) >= self.min_distance):
            
            with self.lock:
                self.positions.append((x, y, datetime.now()))
                self.last_update_time = current_time
                self.last_x = x
                self.last_y = y
                
                # Уведомляем слушателей о новой позиции
                self.notify_listeners("position_updated", {
                    "x": x,
                    "y": y,
                    "timestamp": datetime.now()
                })

    def stop_tracking(self) -> None:
        """Остановить отслеживание мыши."""
        if not self.is_tracking:
            return

        if self.listener:
            self.listener.stop()
            self.listener.join()
            self.listener = None
            self.is_tracking = False

            # Уведомляем слушателей о завершении отслеживания
            with self.lock:
                self.notify_listeners("tracking_stopped", {
                    "positions_count": len(self.positions),
                    "timestamp": datetime.now()
                })

    @property
    def current_screenshot(self) -> Optional[np.ndarray]:
        """Получить текущий скриншот."""
        return self.screenshot.copy() if self.screenshot is not None else None 