"""
Handles the user interface components using ttkbootstrap.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mouse_tracker import MouseTracker
from heatmap import Heatmap
import ttkbootstrap as ttkb
import numpy as np
import os
import json

class MouseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Тепловая карта движений мыши")
        self.root.geometry("1200x800")

        # Initialize components responsible for tracking and plotting
        self.mouse_tracker = MouseTracker()
        self.heatmap = Heatmap()

        self.setup_ui()

    def setup_ui(self):
        style = ttkb.Style("superhero")

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        self.fig, self.ax = self.heatmap.create_figure()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        settings_frame = ttk.Frame(self.main_frame, width=250, padding=10)
        settings_frame.pack(side=tk.RIGHT, fill=tk.Y)

        button_style = {'bootstyle': 'primary', 'padding': 10}
        slider_style = {'bootstyle': 'success', 'orient': tk.HORIZONTAL}

        ttk.Button(settings_frame, text="Начать отслеживание", command=self.start_tracking, **button_style).pack(
            anchor=tk.N, fill=tk.X, pady=10)
        ttk.Button(settings_frame, text="Завершить отслеживание", command=self.stop_tracking, **button_style).pack(
            anchor=tk.N, fill=tk.X, pady=10)
        ttk.Button(settings_frame, text="Загрузить движения", command=self.load_positions, **button_style).pack(
            anchor=tk.N, fill=tk.X, pady=10)
        ttk.Button(settings_frame, text="Загрузить изображение", command=self.load_image, **button_style).pack(
            anchor=tk.N, fill=tk.X, pady=10)

        ttk.Label(settings_frame, text="Разрешение", font=("Arial", 10)).pack(anchor=tk.N)
        self.slider_resolution = ttk.Scale(settings_frame, from_=10, to=500, **slider_style)
        self.slider_resolution.set(100)
        self.slider_resolution.pack(anchor=tk.N, fill=tk.X, pady=10)

        ttk.Label(settings_frame, text="Яркость", font=("Arial", 10)).pack(anchor=tk.N)
        self.slider_brightness = ttk.Scale(settings_frame, from_=0.1, to=3.0, **slider_style)
        self.slider_brightness.set(1.0)
        self.slider_brightness.pack(anchor=tk.N, fill=tk.X, pady=10)

        ttk.Label(settings_frame, text="Размер", font=("Arial", 10)).pack(anchor=tk.N)
        self.slider_size = ttk.Scale(settings_frame, from_=0.1, to=3.0, **slider_style)
        self.slider_size.set(1.0)
        self.slider_size.pack(anchor=tk.N, fill=tk.X, pady=10)

        ttk.Label(settings_frame, text="Чувствительность", font=("Arial", 10)).pack(anchor=tk.N)
        self.slider_sensitivity = ttk.Scale(settings_frame, from_=0.1, to=5.0, **slider_style)
        self.slider_sensitivity.set(1.0)
        self.slider_sensitivity.pack(anchor=tk.N, fill=tk.X, pady=10)

        cmap_label = ttk.Label(settings_frame, text="Цветовая карта", font=("Arial", 10))
        cmap_label.pack(anchor=tk.N)

        cmap_options = ['hot', 'cool', 'viridis', 'plasma', 'inferno', 'magma', 'cividis']
        self.cmap_combobox = ttk.Combobox(settings_frame, values=cmap_options)
        self.cmap_combobox.set(self.heatmap.color_map)
        self.cmap_combobox.pack(anchor=tk.N, fill=tk.X, pady=10)
        self.cmap_combobox.bind("<<ComboboxSelected>>", self.change_color_map)

        ttk.Button(settings_frame, text="Сохранить тепловую карту", command=self.save_heatmap, **button_style).pack(
            anchor=tk.S, fill=tk.X, pady=20)

        self.slider_resolution.bind("<ButtonRelease-1>", lambda event: self.update_heatmap())
        self.slider_brightness.bind("<ButtonRelease-1>", lambda event: self.update_heatmap())
        self.slider_size.bind("<ButtonRelease-1>", lambda event: self.update_heatmap())
        self.slider_sensitivity.bind("<ButtonRelease-1>", lambda event: self.update_heatmap())

    def change_color_map(self, event):
        self.heatmap.color_map = self.cmap_combobox.get()
        self.update_heatmap()

    def start_tracking(self):
        self.mouse_tracker.start_tracking(self.root)

    def stop_tracking(self):
        self.mouse_tracker.stop_tracking()
        self.update_heatmap()
        self.save_positions()

    def save_positions(self):
        self.mouse_tracker.save_positions()

    def load_positions(self):
        filepath = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filepath:
            self.mouse_tracker.load_positions(filepath)
            self.update_heatmap()
            messagebox.showinfo("Информация", "Движения мыши загружены.")

    def load_image(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpeg"), ("All files", "*.*")])
        if filepath:
            self.heatmap.load_image(filepath)
            self.update_heatmap()
            messagebox.showinfo("Информация", f"Изображение загружено: {filepath}")

    def update_heatmap(self):
        if self.mouse_tracker.positions:
            x, y = zip(*self.mouse_tracker.positions)
            self.heatmap.update_heatmap(x, y, self.slider_resolution, self.slider_brightness, self.slider_size,
                                        self.slider_sensitivity)

    def save_heatmap(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if filepath:
            self.heatmap.save_heatmap(filepath)
            messagebox.showinfo("Информация", f"Тепловая карта сохранена в: {filepath}")
