"""Экран прогресса и достижений"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from presentation.gui.styles import Colors, Fonts
from data.repositories import DeckRepository, CardRepository, StatisticsRepository


class ProgressScreen(tk.Frame):
    """Экран прогресса"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=Colors.BG_LIGHT)
        self.parent = parent
        self.deck_repo = DeckRepository()
        self.card_repo = CardRepository()
        self.stats_repo = StatisticsRepository()
        
        self.create_widgets()
        self.load_data()
        
        # Привязываем событие изменения размера
        self.bind("<Configure>", self.on_resize)
    
    def format_time(self, minutes):
        """Форматирование времени в минуты и секунды"""
        if minutes <= 0:
            return "0 мин"
        
        # Округляем до 2 знаков для точности
        total_seconds = int(round(minutes * 60))
        
        mins = total_seconds // 60
        secs = total_seconds % 60
        
        if mins > 0 and secs > 0:
            return f"{mins} мин {secs} сек"
        elif mins > 0:
            return f"{mins} мин"
        else:
            return f"{secs} сек"
    
    def create_widgets(self):
        """Создание виджетов с прокруткой"""
        # Создаем Canvas для прокрутки
        canvas = tk.Canvas(self, bg=Colors.BG_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        self.scrollable_frame = tk.Frame(canvas, bg=Colors.BG_LIGHT)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas = canvas
        scrollbar.pack(side="right", fill="y")
        
        # Универсальный обработчик скролла
        self._mousewheel_handler = self._make_mousewheel_handler()
        self._bind_mousewheel(canvas)
        self._bind_mousewheel(self.scrollable_frame)
    
    def _make_mousewheel_handler(self):
        """Возвращает плавный обработчик скролла колесиком"""
        def handler(event):
            if hasattr(event, 'delta') and event.delta != 0:
                delta = -1 * (event.delta // 30)
            elif event.num == 4:
                delta = -3
            elif event.num == 5:
                delta = 3
            else:
                return
            
            current_pos = self.canvas.yview()[0]
            new_pos = current_pos + (delta / 100)
            new_pos = max(0, min(1, new_pos))
            self.canvas.yview_moveto(new_pos)
            self.canvas.update_idletasks()
        return handler

    def _bind_mousewheel(self, widget):
        """Привязывает скролл к виджету и всем его дочерним элементам рекурсивно"""
        widget.bind("<MouseWheel>", self._mousewheel_handler, add="+")
        widget.bind("<Button-4>", self._mousewheel_handler, add="+")
        widget.bind("<Button-5>", self._mousewheel_handler, add="+")
        for child in widget.winfo_children():
            self._bind_mousewheel(child)
    
    def load_data(self):
        """Загрузка всех данных с принудительным обновлением"""
        # Очищаем старые данные
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Принудительно получаем свежие данные из БД
        self.stats_repo.refresh()
        
        # Получаем данные
        streak = self.stats_repo.get_current_streak()
        today_stats = self.stats_repo.get_today_stats()
        global_stats = self.stats_repo.get_global_stats()
        total_studied_all_time = global_stats['studied_cards']
        
        # Заголовок
        header_frame = tk.Frame(self.scrollable_frame, bg=Colors.BG_WHITE)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text="📊 Прогресс изучения",
            font=Fonts.TITLE,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_DARK
        ).pack(pady=20)
        
        # ===== ДОСТИЖЕНИЯ =====
        achievements_frame = tk.LabelFrame(
            self.scrollable_frame, 
            text="🏆 Достижения", 
            font=Fonts.SUBTITLE, 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        achievements_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Карточки достижений
        ach_container = tk.Frame(achievements_frame, bg=Colors.BG_WHITE)
        ach_container.pack(fill=tk.BOTH, expand=True, pady=20, padx=10)
        
        for i in range(3):
            ach_container.grid_columnconfigure(i, weight=1)
        
        achievements = [
            ("🔥 Текущая серия", f"{streak} дней", "Повторяйте слова каждый день!"),
            ("📚 Изучено сегодня", f"{today_stats['cards_studied']} слов", "Сегодняшние успехи"),
            ("🎯 Всего изучено", f"{total_studied_all_time} слов", "Общий прогресс")
        ]
        
        for i, (title, value, subtitle) in enumerate(achievements):
            frame = tk.Frame(ach_container, bg=Colors.BG_WHITE, relief=tk.RIDGE, bd=1)
            frame.grid(row=0, column=i, padx=10, sticky="nsew")
            
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
            ).pack(pady=(5, 5))
            
            tk.Label(
                frame, 
                text=subtitle, 
                font=Fonts.SMALL,
                bg=Colors.BG_WHITE, 
                fg=Colors.TEXT_GRAY
            ).pack(pady=(0, 15))
        
        # ===== ОБЩАЯ СТАТИСТИКА =====
        stats_frame = tk.LabelFrame(
            self.scrollable_frame, 
            text="📈 Общая статистика", 
            font=Fonts.SUBTITLE, 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        stats_frame.pack(fill=tk.X, padx=20, pady=10)

        stats_grid = tk.Frame(stats_frame, bg=Colors.BG_WHITE)
        stats_grid.pack(fill=tk.BOTH, expand=True, pady=20, padx=10)

        for i in range(2):
            stats_grid.grid_columnconfigure(i, weight=1)
        for i in range(2):
            stats_grid.grid_rowconfigure(i, weight=1)

        stats_data = [
            ("📋 Всего карточек", str(global_stats['total_cards'])),
            ("✅ Изучено", str(global_stats['studied_cards'])),
            ("⏳ Осталось", str(global_stats['remaining_cards'])),
            ("📊 Процент", f"{global_stats['percent']}%")
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
        
        # ===== ПРОГРЕСС ЗА ПЕРИОД (график) =====
        period_frame = tk.LabelFrame(
            self.scrollable_frame, 
            text="📅 Прогресс за последние 7 дней", 
            font=Fonts.SUBTITLE, 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        period_frame.pack(fill=tk.X, padx=20, pady=10)
        
        period_data = self.stats_repo.get_studied_cards_period(7)
        
        if period_data:
            graph_frame = tk.Frame(period_frame, bg=Colors.BG_WHITE)
            graph_frame.pack(pady=20, padx=20)
            
            max_value = max([count for _, count in period_data]) if period_data else 1
            
            for date_str, count in period_data:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                date_label = date_obj.strftime('%d.%m')
                
                bar_height = 30
                bar_width = (count / max_value) * 300 if max_value > 0 else 0
                
                row_frame = tk.Frame(graph_frame, bg=Colors.BG_WHITE)
                row_frame.pack(fill=tk.X, pady=5)
                
                tk.Label(
                    row_frame, 
                    text=date_label, 
                    width=10, 
                    anchor=tk.W,
                    font=Fonts.SMALL,
                    bg=Colors.BG_WHITE
                ).pack(side=tk.LEFT)
                
                bar_canvas = tk.Canvas(row_frame, height=bar_height, width=350, bg=Colors.BG_WHITE, highlightthickness=0)
                bar_canvas.pack(side=tk.LEFT, padx=10)
                bar_canvas.create_rectangle(0, 0, bar_width, bar_height, fill=Colors.PRIMARY, tags="bar")
                
                tk.Label(
                    row_frame, 
                    text=str(count), 
                    width=5,
                    font=Fonts.SMALL,
                    bg=Colors.BG_WHITE,
                    fg=Colors.TEXT_GRAY
                ).pack(side=tk.LEFT)
        else:
            tk.Label(
                period_frame, 
                text="Нет данных за последние 7 дней.\nПройдите тесты, чтобы увидеть прогресс!",
                font=Fonts.BODY,
                bg=Colors.BG_WHITE,
                fg=Colors.TEXT_GRAY,
                justify=tk.CENTER
            ).pack(pady=30)
        
        # ===== СТАТИСТИКА ЗА СЕГОДНЯ =====
        daily_frame = tk.LabelFrame(
            self.scrollable_frame, 
            text="📅 Статистика за сегодня", 
            font=Fonts.SUBTITLE, 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        daily_frame.pack(fill=tk.X, padx=20, pady=10)

        daily_info = tk.Frame(daily_frame, bg=Colors.BG_WHITE)
        daily_info.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)

        daily_info.grid_columnconfigure(0, weight=1)
        daily_info.grid_columnconfigure(1, weight=1)

        correct_percent = today_stats['correct_percent']
        time_spent_minutes = today_stats.get('time_spent_minutes', today_stats['time_spent'])

        # ФОРМАТИРОВАНИЕ ВРЕМЕНИ БЕЗ ПОГРЕШНОСТЕЙ
        total_seconds = int(round(time_spent_minutes * 60))
        mins = total_seconds // 60
        secs = total_seconds % 60

        if mins > 0 and secs > 0:
            time_str = f"{mins} мин {secs} сек"
        elif mins > 0:
            time_str = f"{mins} мин"
        elif secs > 0:
            time_str = f"{secs} сек"
        else:
            time_str = "0 мин"

        daily_stats = [
            ("🎴 Изучено карточек:", f"{today_stats['cards_studied']}"),
            ("✓ Правильных ответов:", f"{correct_percent}%"),
            ("⏱ Время изучения:", time_str)
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
            
            # Цвет для процента правильных ответов
            if "Правильных ответов" in label:
                if correct_percent >= 80:
                    color = Colors.SUCCESS
                elif correct_percent >= 60:
                    color = Colors.INFO
                elif correct_percent >= 40:
                    color = Colors.WARNING
                else:
                    color = Colors.ERROR
            else:
                color = Colors.SUCCESS
            
            tk.Label(
                daily_info, 
                text=value, 
                font=Fonts.BODY_BOLD, 
                bg=Colors.BG_WHITE, 
                fg=color,
                anchor=tk.W
            ).grid(row=i, column=1, padx=20, pady=10, sticky="w")
        
        # Привязываем скролл ко всем созданным виджетам
        self._bind_mousewheel(self.scrollable_frame)
        
        # Нижний отступ
        tk.Frame(self.scrollable_frame, height=20, bg=Colors.BG_LIGHT).pack()
    
    def on_canvas_configure(self, event):
        """Обновление ширины при изменении canvas"""
        if event.width > 0 and hasattr(self, 'canvas'):
            try:
                self.canvas.itemconfig(1, width=event.width)
            except:
                pass

    def refresh(self):
        """Обновить данные на экране"""
        # Принудительно обновляем репозиторий статистики
        self.stats_repo.refresh()
        # Перезагружаем данные
        self.load_data()

    def on_resize(self, event):
        """Обновление при изменении размера"""
        pass