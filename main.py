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
import ttkbootstrap as ttkb


class MouseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Тепловая карта движений мыши")
        self.root.geometry("1200x800")
        self.root.minsize(width=1200, height=800)

        self.positions = []
        self.listener = None
        self.color_map = 'hot'
        self.img = None
        self.screen_resolution = None
        self.tracks_directory = "mouse_tracks"

        if not os.path.exists(self.tracks_directory):
            os.makedirs(self.tracks_directory)

        self.setup_ui()
        self.update_tracks_combobox()

    def setup_ui(self):
        style = ttkb.Style("superhero")

        self.main_frame = ttkb.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.axis('off')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas_widget = self.canvas.get_tk_widget()

        settings_frame = ttkb.Frame(self.main_frame, width=250, padding=10)
        settings_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        button_style = {'bootstyle': 'primary', 'padding': 10, 'takefocus': 0}
        slider_style = {'bootstyle': 'success', 'orient': tk.HORIZONTAL, 'takefocus': 0}

        ttkb.Button(settings_frame, text="Начать отслеживание", command=self.start_tracking, **button_style).pack(
            anchor=tk.N, fill=tk.X, pady=10)
        ttkb.Button(settings_frame, text="Завершить отслеживание", command=self.stop_tracking, **button_style).pack(
            anchor=tk.N, fill=tk.X, pady=10)

        ttkb.Label(settings_frame, text="Выберите маршрут", font=("Arial", 10)).pack(anchor=tk.N)
        self.track_combobox = ttkb.Combobox(settings_frame, state='readonly', takefocus=0)
        self.track_combobox.pack(anchor=tk.N, fill=tk.X, pady=10)
        self.track_combobox.bind("<<ComboboxSelected>>", self.load_selected_track)

        ttkb.Button(settings_frame, text="Загрузить изображение", command=self.load_image, **button_style).pack(
            anchor=tk.N, fill=tk.X, pady=10)

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

        cmap_label = ttkb.Label(settings_frame, text="Цветовая карта", font=("Arial", 10))
        cmap_label.pack(anchor=tk.N)

        cmap_options = ['hot', 'cool', 'viridis', 'plasma', 'inferno', 'magma', 'cividis']
        self.cmap_combobox = ttkb.Combobox(settings_frame, values=cmap_options, state='readonly', takefocus=0)
        self.cmap_combobox.set(self.color_map)
        self.cmap_combobox.pack(anchor=tk.N, fill=tk.X, pady=10)
        self.cmap_combobox.bind("<<ComboboxSelected>>", self.change_color_map)

        ttkb.Button(settings_frame, text="Сохранить тепловую карту", command=self.save_heatmap, **button_style).pack(
            anchor=tk.S, fill=tk.X, pady=20)

        self.slider_resolution.bind("<ButtonRelease-1>", lambda event: self.update_heatmap())
        self.slider_brightness.bind("<ButtonRelease-1>", lambda event: self.update_heatmap())
        self.slider_size.bind("<ButtonRelease-1>", lambda event: self.update_heatmap())
        self.slider_sensitivity.bind("<ButtonRelease-1>", lambda event: self.update_heatmap())

    def change_color_map(self, event):
        self.color_map = self.cmap_combobox.get()
        self.update_heatmap()

    def start_tracking(self):
        delay_seconds = 5

        def start_after_delay():
            screenshot = pyautogui.screenshot()
            self.img = np.array(screenshot)
            self.screen_resolution = (self.img.shape[1], self.img.shape[0])

            self.positions.clear()
            self.listener = mouse.Listener(on_move=self.on_move)
            self.listener.start()

        messagebox.showinfo(
            "Информация",
            f"У вас есть {delay_seconds} секунд, чтобы свернуть окна и подготовить экран для скриншота..."
        )

        self.root.after(delay_seconds * 1000, start_after_delay)

    def on_move(self, x, y):
        self.positions.append((x, y))

    def stop_tracking(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
            self.update_heatmap()
            filename = self.save_positions()
            self.update_tracks_combobox()
            self.track_combobox.set(os.path.basename(filename))

    def save_positions(self):
        if self.positions and self.screen_resolution:
            data = {
                'resolution': {
                    'width': self.screen_resolution[0],
                    'height': self.screen_resolution[1]
                },
                'positions': self.positions
            }
            # Форматирование имени файла с текущей датой и временем (без секунд)
            current_time = time.strftime("%Y-%m-%d_%H-%M")
            filename = os.path.join(self.tracks_directory, f"track_{current_time}.json")
            with open(filename, 'w') as f:
                json.dump(data, f)
            messagebox.showinfo("Информация", f"Движения мыши сохранены в: {filename}")
            return filename

    def update_tracks_combobox(self):
        files = [f for f in os.listdir(self.tracks_directory) if f.endswith('.json')]
        self.track_combobox['values'] = files

    def load_selected_track(self, event):
        selected_file = self.track_combobox.get()
        if selected_file:
            filepath = os.path.join(self.tracks_directory, selected_file)
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.positions = data['positions']
            res = data['resolution']
            self.img = np.zeros((res['height'], res['width'], 3), dtype=np.uint8)
            self.update_heatmap()
            messagebox.showinfo("Информация", f"Выбранный маршрут загружен: {selected_file}")

    def load_image(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpeg"), ("All files", "*.*")])
        if filepath:
            self.img = np.array(plt.imread(filepath))
            self.update_heatmap()
            messagebox.showinfo("Информация", f"Изображение загружено: {filepath}")

    def create_heatmap(self, resolution, brightness, size_factor, sensitivity, img, x, y):
        if img is None:
            img = np.zeros((800, 1200, 3), dtype=np.uint8)

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
            self.create_heatmap(resolution, brightness, size_factor, sensitivity, self.img, x, y)

    def save_heatmap(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if filepath:
            self.fig.savefig(filepath, dpi=300)
            messagebox.showinfo("Информация", f"Тепловая карта сохранена в: {filepath}")


if __name__ == "__main__":
    root = ttkb.Window()
    app = MouseTrackerApp(root)
    root.mainloop()
