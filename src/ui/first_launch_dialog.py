import tkinter as tk
import ttkbootstrap as ttkb
from typing import Dict, Any, Optional
import json
import os


class FirstLaunchDialog:
    def __init__(self, parent: tk.Tk, config_path: str):
        try:
            print("Создание диалогового окна...")
            # Создаем новое окно вместо Toplevel
            self.dialog = ttkb.Window()
            self.dialog.title("Первый запуск")
            
            # Устанавливаем минимальный размер окна
            self.dialog.minsize(400, 300)
            
            self.config_path = config_path
            self.result: Optional[Dict[str, Any]] = None
            
            # Загружаем конфигурацию
            print("Загрузка конфигурации диалога...")
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            print("Создание виджетов диалога...")
            self.create_widgets()
            
            # Центрируем окно
            self.center_window()
            
            # Делаем окно модальным и поверх других окон
            self.dialog.lift()
            self.dialog.focus_force()
            print("Диалоговое окно создано и отображено")
            
        except Exception as e:
            print(f"Ошибка при создании диалога: {e}")
            raise

    def center_window(self):
        """Центрирование окна на экране."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        try:
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
            if self.config["user"].get("fullname"):
                self.name_entry.insert(0, self.config["user"]["fullname"])

            # Группа
            group_frame = ttkb.Frame(main_frame)
            group_frame.pack(fill=tk.X, pady=5)
            
            ttkb.Label(group_frame, text="Группа:").pack(side=tk.LEFT)
            self.group_entry = ttkb.Entry(group_frame, width=40)
            self.group_entry.pack(side=tk.LEFT, padx=(10, 0))
            if self.config["user"].get("group"):
                self.group_entry.insert(0, self.config["user"]["group"])

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
            if self.config["user"].get("selected_program"):
                self.program_combo.set(self.config["user"]["selected_program"])
            else:
                self.program_combo.set(self.config["available_programs"][0])

            # Кнопки
            button_frame = ttkb.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(20, 0))
            
            # Добавляем кнопку отмены
            ttkb.Button(
                button_frame,
                text="Отмена",
                command=self.cancel,
                bootstyle="secondary",
                width=20
            ).pack(side=tk.LEFT)
            
            ttkb.Button(
                button_frame,
                text="Сохранить",
                command=self.save_data,
                bootstyle="success",
                width=20
            ).pack(side=tk.RIGHT)

        except Exception as e:
            print(f"Ошибка при создании виджетов: {e}")
            raise

    def cancel(self):
        """Обработчик кнопки отмены."""
        self.result = None
        self.dialog.quit()
        self.dialog.destroy()

    def save_data(self):
        try:
            name = self.name_entry.get().strip()
            group = self.group_entry.get().strip()
            program = self.program_combo.get()

            if not name or not group:
                ttkb.messagebox.showerror(
                    "Ошибка",
                    "Пожалуйста, заполните все поля!"
                )
                return
                
            # Проверяем минимальную длину ФИО и группы
            if len(name) < 5:
                ttkb.messagebox.showerror(
                    "Ошибка",
                    "ФИО должно содержать не менее 5 символов!"
                )
                return
                
            if len(group) < 3:
                ttkb.messagebox.showerror(
                    "Ошибка",
                    "Название группы должно содержать не менее 3 символов!"
                )
                return

            # Сохраняем данные
            self.config["user"]["fullname"] = name
            self.config["user"]["group"] = group
            self.config["user"]["selected_program"] = program
            self.config["is_first_launch"] = False

            # Сохраняем конфигурацию
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)

            self.result = self.config["user"]
            self.dialog.quit()
            self.dialog.destroy()
            
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            ttkb.messagebox.showerror(
                "Ошибка",
                f"Не удалось сохранить данные: {str(e)}"
            )

    def show(self) -> Optional[Dict[str, Any]]:
        try:
            print("Ожидание взаимодействия с диалогом...")
            self.dialog.mainloop()
            print("Диалог закрыт")
            return self.result
        except Exception as e:
            print(f"Ошибка при отображении диалога: {e}")
            return None 