"""Экран глобального поиска"""

import tkinter as tk
from tkinter import ttk, messagebox
from presentation.gui.styles import Colors, Fonts
from data.repositories import DeckRepository, CardRepository


class SearchScreen(tk.Frame):
    """Экран глобального поиска"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=Colors.BG_LIGHT)
        self.parent = parent
        self.deck_repo = DeckRepository()
        self.card_repo = CardRepository()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создание виджетов"""
        # Верхняя панель с поиском
        header_frame = tk.Frame(self, bg=Colors.BG_WHITE)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text="🔍 Глобальный поиск",
            font=Fonts.TITLE,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_DARK
        ).pack(pady=10)
        
        # Строка поиска
        search_frame = tk.Frame(header_frame, bg=Colors.BG_WHITE)
        search_frame.pack(fill=tk.X, padx=50, pady=10)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search())
        
        self.search_entry = tk.Entry(
            search_frame, 
            textvariable=self.search_var,
            font=Fonts.BODY, 
            bg=Colors.BG_LIGHT, 
            relief=tk.FLAT,
            insertbackground=Colors.PRIMARY
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))
        
        self.search_entry.bind('<KeyRelease>', lambda e: self.search())
        
        clear_btn = tk.Button(
            search_frame,
            text="✕",
            command=self.clear_search,
            bg=Colors.TEXT_GRAY,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            padx=15,
            cursor="hand2",
            relief=tk.FLAT
        )
        clear_btn.pack(side=tk.RIGHT)
        self.create_tooltip(clear_btn, "Очистить поиск")
        
        # Результаты поиска
        results_frame = tk.LabelFrame(
            self, 
            text="Результаты поиска", 
            font=Fonts.SUBTITLE, 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Canvas для прокрутки
        canvas = tk.Canvas(results_frame, bg=Colors.BG_WHITE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        self.results_container = tk.Frame(canvas, bg=Colors.BG_WHITE)
        
        self.results_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.results_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        self.results_container.bind("<MouseWheel>", _on_mousewheel)
        
        self.canvas = canvas
        
        # Начальное сообщение
        self.show_initial_message()
    
    def create_tooltip(self, widget, text):
        """Создание всплывающей подсказки"""
        def show_tooltip(event):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background="#FFFFE0", relief="solid", borderwidth=1, font=("Segoe UI", 9))
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind("<Leave>", lambda e: hide_tooltip())
        
        widget.bind("<Enter>", show_tooltip)
    
    def show_initial_message(self):
        """Показать начальное сообщение"""
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        msg_label = tk.Label(
            self.results_container,
            text="🔎 Введите слово или фразу для поиска по колодам и карточкам",
            font=("Segoe UI", 12),
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_GRAY,
            justify=tk.CENTER
        )
        msg_label.pack(expand=True, pady=100)
    
    def clear_search(self):
        """Очистить поиск"""
        self.search_var.set("")
        self.search_entry.focus()
        self.show_initial_message()
    
    def search(self):
        """Выполнение поиска"""
        query = self.search_var.get().strip().lower()
        
        if not query:
            self.show_initial_message()
            return
        
        # Очищаем результаты
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        results = []
        
        # Поиск по колодам
        decks = self.deck_repo.get_all()
        for deck in decks:
            if query in deck.name.lower() or (deck.description and query in deck.description.lower()):
                results.append(('deck', deck))
        
        # Поиск по карточкам
        for deck in decks:
            cards = self.card_repo.get_by_deck(deck.id)
            for card in cards:
                if (query in card.word.lower() or 
                    query in card.translation.lower() or
                    (card.example and query in card.example.lower())):
                    results.append(('card', card, deck))
        
        if not results:
            no_results = tk.Label(
                self.results_container,
                text=f"😕 По запросу '{query}' ничего не найдено",
                font=("Segoe UI", 12),
                bg=Colors.BG_WHITE,
                fg=Colors.TEXT_GRAY,
                justify=tk.CENTER
            )
            no_results.pack(expand=True, pady=100)
            return
        
        # Заголовок с количеством результатов
        count_label = tk.Label(
            self.results_container,
            text=f"Найдено {len(results)} результатов",
            font=Fonts.BODY_BOLD,
            bg=Colors.BG_WHITE,
            fg=Colors.PRIMARY,
            anchor=tk.W
        )
        count_label.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Отображаем результаты
        for result in results:
            if result[0] == 'deck':
                self.display_deck_result(result[1])
            else:
                self.display_card_result(result[1], result[2])
    
    def display_deck_result(self, deck):
        """Отображение результата - колода"""
        frame = tk.Frame(self.results_container, bg=Colors.BG_WHITE, relief=tk.RIDGE, bd=1)
        frame.pack(fill=tk.X, pady=5, padx=10)
        
        tk.Label(
            frame,
            text="📚 КОЛОДА",
            font=("Segoe UI", 9, "bold"),
            bg=Colors.BG_WHITE,
            fg=Colors.PRIMARY
        ).pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        tk.Label(
            frame,
            text=deck.name,
            font=("Segoe UI", 12, "bold"),
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_DARK
        ).pack(anchor=tk.W, padx=10, pady=(0, 2))
        
        if deck.description:
            tk.Label(
                frame,
                text=deck.description,
                font=Fonts.SMALL,
                bg=Colors.BG_WHITE,
                fg=Colors.TEXT_GRAY
            ).pack(anchor=tk.W, padx=10, pady=(0, 5))
    
    def display_card_result(self, card, deck):
        """Отображение результата - карточка"""
        frame = tk.Frame(self.results_container, bg=Colors.BG_WHITE, relief=tk.RIDGE, bd=1)
        frame.pack(fill=tk.X, pady=5, padx=10)
        
        status = "✅" if card.status == "studied" else "📝"
        
        tk.Label(
            frame,
            text=f"{status} КАРТОЧКА",
            font=("Segoe UI", 9, "bold"),
            bg=Colors.BG_WHITE,
            fg=Colors.SUCCESS if card.status == "studied" else Colors.INFO
        ).pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        tk.Label(
            frame,
            text=f"Колода: {deck.name}",
            font=("Segoe UI", 9),
            bg=Colors.BG_WHITE,
            fg=Colors.PRIMARY
        ).pack(anchor=tk.W, padx=10, pady=(0, 2))
        
        word_frame = tk.Frame(frame, bg=Colors.BG_WHITE)
        word_frame.pack(anchor=tk.W, padx=10, pady=(0, 2))
        
        tk.Label(
            word_frame,
            text=f"{card.word}",
            font=("Segoe UI", 11, "bold"),
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_DARK
        ).pack(side=tk.LEFT)
        
        tk.Label(
            word_frame,
            text=f" → {card.translation}",
            font=("Segoe UI", 11),
            bg=Colors.BG_WHITE,
            fg=Colors.PRIMARY
        ).pack(side=tk.LEFT)
        
        if card.transcription:
            tk.Label(
                frame,
                text=f"[{card.transcription}]",
                font=("Segoe UI", 9, "italic"),
                bg=Colors.BG_WHITE,
                fg=Colors.TEXT_GRAY
            ).pack(anchor=tk.W, padx=10, pady=(0, 2))
        
        if card.example:
            tk.Label(
                frame,
                text=f"📖 {card.example[:100]}",
                font=("Segoe UI", 9),
                bg=Colors.BG_WHITE,
                fg=Colors.TEXT_GRAY,
                wraplength=700,
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=10, pady=(0, 5))