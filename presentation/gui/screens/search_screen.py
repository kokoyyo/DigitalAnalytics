"""Экран глобального поиска"""

import tkinter as tk
from tkinter import ttk
from presentation.gui.styles import Colors, Fonts


class SearchScreen(tk.Frame):
    """Экран поиска"""
    
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
    
    def create_content(self, parent):
        """Создание содержимого экрана"""
        # Верхняя панель
        header_frame = tk.Frame(parent, bg=Colors.BG_WHITE)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text="🔍 Глобальный поиск",
            font=Fonts.TITLE,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_DARK
        ).pack(pady=20)
        
        # Строка поиска
        search_frame = tk.Frame(header_frame, bg=Colors.BG_WHITE)
        search_frame.pack(fill=tk.X, padx=50, pady=10)
        
        self.search_entry = tk.Entry(search_frame, font=Fonts.BODY, bg=Colors.BG_LIGHT, relief=tk.FLAT)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        
        search_btn = tk.Button(
            search_frame,
            text="🔍 Найти",
            command=self.search,
            bg=Colors.PRIMARY,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            padx=20,
            cursor="hand2"
        )
        search_btn.pack(side=tk.RIGHT)
        
        # Результаты поиска
        results_frame = tk.LabelFrame(
            parent, 
            text="Результаты поиска", 
            font=Fonts.SUBTITLE, 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.results_text = tk.Text(
            results_frame, 
            font=Fonts.BODY, 
            bg=Colors.BG_WHITE, 
            fg=Colors.TEXT_DARK, 
            wrap=tk.WORD, 
            padx=10, 
            pady=10
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(self.results_text, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text.insert("1.0", "🔎 Введите слово или фразу для поиска по колодам и карточкам")
        self.results_text.config(state=tk.DISABLED)
    
    def search(self):
        """Выполнение поиска"""
        query = self.search_entry.get().strip()
        if not query:
            return
        
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        
        # Здесь будет реальный поиск по БД
        results = [
            ("Колода: Английский A1", "Найдено 3 карточки", "apple - яблоко"),
            ("Колода: Бизнес английский", "Найдено 2 карточки", "meeting - встреча"),
            ("Колода: Неправильные глаголы", "Найдено 1 карточка", "go - went - gone")
        ]
        
        if results:
            for title, subtitle, content in results:
                self.results_text.insert(tk.END, f"📚 {title}\n", "title")
                self.results_text.insert(tk.END, f"   {subtitle}\n", "subtitle")
                self.results_text.insert(tk.END, f"   {content}\n\n", "content")
            
            self.results_text.tag_config("title", font=Fonts.BODY_BOLD, foreground=Colors.PRIMARY)
            self.results_text.tag_config("subtitle", font=Fonts.SMALL, foreground=Colors.TEXT_GRAY)
            self.results_text.tag_config("content", font=Fonts.BODY, foreground=Colors.TEXT_DARK)
        else:
            self.results_text.insert("1.0", f"😕 По запросу '{query}' ничего не найдено")
        
        self.results_text.config(state=tk.DISABLED)