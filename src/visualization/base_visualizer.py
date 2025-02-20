from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import numpy as np


class BaseVisualizer(ABC):
    """Базовый абстрактный класс для всех визуализаторов."""

    def __init__(self):
        self.background_image: Optional[np.ndarray] = None
        self.config: Dict[str, Any] = {}

    @abstractmethod
    def update(self, data: Any) -> None:
        """Обновить визуализацию новыми данными."""
        pass

    @abstractmethod
    def render(self) -> np.ndarray:
        """Отрендерить визуализацию."""
        pass

    def set_background(self, image: np.ndarray) -> None:
        """Установить фоновое изображение."""
        self.background_image = image.copy() if image is not None else None

    def set_config(self, config: Dict[str, Any]) -> None:
        """Установить конфигурацию визуализатора."""
        self.config.update(config)

    @abstractmethod
    def export(self, filepath: str, **kwargs) -> None:
        """Экспортировать визуализацию в файл."""
        pass

    @property
    def visualization_type(self) -> str:
        """Получить тип визуализации."""
        return self.__class__.__name__ 