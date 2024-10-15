"""
Responsible for creating and updating heatmaps based on mouse movements.
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter

class Heatmap:
    def __init__(self):
        self.img = None
        self.color_map = 'hot'
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.ax.axis('off')

    def create_figure(self):
        return self.fig, self.ax

    def load_image(self, filepath):
        self.img = np.array(plt.imread(filepath))

    def update_heatmap(self, x, y, slider_resolution, slider_brightness, slider_size, slider_sensitivity):
        resolution = int(float(slider_resolution.get()))
        brightness = slider_brightness.get()
        size_factor = slider_size.get()
        sensitivity = slider_sensitivity.get()

        if self.img is None:
            self.img = np.zeros((800, 1200, 3), dtype=np.uint8)

        self.ax.clear()

        heatmap, xedges, yedges = np.histogram2d(x, y, bins=[resolution, resolution], range=[[0, self.img.shape[1]], [0, self.img.shape[0]]])
        heatmap = heatmap ** sensitivity
        heatmap = gaussian_filter(heatmap, sigma=3 * size_factor)
        heatmap = np.clip(heatmap, 0, None)

        if np.max(heatmap) != 0:
            heatmap /= np.max(heatmap)

        heatmap *= brightness
        heatmap = np.clip(heatmap, 0, 1)

        self.ax.imshow(np.flipud(self.img))
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        self.ax.imshow(heatmap.T, extent=extent, origin='upper', cmap=self.color_map, alpha=heatmap.T)
        self.ax.axis('off')
        self.fig.tight_layout()
        self.fig.canvas.draw()

    def save_heatmap(self, filepath):
        self.fig.savefig(filepath, dpi=300)
