"""Модуль с кастомной темой для приложения."""
import ttkbootstrap as ttkb

def create_custom_theme():
    """Создает и возвращает кастомную темную тему."""
    return {
        "type": "dark",
        
        # Основные цвета
        "colors": {
            "primary": "#4A9EFF",  # Яркий синий
            "secondary": "#2D2D30",  # Тёмно-серый
            "success": "#3BD16F",  # Яркий зеленый
            "info": "#61AFEF",  # Светло-синий
            "warning": "#E5C07B",  # Приятный желтый
            "danger": "#E06C75",  # Приятный красный
            "bg": "#1E1E1E",  # Тёмный фон
            "fg": "#FFFFFF",  # Белый текст
            "selectbg": "#264F78",  # Синий для выделения
            "selectfg": "#FFFFFF",  # Белый текст на выделении
            "border": "#2D2D30",  # Тёмные границы
        },
        
        # Стили для виджетов
        "ttk": {
            "TFrame": {
                "configure": {
                    "background": "#1E1E1E",
                    "borderwidth": 0,
                }
            },
            "TLabel": {
                "configure": {
                    "background": "#1E1E1E",
                    "foreground": "#FFFFFF",
                    "font": ("Segoe UI", 10),
                }
            },
            "TButton": {
                "configure": {
                    "background": "#4A9EFF",
                    "foreground": "#FFFFFF",
                    "borderwidth": 0,
                    "focuscolor": "#4A9EFF",
                    "font": ("Segoe UI", 10, "bold"),
                    "padding": 10,
                },
                "map": {
                    "background": [("active", "#2B7DE9")],
                    "foreground": [("active", "#FFFFFF")],
                }
            },
            "Horizontal.TScale": {
                "configure": {
                    "background": "#1E1E1E",
                    "troughcolor": "#2D2D30",
                    "borderwidth": 0,
                    "focuscolor": "#4A9EFF",
                }
            },
            "TCombobox": {
                "configure": {
                    "fieldbackground": "#2D2D30",
                    "background": "#FFFFFF",
                    "foreground": "#FFFFFF",
                    "arrowcolor": "#FFFFFF",
                    "borderwidth": 0,
                    "focuscolor": "#4A9EFF",
                    "padding": 5,
                },
                "map": {
                    "fieldbackground": [("readonly", "#2D2D30")],
                    "foreground": [("readonly", "#FFFFFF")],
                }
            },
            "TLabelframe": {
                "configure": {
                    "background": "#1E1E1E",
                    "foreground": "#FFFFFF",
                    "borderwidth": 1,
                    "relief": "solid",
                    "bordercolor": "#2D2D30",
                }
            },
            "TLabelframe.Label": {
                "configure": {
                    "background": "#1E1E1E",
                    "foreground": "#FFFFFF",
                    "font": ("Segoe UI", 10, "bold"),
                }
            }
        }
    } 