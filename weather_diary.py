import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary / Дневник погоды")
        self.root.geometry("850x600")
        self.root.resizable(True, True)
        
        self.entries = []  # Хранилище всех записей
        self.setup_ui()
        self.load_from_json()  # Автоматическая загрузка при запуске

    def setup_ui(self):
        # --- Блок ввода ---
        input_frame = ttk.LabelFrame(self.root, text="➕ Новая запись")
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Дата (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.desc_entry = ttk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="we")

        ttk.Label(input_frame, text="Осадки:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.precip_var = tk.StringVar(value="Нет")
        self.precip_combo = ttk.Combobox(input_frame, textvariable=self.precip_var, 
                                         values=["Да", "Нет"], state="readonly", width=10)
        self.precip_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(input_frame, text="Добавить запись", command=self.add_entry).grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky="e")

        # --- Блок фильтрации ---
        filter_frame = ttk.LabelFrame(self.root, text="🔍 Фильтрация")
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Дата (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.filter_date_entry = ttk.Entry(filter_frame, width=20)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="Температура > (°C):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filter).grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky="e")

        # --- Таблица записей ---
        table_frame = ttk.LabelFrame(self.root, text="📋 Список записей")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("date", "temp", "desc", "precip")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Темп. (°C)")
        self.tree.heading("desc", text="Описание погоды")
        self.tree.heading("precip", text="Осадки")
        
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("temp", width=90, anchor="center")
        self.tree.column("desc", width=350, anchor="w")
        self.tree.column("precip", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Кнопки управления файлами ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="💾 Сохранить в JSON", command=self.save_to_json).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📂 Загрузить из JSON", command=self.load_from_json).pack(side="left", padx=5)

    def validate_inputs(self):
        date_str = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()

        if not date_str:
            messagebox.showerror("Ошибка", "Поле 'Дата' не может быть пустым.")
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Ожидается: YYYY-MM-DD")
            return False

        if not temp_str:
            messagebox.showerror("Ошибка", "Поле 'Температура' не может быть пустым.")
            return False
        try:
            float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом (например: 15.5 или -3).")
            return False

        if not desc:
            messagebox.showerror("Ошибка", "Поле 'Описание' не может быть пустым.")
            return False

        return True

    def add_entry(self):
        if not self.validate_inputs():
            return

        new_entry = {
            "date": self.date_entry.get().strip(),
            "temp": float(self.temp_entry.get().strip()),
            "desc": self.desc_entry.get().strip(),
            "precip": self.precip_var.get()
        }
        self.entries.append(new_entry)
        self.populate_table(self.entries)
        self.clear_inputs()
        messagebox.showinfo("Успех", "Запись успешно добавлена!")

    def clear_inputs(self):
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set("Нет")

    def populate_table(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for e in data:
            self.tree.insert("", tk.END, values=(e["date"], f"{e['temp']:.1f}", e["desc"], e["precip"]))

    def apply_filter(self):
        date_filter = self.filter_date_entry.get().strip()
        temp_filter = self.filter_temp_entry.get().strip()

        if not date_filter and not temp_filter:
            messagebox.showwarning("Внимание", "Укажите хотя бы один параметр фильтрации.")
            return

        filtered = []
        for e in self.entries:
            match_date = (e["date"] == date_filter) if date_filter else True
            match_temp = True
            
            if temp_filter:
                try:
                    threshold = float(temp_filter)
                    match_temp = e["temp"] > threshold
                except ValueError:
                    messagebox.showerror("Ошибка", "Неверное значение температуры для фильтра.")
                    return

            if match_date and match_temp:
                filtered.append(e)

        self.populate_table(filtered)
        messagebox.showinfo("Результат", f"Найдено записей: {len(filtered)}")

    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.populate_table(self.entries)

    def save_to_json(self):
        try:
            with open("weather_diary.json", "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", "Данные сохранены в weather_diary.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def load_from_json(self):
        if not os.path.exists("weather_diary.json"):
            self.entries = []
            self.populate_table(self.entries)
            return
        try:
            with open("weather_diary.json", "r", encoding="utf-8") as f:
                self.entries = json.load(f)
            self.populate_table(self.entries)
            messagebox.showinfo("Успех", "Данные загружены из weather_diary.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")
            self.entries = []

if __name__ == "__main__":
    root = tk.Tk()
    # Установка темы (опционально, работает в Python 3.10+)
    try:
        style = ttk.Style()
        style.theme_use("clam")
    except:
        pass
    app = WeatherDiaryApp(root)
    root.mainloop()