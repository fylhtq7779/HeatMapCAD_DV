import tkinter as tk
import ttkbootstrap as ttkb

def main():
    print("Создание главного окна...")
    root = ttkb.Window(themename="darkly")
    root.title("Тестовое окно")
    root.geometry("300x200")
    
    print("Создание кнопки...")
    button = ttkb.Button(root, text="Тестовая кнопка", bootstyle="success")
    button.pack(pady=20)
    
    print("Запуск главного цикла...")
    root.mainloop()

if __name__ == "__main__":
    print("Запуск программы...")
    main() 