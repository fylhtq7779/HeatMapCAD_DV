"""
Responsible for tracking mouse movements.
"""

import pyautogui
from pynput import mouse
import numpy as np
import json
import os
from tkinter import messagebox  # Убедитесь, что этот импорт добавлен

class MouseTracker:
    def __init__(self):
        self.positions = []
        self.listener = None
        self.screen_resolution = None

    def start_tracking(self, root):
        delay_seconds = 5
        messagebox.showinfo("Информация",
                            f"У вас есть {delay_seconds} секунд, чтобы свернуть окна и подготовить экран для скриншота...")
        root.after(delay_seconds * 1000, self._start_tracking)

    def _start_tracking(self):
        screenshot = pyautogui.screenshot()
        self.screen_resolution = screenshot.size
        self.positions.clear()
        self.listener = mouse.Listener(on_move=self.on_move)
        self.listener.start()

    def on_move(self, x, y):
        self.positions.append((x, y))

    def stop_tracking(self):
        if self.listener:
            self.listener.stop()
            self.listener = None

    def save_positions(self):
        if self.positions and self.screen_resolution:
            data = {
                'resolution': {
                    'width': self.screen_resolution[0],
                    'height': self.screen_resolution[1]
                },
                'positions': self.positions
            }
            filename = os.path.join(os.getcwd(), "mouse_movements.json")
            with open(filename, 'w') as f:
                json.dump(data, f)
            messagebox.showinfo("Информация", f"Движения мыши сохранены в: {filename}")

    def load_positions(self, filepath):
        if filepath:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.positions = data['positions']
