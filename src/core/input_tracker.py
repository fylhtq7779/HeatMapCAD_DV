from abc import ABC, abstractmethod
from typing import List, Tuple, Any
from datetime import datetime


class InputTracker(ABC):
    """Базовый абстрактный класс для всех трекеров устройств ввода."""
    
    def __init__(self):
        self.positions: List[Tuple[Any, Any, datetime]] = []
        self.is_tracking: bool = False
        self.listeners = []

    @abstractmethod
    def start_tracking(self) -> None:
        """Начать отслеживание устройства ввода."""
        pass

    @abstractmethod
    def stop_tracking(self) -> None:
        """Остановить отслеживание устройства ввода."""
        pass

    def add_listener(self, listener) -> None:
        """Добавить слушателя событий."""
        self.listeners.append(listener)

    def remove_listener(self, listener) -> None:
        """Удалить слушателя событий."""
        if listener in self.listeners:
            self.listeners.remove(listener)

    def notify_listeners(self, event_type: str, data: Any) -> None:
        """Уведомить всех слушателей о событии."""
        for listener in self.listeners:
            listener(event_type, data)

    def clear_data(self) -> None:
        """Очистить собранные данные."""
        self.positions.clear()

    @property
    def tracking_data(self) -> List[Tuple[Any, Any, datetime]]:
        """Получить собранные данные."""
        return self.positions.copy() 