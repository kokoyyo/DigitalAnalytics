"""Экран прогресса и достижений"""

import tkinter as tk
from tkinter import ttk
from presentation.gui.styles import Colors, Fonts


class ProgressScreen(tk.Frame):
    """Экран прогресса"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=Colors.BG_LIGHT)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создание виджетов"""
        # Создаем Canvas для прокрутки
        self.canvas = tk.Canvas(self, bg=Colors.BG_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Создаем фрейм для содержимого внутри Canvas
        self.scrollable_frame = tk.Frame(self.canvas, bg=Colors.BG_LIGHT)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # При изменении размера canvas обновляем ширину окна
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Привязываем колесико мыши
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Создаем содержимое внутри скроллируемого фрейма
        self.create_content(self.scrollable_frame)
        
        # Сохраняем ссылки на элементы, которые нужно обновлять
        self.widgets_to_update = []
    
    def _on_canvas_configure(self, event):
        """Обновление ширины при изменении размера canvas"""
        canvas_width = event.width
        # Обновляем ширину окна в canvas
        self.canvas.itemconfig(1, width=canvas_width)
        # Обновляем ширину всех виджетов
        self.update_widgets_width(canvas_width)
    
    def update_widgets_width(self, width):
        """Обновление ширины виджетов при изменении размера окна"""
        if width > 0:
            # Обновляем ширину фреймов-контейнеров
            for widget in self.widgets_to_update:
                if isinstance(widget, tuple):
                    frame, padding = widget
                    try:
                        frame.config(width=width - padding)
                    except:
                        pass
                elif hasattr(widget, 'config'):
                    try:
                        widget.config(width=width - 40)
                    except:
                        pass
    
    def create_content(self, parent):
        """Создание содержимого экрана"""
        current_width = self.canvas.winfo_width() if hasattr(self, 'canvas') and self.canvas.winfo_width() > 0 else 900
        
        # Заголовок
        header_frame = tk.Frame(parent, bg=Colors.BG_WHITE)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        title_label = tk.Label(
            header_frame,
            text="📊 Прогресс изучения",
            font=Fonts.TITLE,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_DARK
        )
        title_label.pack(pady=20)
        
        # Достижения
        achievements_frame = tk.LabelFrame(
            parent, 
            text="🏆 Достижения", 
            font=Fonts.SUBTITLE, 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        achievements_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Контейнер для достижений с адаптивной сеткой
        ach_container = tk.Frame(achievements_frame, bg=Colors.BG_WHITE)
        ach_container.pack(fill=tk.BOTH, expand=True, pady=20, padx=10)
        
        # Настройка весов для равномерного распределения
        for i in range(3):
            ach_container.grid_columnconfigure(i, weight=1)
        
        achievements = [
            ("🔥 Текущая серия", "5 дней"),
            ("📚 Изучено сегодня", "12 слов"),
            ("🎯 Всего изучено", "248 слов")
        ]
        
        for i, (title, value) in enumerate(achievements):
            frame = tk.Frame(ach_container, bg=Colors.BG_WHITE, relief=tk.RIDGE, bd=1)
            frame.grid(row=0, column=i, padx=10, sticky="nsew")
            
            # Внутренние отступы
            tk.Label(
                frame, 
                text=title, 
                font=Fonts.BODY,
                bg=Colors.BG_WHITE, 
                fg=Colors.TEXT_GRAY
            ).pack(pady=(15, 5))
            
            tk.Label(
                frame, 
                text=value, 
                font=("Segoe UI", 20, "bold"),
                bg=Colors.BG_WHITE, 
                fg=Colors.PRIMARY
            ).pack(pady=(5, 15))
        
        # Общая статистика
        stats_frame = tk.LabelFrame(
            parent, 
            text="📈 Общая статистика", 
            font=Fonts.SUBTITLE, 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Контейнер для статистики с адаптивной сеткой
        stats_grid = tk.Frame(stats_frame, bg=Colors.BG_WHITE)
        stats_grid.pack(fill=tk.BOTH, expand=True, pady=20, padx=10)
        
        # Настройка весов для сетки (2x2)
        for i in range(2):
            stats_grid.grid_columnconfigure(i, weight=1)
        for i in range(2):
            stats_grid.grid_rowconfigure(i, weight=1)
        
        stats_data = [
            ("📋 Всего карточек", "420"),
            ("✅ Изучено", "248"),
            ("⏳ Осталось", "172"),
            ("📊 Процент", "59%")
        ]
        
        for i, (label, value) in enumerate(stats_data):
            row = i // 2
            col = i % 2
            frame = tk.Frame(stats_grid, bg=Colors.BG_WHITE, relief=tk.RIDGE, bd=1)
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            tk.Label(
                frame, 
                text=label, 
                font=Fonts.BODY,
                bg=Colors.BG_WHITE, 
                fg=Colors.TEXT_GRAY
            ).pack(pady=(15, 5))
            
            tk.Label(
                frame, 
                text=value, 
                font=("Segoe UI", 18, "bold"),
                bg=Colors.BG_WHITE, 
                fg=Colors.SUCCESS
            ).pack(pady=(5, 15))
        
        # Статистика за сегодня
        daily_frame = tk.LabelFrame(
            parent, 
            text="📅 Статистика за сегодня", 
            font=Fonts.SUBTITLE, 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        daily_frame.pack(fill=tk.X, padx=20, pady=10)
        
        daily_info = tk.Frame(daily_frame, bg=Colors.BG_WHITE)
        daily_info.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)
        
        # Настройка весов для колонок
        daily_info.grid_columnconfigure(0, weight=1)
        daily_info.grid_columnconfigure(1, weight=1)
        
        daily_stats = [
            ("🎴 Изучено карточек:", "12"),
            ("✓ Правильных ответов:", "85%"),
            ("⏱ Время изучения:", "25 мин")
        ]
        
        for i, (label, value) in enumerate(daily_stats):
            tk.Label(
                daily_info, 
                text=label, 
                font=Fonts.BODY, 
                bg=Colors.BG_WHITE, 
                fg=Colors.TEXT_DARK,
                anchor=tk.E
            ).grid(row=i, column=0, padx=20, pady=10, sticky="e")
            
            tk.Label(
                daily_info, 
                text=value, 
                font=Fonts.BODY_BOLD, 
                bg=Colors.BG_WHITE, 
                fg=Colors.SUCCESS,
                anchor=tk.W
            ).grid(row=i, column=1, padx=20, pady=10, sticky="w")
        
        # Добавляем нижний отступ для красоты
        bottom_spacer = tk.Frame(parent, height=20, bg=Colors.BG_LIGHT)
        bottom_spacer.pack()
        
        # Сохраняем ссылки на фреймы для обновления
        self.widgets_to_update = [
            (achievements_frame, 40),
            (stats_frame, 40),
            (daily_frame, 40)
        ]
    
    def update_content_width(self):
        """Обновление ширины контента"""
        if hasattr(self, 'canvas') and self.canvas.winfo_width() > 0:
            self.update_widgets_width(self.canvas.winfo_width())