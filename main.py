"""
Main entry point for the application. Initializes and runs the MouseTrackerApp.
"""

import ttkbootstrap as ttkb
from ui import MouseTrackerApp

if __name__ == "__main__":
    root = ttkb.Window()  # Используем ttkb.Window для корректного использования стиля
    app = MouseTrackerApp(root)
    root.mainloop()
