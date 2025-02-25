import tkinter as tk
import ttkbootstrap as ttkb
from typing import Dict, Any, Optional
import json
import os


class FirstLaunchDialog:
    def __init__(self, parent: tk.Tk, config_path: str):
        self.dialog = ttkb.Toplevel(parent)
        self.dialog.title("Первый запуск")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.config_path = config_path
        self.result: Optional[Dict[str, Any]] = None
        
        # Загружаем конфигурацию
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.create_widgets()
        
        # Центрируем окно
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'+{x}+{y}')

    def create_widgets(self):
        # Создаем основной контейнер с отступами
        main_frame = ttkb.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        title_label = ttkb.Label(
            main_frame,
            text="Добро пожаловать!\nПожалуйста, введите ваши данные:",
            font=("Segoe UI", 12, "bold"),
            justify=tk.CENTER
        )
        title_label.pack(pady=(0, 20))

        # ФИО
        name_frame = ttkb.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        ttkb.Label(name_frame, text="ФИО:").pack(side=tk.LEFT)
        self.name_entry = ttkb.Entry(name_frame, width=40)
        self.name_entry.pack(side=tk.LEFT, padx=(10, 0))

        # Группа
        group_frame = ttkb.Frame(main_frame)
        group_frame.pack(fill=tk.X, pady=5)
        
        ttkb.Label(group_frame, text="Группа:").pack(side=tk.LEFT)
        self.group_entry = ttkb.Entry(group_frame, width=40)
        self.group_entry.pack(side=tk.LEFT, padx=(10, 0))

        # Программа
        program_frame = ttkb.Frame(main_frame)
        program_frame.pack(fill=tk.X, pady=5)
        
        ttkb.Label(program_frame, text="Программа:").pack(side=tk.LEFT)
        self.program_combo = ttkb.Combobox(
            program_frame,
            values=self.config["available_programs"],
            state="readonly",
            width=37
        )
        self.program_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.program_combo.set(self.config["available_programs"][0])

        # Кнопки
        button_frame = ttkb.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttkb.Button(
            button_frame,
            text="Сохранить",
            command=self.save_data,
            bootstyle="success",
            width=20
        ).pack(side=tk.RIGHT)

    def save_data(self):
        name = self.name_entry.get().strip()
        group = self.group_entry.get().strip()
        program = self.program_combo.get()

        if not name or not group:
            ttkb.messagebox.showerror(
                "Ошибка",
                "Пожалуйста, заполните все поля!"
            )
            return

        # Сохраняем данные
        self.config["user"]["full_name"] = name
        self.config["user"]["group"] = group
        self.config["user"]["selected_program"] = program
        self.config["is_first_launch"] = False

        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

        self.result = self.config["user"]
        self.dialog.destroy()

    def show(self) -> Optional[Dict[str, Any]]:
        self.dialog.wait_window()
        return self.result 