"""Экран настроек"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from presentation.gui.styles import Colors, Fonts


class SettingsScreen(tk.Frame):
    """Экран настроек"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=Colors.BG_LIGHT)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создание виджетов"""
        # Создаем Canvas для прокрутки
        canvas = tk.Canvas(self, bg=Colors.BG_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        # Создаем фрейм для содержимого внутри Canvas
        self.scrollable_frame = tk.Frame(canvas, bg=Colors.BG_LIGHT)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=canvas.winfo_width())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # При изменении размера canvas обновляем ширину окна
        canvas.bind("<Configure>", self._on_canvas_configure)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Привязываем колесико мыши
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Создаем содержимое
        self.create_content(self.scrollable_frame)
    
    def _on_canvas_configure(self, event):
        """Обновление ширины при изменении размера canvas"""
        canvas_width = event.width
        self.canvas.itemconfig(1, width=canvas_width)
        self.canvas = canvas
    
    def create_content(self, parent):
        """Создание содержимого экрана"""
        # Заголовок
        header_frame = tk.Frame(parent, bg=Colors.BG_WHITE)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text="⚙️ Настройки",
            font=Fonts.TITLE,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_DARK
        ).pack(pady=20)
        
        # Настройка приложения
        app_frame = tk.LabelFrame(
            parent, 
            text="🎨 Настройка приложения", 
            font=Fonts.SUBTITLE, 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        app_frame.pack(fill=tk.X, padx=20, pady=10)
        
        theme_frame = tk.Frame(app_frame, bg=Colors.BG_WHITE)
        theme_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(
            theme_frame, 
            text="Тема оформления:", 
            font=Fonts.BODY, 
            bg=Colors.BG_WHITE, 
            fg=Colors.TEXT_DARK
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        theme_var = tk.StringVar(value="light")
        light_radio = tk.Radiobutton(
            theme_frame, 
            text="Светлая", 
            variable=theme_var, 
            value="light", 
            bg=Colors.BG_WHITE, 
            font=Fonts.BODY
        )
        light_radio.pack(side=tk.LEFT, padx=10)
        
        dark_radio = tk.Radiobutton(
            theme_frame, 
            text="Темная", 
            variable=theme_var, 
            value="dark", 
            bg=Colors.BG_WHITE, 
            font=Fonts.BODY, 
            state=tk.DISABLED
        )
        dark_radio.pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            theme_frame, 
            text="(темная тема в разработке)", 
            font=Fonts.SMALL, 
            bg=Colors.BG_WHITE, 
            fg=Colors.TEXT_GRAY
        ).pack(side=tk.LEFT, padx=10)
        
        # Управление данными
        data_frame = tk.LabelFrame(
            parent, 
            text="💾 Управление данными", 
            font=Fonts.SUBTITLE, 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        data_frame.pack(fill=tk.X, padx=20, pady=10)
        
        btn_frame = tk.Frame(data_frame, bg=Colors.BG_WHITE)
        btn_frame.pack(pady=20)
        
        export_btn = tk.Button(
            btn_frame,
            text="📤 Экспортировать данные",
            command=self.export_data,
            bg=Colors.SUCCESS,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        export_btn.pack(side=tk.LEFT, padx=10)
        
        import_btn = tk.Button(
            btn_frame,
            text="📥 Импортировать данные",
            command=self.import_data,
            bg=Colors.PRIMARY,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        import_btn.pack(side=tk.LEFT, padx=10)
        
        # О программе
        about_frame = tk.LabelFrame(
            parent, 
            text="ℹ️ О программе", 
            font=Fonts.SUBTITLE, 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        about_frame.pack(fill=tk.X, padx=20, pady=10)
        
        about_text = """
Flashcard English v0.1.0

Приложение для изучения английского языка по методу флеш-карточек
Разработано с использованием Python и Tkinter

Функции:
• Создание и управление колодами карточек
• Тестирование с множественным выбором
• Отслеживание прогресса и достижений
• Глобальный поиск по словам и переводам

© 2024 Все права защищены
        """
        
        tk.Label(
            about_frame, 
            text=about_text, 
            font=Fonts.BODY, 
            bg=Colors.BG_WHITE, 
            fg=Colors.TEXT_GRAY, 
            justify=tk.LEFT
        ).pack(pady=20)
        
        # Добавляем нижний отступ
        tk.Frame(parent, height=20, bg=Colors.BG_LIGHT).pack()
    
    def export_data(self):
        """Экспорт данных"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            messagebox.showinfo("Экспорт", f"Данные экспортированы в {filename}\n(Функция в разработке)")
    
    def import_data(self):
        """Импорт данных"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            messagebox.showinfo("Импорт", f"Данные импортированы из {filename}\n(Функция в разработке)")