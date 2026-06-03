"""
Калькулятор с историей операций — GUI версия (tkinter)
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from typing import List, Dict, Union


class CalculatorGUI:
    """Графический калькулятор с историей"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🧮 Калькулятор с историей")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        self.history: List[Dict[str, Union[str, float]]] = []
        self.history_file = "calc_history.json"
        
        self._create_styles()
        self._create_widgets()
        self._load_history()
        self._update_history_display()
    
    def _create_styles(self):
        """Настройка стилей"""
        self.bg_color = "#2c3e50"
        self.fg_color = "#ecf0f1"
        self.accent_color = "#3498db"
        self.btn_color = "#34495e"
        self.root.configure(bg=self.bg_color)
    
    def _create_widgets(self):
        """Создание элементов интерфейса"""
        # === Верхняя часть: Дисплей ===
        self.display_var = tk.StringVar(value="0")
        
        display_frame = tk.Frame(self.root, bg=self.bg_color)
        display_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.display = tk.Entry(
            display_frame,
            textvariable=self.display_var,
            font=("Arial", 28),
            justify="right",
            bg="#1a252f",
            fg=self.fg_color,
            insertbackground=self.fg_color,
            bd=0,
            highlightthickness=2,
            highlightcolor=self.accent_color
        )
        self.display.pack(fill=tk.X, ipady=10)
        
        # === Поле ввода операции ===
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Label(input_frame, text="Операция:", bg=self.bg_color, fg=self.fg_color,
                font=("Arial", 12)).pack(side=tk.LEFT)
        
        self.op_var = tk.StringVar(value="+")
        op_combo = ttk.Combobox(input_frame, textvariable=self.op_var, 
                               values=["+", "-", "*", "/"], width=5, state="readonly")
        op_combo.pack(side=tk.LEFT, padx=5)
        op_combo.configure(font=("Arial", 14))
        
        # === Кнопки управления ===
        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Button(btn_frame, text="Вычислить", command=self._calculate,
                 bg=self.accent_color, fg="white", font=("Arial", 12, "bold"),
                 width=15, cursor="hand2", bd=0, pady=5).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="Очистить", command=self._clear_display,
                 bg="#e74c3c", fg="white", font=("Arial", 12),
                 width=10, cursor="hand2", bd=0, pady=5).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="Стереть", command=self._backspace,
                 bg=self.btn_color, fg=self.fg_color, font=("Arial", 12),
                 width=10, cursor="hand2", bd=0, pady=5).pack(side=tk.LEFT, padx=2)
        
        # === Цифровая клавиатура ===
        keypad_frame = tk.Frame(self.root, bg=self.bg_color)
        keypad_frame.pack(padx=10, pady=5)
        
        buttons = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['0', '.', '±']
        ]
        
        for row_idx, row in enumerate(buttons):
            for col_idx, char in enumerate(row):
                btn = tk.Button(
                    keypad_frame,
                    text=char,
                    command=lambda c=char: self._on_number_click(c),
                    bg=self.btn_color,
                    fg=self.fg_color,
                    font=("Arial", 16, "bold"),
                    width=5,
                    height=2,
                    cursor="hand2",
                    bd=0,
                    activebackground=self.accent_color,
                    activeforeground="white"
                )
                btn.grid(row=row_idx, column=col_idx, padx=3, pady=3)
        
        # === История операций ===
        history_frame = tk.LabelFrame(self.root, text=" История операций ", 
                                     bg=self.bg_color, fg=self.fg_color,
                                     font=("Arial", 11, "bold"))
        history_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.history_text = scrolledtext.ScrolledText(
            history_frame,
            wrap=tk.WORD,
            bg="#1a252f",
            fg=self.fg_color,
            font=("Consolas", 10),
            bd=0,
            highlightthickness=0
        )
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.history_text.config(state=tk.DISABLED)
        
        # === Кнопки истории ===
        hist_btn_frame = tk.Frame(self.root, bg=self.bg_color)
        hist_btn_frame.pack(padx=10, pady=5, fill=tk.X)
        
        tk.Button(hist_btn_frame, text="🗑️ Очистить историю", command=self._clear_history,
                 bg="#e67e22", fg="white", font=("Arial", 10),
                 cursor="hand2", bd=0, pady=5).pack(side=tk.LEFT, padx=2)
        
        tk.Button(hist_btn_frame, text="💾 Сохранить в файл", command=self._save_to_file,
                 bg="#27ae60", fg="white", font=("Arial", 10),
                 cursor="hand2", bd=0, pady=5).pack(side=tk.LEFT, padx=2)
        
        # Привязка клавиш
        self.root.bind('<Return>', lambda e: self._calculate())
        self.root.bind('<BackSpace>', lambda e: self._backspace())
        self.root.bind('<Escape>', lambda e: self._clear_display())
        for i in range(10):
            self.root.bind(str(i), lambda e, num=i: self._on_number_click(str(num)))
    
    def _on_number_click(self, char: str):
        """Обработка нажатия цифровой кнопки"""
        current = self.display_var.get()
        
        if char == '±':
            if current.startswith('-'):
                self.display_var.set(current[1:])
            else:
                self.display_var.set('-' + current)
        elif char == '.' and '.' in current:
            pass
        else:
            if current == '0' and char != '.':
                self.display_var.set(char)
            else:
                self.display_var.set(current + char)
    
    def _clear_display(self):
        """Очистка дисплея"""
        self.display_var.set("0")
    
    def _backspace(self):
        """Стереть последний символ"""
        current = self.display_var.get()
        if len(current) > 1:
            self.display_var.set(current[:-1])
        else:
            self.display_var.set("0")
    
    def _calculate(self):
        """Выполнение вычисления"""
        try:
            # Получаем значения
            expr = self.display_var.get()
            if not expr or expr == '0':
                return
            
            # Ввод второго числа через диалог
            self._show_input_dialog(expr)
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.display_var.set("0")
    
    def _show_input_dialog(self, first_num: str):
        """Диалог ввода второго числа"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Второе число")
        dialog.geometry("300x150")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"Первое число: {first_num}", 
                bg=self.bg_color, fg=self.fg_color, font=("Arial", 12)).pack(pady=5)
        
        tk.Label(dialog, text="Введите второе число:", 
                bg=self.bg_color, fg=self.fg_color, font=("Arial", 11)).pack()
        
        entry = tk.Entry(dialog, font=("Arial", 16), justify="center", width=15)
        entry.pack(pady=5)
        entry.focus()
        
        def do_calc():
            try:
                num1 = float(first_num)
                num2 = float(entry.get())
                op = self.op_var.get()
                
                if op == '+':
                    result = num1 + num2
                elif op == '-':
                    result = num1 - num2
                elif op == '*':
                    result = num1 * num2
                elif op == '/':
                    if num2 == 0:
                        raise ZeroDivisionError("Деление на ноль!")
                    result = num1 / num2
                
                # Форматирование
                expr_str = f"{num1} {op} {num2} = {result:.4f}".rstrip('0').rstrip('.')
                
                # Сохранение в историю
                self._add_to_history(expr_str, result)
                
                # Обновление дисплея
                self.display_var.set(str(result).rstrip('0').rstrip('.'))
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число!")
            except ZeroDivisionError as e:
                messagebox.showerror("Ошибка", str(e))
                dialog.destroy()
        
        tk.Button(dialog, text="Вычислить", command=do_calc,
                 bg=self.accent_color, fg="white", font=("Arial", 12),
                 cursor="hand2", bd=0, pady=5, width=15).pack(pady=5)
        
        entry.bind('<Return>', lambda e: do_calc())
    
    def _add_to_history(self, expression: str, result: float):
        """Добавление в историю"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "expression": expression,
            "result": result
        }
        self.history.append(entry)
        self._update_history_display()
        self._save_history()
    
    def _update_history_display(self):
        """Обновление отображения истории"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        
        if not self.history:
            self.history_text.insert(tk.END, "История пуста...")
        else:
            for i, entry in enumerate(self.history, 1):
                self.history_text.insert(tk.END, 
                    f"{i}. [{entry['timestamp']}]\n   {entry['expression']}\n\n")
        
        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)
    
    def _clear_history(self):
        """Очистка истории"""
        if not self.history:
            return
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history = []
            self._update_history_display()
            self._save_history()
    
    def _save_to_file(self):
        """Сохранение истории в файл через диалог"""
        filename = f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== ИСТОРИЯ ОПЕРАЦИЙ ===\n\n")
                for entry in self.history:
                    f.write(f"[{entry['timestamp']}] {entry['expression']}\n")
            messagebox.showinfo("Успех", f"История сохранена в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _save_history(self):
        """Сохранение в JSON"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def _load_history(self):
        """Загрузка истории"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.history = []


def main():
    root = tk.Tk()
    app = CalculatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()