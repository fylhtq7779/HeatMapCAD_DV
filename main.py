import pyautogui
from pynput import mouse
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import json
import os
import pandas as pd
import ttkbootstrap as ttkb  # Импортируем ttkbootstrap

class MouseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Тепловая карта движений мыши")
        self.root.geometry("1200x800")
        self.root.minsize(width=1200, height=800)  # Установить минимальный размер окна

        self.filter_stationary = tk.BooleanVar(value=False)  # Переменная для чекбокса
        self.positions = []
        self.listener = None
        self.color_map = 'hot'
        self.img = None
        self.screen_resolution = None

        self.setup_ui()

    def setup_ui(self):
        style = ttkb.Style("superhero")

        self.main_frame = ttkb.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        # Создаем фигуру и ось для графика
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.axis('off')

        # Устанавливаем канву для matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas_widget = self.canvas.get_tk_widget()

        # Создаем фрейм для настроек
        settings_frame = ttkb.Frame(self.main_frame, width=250, padding=10)
        settings_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Настройка виджета канвы, чтобы он занял оставшееся пространство
        self.canvas_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        button_style = {'bootstyle': 'primary', 'padding': 10}
        slider_style = {'bootstyle': 'success', 'orient': tk.HORIZONTAL}

        # Добавляем кнопки в фрейм с настройками
        ttkb.Button(settings_frame, text="Начать отслеживание", command=self.start_tracking, **button_style).pack(
            anchor=tk.N, fill=tk.X, pady=10)
        ttkb.Button(settings_frame, text="Завершить отслеживание", command=self.stop_tracking, **button_style).pack(
            anchor=tk.N, fill=tk.X, pady=10)
        ttkb.Button(settings_frame, text="Загрузить движения", command=self.load_positions, **button_style).pack(
            anchor=tk.N, fill=tk.X, pady=10)
        ttkb.Button(settings_frame, text="Загрузить изображение", command=self.load_image, **button_style).pack(
            anchor=tk.N, fill=tk.X, pady=10)

        # Добавляем слайдеры и метки для них
        ttkb.Label(settings_frame, text="Разрешение", font=("Arial", 10)).pack(anchor=tk.N)
        self.slider_resolution = ttkb.Scale(settings_frame, from_=10, to=500, **slider_style)
        self.slider_resolution.set(100)
        self.slider_resolution.pack(anchor=tk.N, fill=tk.X, pady=10)

        ttkb.Label(settings_frame, text="Яркость", font=("Arial", 10)).pack(anchor=tk.N)
        self.slider_brightness = ttkb.Scale(settings_frame, from_=0.1, to=3.0, **slider_style)
        self.slider_brightness.set(1.0)
        self.slider_brightness.pack(anchor=tk.N, fill=tk.X, pady=10)

        ttkb.Label(settings_frame, text="Размер", font=("Arial", 10)).pack(anchor=tk.N)
        self.slider_size = ttkb.Scale(settings_frame, from_=0.1, to=3.0, **slider_style)
        self.slider_size.set(1.0)
        self.slider_size.pack(anchor=tk.N, fill=tk.X, pady=10)

        ttkb.Label(settings_frame, text="Чувствительность", font=("Arial", 10)).pack(anchor=tk.N)
        self.slider_sensitivity = ttkb.Scale(settings_frame, from_=0.1, to=5.0, **slider_style)
        self.slider_sensitivity.set(1.0)
        self.slider_sensitivity.pack(anchor=tk.N, fill=tk.X, pady=10)

        # Добавляем возможность выбора цветовой карты
        cmap_label = ttkb.Label(settings_frame, text="Цветовая карта", font=("Arial", 10))
        cmap_label.pack(anchor=tk.N)

        cmap_options = ['hot', 'cool', 'viridis', 'plasma', 'inferno', 'magma', 'cividis']
        self.cmap_combobox = ttkb.Combobox(settings_frame, values=cmap_options)
        self.cmap_combobox.set(self.color_map)
        self.cmap_combobox.pack(anchor=tk.N, fill=tk.X, pady=10)
        self.cmap_combobox.bind("<<ComboboxSelected>>", self.change_color_map)

        self.filter_checkbox = ttkb.Checkbutton(
            self.main_frame, text="Фильтровать неподвижные координаты",
            variable=self.filter_stationary
        )
        self.filter_checkbox.pack(anchor=tk.N, fill=tk.X, pady=10)

        # Кнопка для сохранения тепловой карты
        ttkb.Button(settings_frame, text="Сохранить тепловую карту", command=self.save_heatmap, **button_style).pack(
            anchor=tk.S, fill=tk.X, pady=20)

        # Привязка изменений слайдеров к обновлению тепловой карты
        self.slider_resolution.bind("<ButtonRelease-1>", lambda event: self.update_heatmap())
        self.slider_brightness.bind("<ButtonRelease-1>", lambda event: self.update_heatmap())
        self.slider_size.bind("<ButtonRelease-1>", lambda event: self.update_heatmap())
        self.slider_sensitivity.bind("<ButtonRelease-1>", lambda event: self.update_heatmap())

    def change_color_map(self, event):
        self.color_map = self.cmap_combobox.get()
        self.update_heatmap()

    def start_tracking(self):
        delay_seconds = 5  # секунды ожидания

        # Функция, которая будет выполнена после ожидания
        def start_after_delay():
            screenshot = pyautogui.screenshot()
            self.img = np.array(screenshot)
            self.screen_resolution = (self.img.shape[1], self.img.shape[0])  # ширина, высота

            self.positions.clear()
            self.listener = mouse.Listener(on_move=self.on_move)
            self.listener.start()

        # Показать сообщение и сделать так, чтобы ожидание началось после закрытия messagebox
        msg_box = messagebox.showinfo(
            "Информация",
            f"У вас есть {delay_seconds} секунд, чтобы свернуть окна и подготовить экран для скриншота..."
        )

        # Используем `after` для ожидания перед выполнением скриншота
        self.root.after(delay_seconds * 1000, start_after_delay)

    def on_move(self, x, y):
        self.positions.append((x, y))

    def stop_tracking(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
            self.update_heatmap()
            self.save_positions()

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

    def load_positions(self):
        filepath = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filepath:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.positions = data['positions']
            res = data['resolution']
            self.img = np.zeros((res['height'], res['width'], 3), dtype=np.uint8)  # Черный фон с заданным разрешением
            self.update_heatmap()
            messagebox.showinfo("Информация", "Движения мыши загружены.")

    def load_image(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpeg"), ("All files", "*.*")])
        if filepath:
            self.img = np.array(plt.imread(filepath))
            self.update_heatmap()
            messagebox.showinfo("Информация", f"Изображение загружено: {filepath}")

    def create_heatmap(self, resolution, brightness, size_factor, sensitivity, img, x, y):
        if img is None:
            img = np.zeros((800, 1200, 3), dtype=np.uint8)  # Черный фон по умолчанию

        self.ax.clear()

        heatmap, xedges, yedges = np.histogram2d(x, y, bins=[resolution, resolution],
                                                 range=[[0, img.shape[1]], [0, img.shape[0]]])
        heatmap = heatmap ** sensitivity
        heatmap = gaussian_filter(heatmap, sigma=3 * size_factor)
        heatmap = np.clip(heatmap, 0, None)

        if np.max(heatmap) != 0:
            heatmap /= np.max(heatmap)

        heatmap *= brightness
        heatmap = np.clip(heatmap, 0, 1)

        self.ax.imshow(np.flipud(img))
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        self.ax.imshow(heatmap.T, extent=extent, origin='upper', cmap=self.color_map, alpha=heatmap.T)
        self.ax.axis('off')
        self.fig.tight_layout()
        self.fig.canvas.draw()

    def update_heatmap(self):
        resolution = int(float(self.slider_resolution.get()))
        brightness = self.slider_brightness.get()
        size_factor = self.slider_size.get()
        sensitivity = self.slider_sensitivity.get()

        if self.positions:
            x, y = zip(*self.positions)
            x = np.array(x)
            y = np.array(y)

            # Применяем фильтрацию, если чекбокс активен
            if self.filter_stationary.get():
                x, y = self.filter_positions(x, y)

            self.create_heatmap(resolution, brightness, size_factor, sensitivity, self.img, x, y)

    def save_heatmap(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if filepath:
            self.fig.savefig(filepath, dpi=300)
            messagebox.showinfo("Информация", f"Тепловая карта сохранена в: {filepath}")
            
    def filter_positions(self, x, y):
        filtered_x = [x[0]]
        filtered_y = [y[0]]

        for i in range(1, len(x)):
            if x[i] != x[i-1] or y[i] != y[i-1]:
                filtered_x.append(x[i])
                filtered_y.append(y[i])

        return np.array(filtered_x), np.array(filtered_y)


if __name__ == "__main__":
    root = ttkb.Window()
    app = MouseTrackerApp(root)
    root.mainloop()

