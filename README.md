```markdown
# Mouse Tracker Application

This is a Python application for tracking mouse movements and generating heatmaps based on those movements. It's built using `pyautogui`, `pynput`, `matplotlib`, and `ttkbootstrap` for GUI elements.

## Project Structure

```
project/
│
├── main.py
├── ui.py
├── mouse_tracker.py
├── heatmap.py
├── utils.py
└── README.md
```

- `main.py`: The main entry point to start the application. It initializes and runs the `MouseTrackerApp`.
- `ui.py`: Contains the `MouseTrackerApp` class responsible for setting up the user interface using ttkbootstrap.
- `mouse_tracker.py`: Manages the tracking of mouse movements.
- `heatmap.py`: Responsible for creating and updating heatmaps based on the tracked mouse movements.
- `utils.py`: Contains utility functions (if needed).
- `README.md`: This file provides an overview of the project.

## Usage

1. Start the application by running `main.py`.
2. Use the interface to start and stop mouse tracking.
3. Load images or movement data, and see the resulting heatmap.
4. Save your heatmap as an image if needed.

## Requirements

- Python 3.x
- pyautogui
- pynput
- matplotlib
- numpy
- scipy
- ttkbootstrap
``` 
