"""Главный экран с колодами"""

import tkinter as tk
from tkinter import ttk, messagebox
from presentation.gui.styles import Colors, Fonts
from data.repositories import DeckRepository, CardRepository


class HomeScreen(tk.Frame):
    """Главный экран с колодами"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=Colors.BG_LIGHT)
        self.parent = parent
        self.deck_repo = DeckRepository()
        self.card_repo = CardRepository()
        self.decks = []
        self.deck_frames = []
        
        self.create_widgets()
        self.load_decks()
        self.bind("<Configure>", self.on_resize)
    
    def create_widgets(self):
        """Создание виджетов"""
        # Верхняя панель
        self.header_frame = tk.Frame(self, bg=Colors.BG_WHITE)
        self.header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Заголовок
        title_label = tk.Label(
            self.header_frame,
            text="Мои колоды",
            font=Fonts.TITLE,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_DARK
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=(15, 0))
        
        # Кнопка добавления
        add_btn = tk.Button(
            self.header_frame,
            text="+ Добавить колоду",
            command=self.add_deck,
            bg=Colors.PRIMARY,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8
        )
        add_btn.pack(side=tk.RIGHT, padx=20, pady=(10, 0))
        
        # Блок статистики
        self.stats_frame = tk.Frame(self.header_frame, bg=Colors.BG_WHITE)
        self.stats_frame.pack(fill=tk.X, padx=20, pady=(60, 10))
        
        self.stats_label = tk.Label(
            self.stats_frame,
            text="",
            font=Fonts.BODY,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_GRAY
        )
        self.stats_label.pack()
        
        # Область для списка колод
        canvas_container = tk.Frame(self, bg=Colors.BG_LIGHT)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.canvas = tk.Canvas(canvas_container, bg=Colors.BG_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        
        self.decks_frame = tk.Frame(self.canvas, bg=Colors.BG_LIGHT)
        self.decks_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.decks_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.decks_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
    
    def _on_canvas_configure(self, event):
        """Обновление ширины контента при изменении размера canvas"""
        self.canvas.itemconfig(1, width=event.width)
        self.update_deck_widths(event.width)
    
    def _on_mousewheel(self, event):
        """Прокрутка колесиком мыши"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_resize(self, event):
        """Обработчик изменения размера окна"""
        if hasattr(self, 'canvas') and self.canvas.winfo_width() > 0:
            self.update_deck_widths(self.canvas.winfo_width())
    
    def update_deck_widths(self, width):
        """Обновление ширины всех карточек колод"""
        if width > 0:
            for frame in self.deck_frames:
                if hasattr(frame, 'desc_label') and frame.desc_label:
                    frame.desc_label.config(wraplength=width - 80)
    
    def update_statistics(self):
        """Обновление статистики"""
        total_cards = 0
        studied_cards = 0
        
        for deck in self.decks:
            cards = self.card_repo.get_by_deck(deck.id)
            total_cards += len(cards)
            studied_cards += sum(1 for c in cards if c.status == 'studied')
        
        percent = (studied_cards / total_cards * 100) if total_cards > 0 else 0
        
        self.stats_label.config(
            text=f"📊 Всего карточек: {total_cards}  |  Изучено: {studied_cards} ({percent:.0f}%)"
        )
    
    def load_decks(self):
        """Загрузка колод из БД"""
        for widget in self.decks_frame.winfo_children():
            widget.destroy()
        
        self.deck_frames.clear()
        self.decks = self.deck_repo.get_all()
        
        if not self.decks:
            empty_label = tk.Label(
                self.decks_frame,
                text="📭 У вас пока нет колод.\n\nНажмите кнопку '+ Добавить колоду' чтобы создать первую колоду",
                font=("Segoe UI", 14),
                bg=Colors.BG_LIGHT,
                fg=Colors.TEXT_GRAY,
                justify=tk.CENTER
            )
            empty_label.pack(expand=True, pady=100)
        else:
            for deck in self.decks:
                self.create_deck_card(deck)
        
        self.update_statistics()
        
        if hasattr(self, 'canvas') and self.canvas.winfo_width() > 0:
            self.update_deck_widths(self.canvas.winfo_width())
    
    def create_deck_card(self, deck):
        """Создание карточки колоды"""
        cards = self.card_repo.get_by_deck(deck.id)
        total_cards = len(cards)
        studied_cards = sum(1 for c in cards if c.status == 'studied')
        progress = (studied_cards / total_cards * 100) if total_cards > 0 else 0
        
        current_width = self.canvas.winfo_width() if hasattr(self, 'canvas') and self.canvas.winfo_width() > 0 else 800
        
        card_frame = tk.Frame(
            self.decks_frame,
            bg=Colors.BG_WHITE,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        card_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Привязываем событие клика на всю карточку
        card_frame.bind("<Button-1>", lambda e, d=deck: self.open_deck(d))
        
        self.deck_frames.append(card_frame)
        
        inner_frame = tk.Frame(card_frame, bg=Colors.BG_WHITE)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        # Верхняя строка
        top_frame = tk.Frame(inner_frame, bg=Colors.BG_WHITE)
        top_frame.pack(fill=tk.X, pady=(0, 8))
        
        name_label = tk.Label(
            top_frame,
            text=deck.name,
            font=("Segoe UI", 16, "bold"),
            bg=Colors.BG_WHITE,
            fg=Colors.PRIMARY,
            cursor="hand2"
        )
        name_label.pack(side=tk.LEFT)
        name_label.bind("<Button-1>", lambda e, d=deck: self.open_deck(d))
        
        menu_btn = tk.Button(
            top_frame,
            text="⋮",
            font=("Segoe UI", 16),
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_GRAY,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda d=deck: self.show_context_menu(d)
        )
        menu_btn.pack(side=tk.RIGHT)
        
        # Описание
        if deck.description:
            desc_label = tk.Label(
                inner_frame,
                text=deck.description,
                font=("Segoe UI", 10),
                bg=Colors.BG_WHITE,
                fg=Colors.TEXT_GRAY,
                wraplength=current_width - 80,
                justify=tk.LEFT
            )
            desc_label.pack(anchor=tk.W, pady=(0, 10))
            card_frame.desc_label = desc_label
        else:
            card_frame.desc_label = None
        
        # Статистика
        stats_progress_frame = tk.Frame(inner_frame, bg=Colors.BG_WHITE)
        stats_progress_frame.pack(fill=tk.X, pady=(0, 5))
        
        stats_text = f"📝 {total_cards} карточек  |  ✅ {studied_cards} изучено"
        stats_label = tk.Label(
            stats_progress_frame,
            text=stats_text,
            font=("Segoe UI", 10),
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_GRAY
        )
        stats_label.pack(side=tk.LEFT)
        
        percent_label = tk.Label(
            stats_progress_frame,
            text=f"{progress:.0f}%",
            font=("Segoe UI", 11, "bold"),
            bg=Colors.BG_WHITE,
            fg=Colors.SUCCESS
        )
        percent_label.pack(side=tk.RIGHT)
        
        # Прогресс-бар
        progress_frame = tk.Frame(inner_frame, bg=Colors.BG_WHITE)
        progress_frame.pack(fill=tk.X)
        
        progress_bar = ttk.Progressbar(
            progress_frame,
            style="Success.Horizontal.TProgressbar",
            maximum=100,
            value=progress
        )
        progress_bar.pack(fill=tk.X, expand=True)
        
        card_frame.current_width = current_width
    
    def open_deck(self, deck):
        """Открыть колоду - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        from presentation.gui.screens.deck_detail_screen import DeckDetailScreen
        
        # Находим MainApplication через родительскую иерархию
        main_app = self.master
        
        # Проверяем, что main_app имеет content_container
        while not hasattr(main_app, 'content_container') and main_app != self.winfo_toplevel():
            main_app = main_app.master
        
        if hasattr(main_app, 'content_container'):
            # Очищаем контент
            for widget in main_app.content_container.winfo_children():
                widget.destroy()
            
            # Создаем экран деталей колоды
            deck_screen = DeckDetailScreen(main_app.content_container, deck.id)
            deck_screen.pack(fill=tk.BOTH, expand=True)
    
    def show_context_menu(self, deck):
        """Показать контекстное меню"""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="✏️ Редактировать", command=lambda: self.edit_deck(deck))
        menu.add_separator()
        menu.add_command(label="🗑️ Удалить", command=lambda: self.delete_deck(deck))
        menu.post(self.winfo_pointerx(), self.winfo_pointery())
    
    def add_deck(self):
        """Добавить новую колоду"""
        dialog = tk.Toplevel(self)
        dialog.title("Создание новой колоды")
        dialog.geometry("450x350")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Название колоды:", font=Fonts.BODY).pack(pady=(20, 5), padx=20, anchor=tk.W)
        name_entry = tk.Entry(dialog, font=Fonts.BODY, width=45)
        name_entry.pack(padx=20, pady=5, fill=tk.X)
        
        tk.Label(dialog, text="Описание:", font=Fonts.BODY).pack(pady=(10, 5), padx=20, anchor=tk.W)
        desc_text = tk.Text(dialog, height=6, font=Fonts.BODY, width=45)
        desc_text.pack(padx=20, pady=5, fill=tk.X)
        
        btn_frame = tk.Frame(dialog, bg=Colors.BG_LIGHT)
        btn_frame.pack(pady=20)
        
        def save():
            name = name_entry.get().strip()
            if name:
                description = desc_text.get("1.0", tk.END).strip()
                self.deck_repo.create(name, description)
                dialog.destroy()
                self.load_decks()
                messagebox.showinfo("Успех", f"Колода '{name}' создана!")
            else:
                messagebox.showwarning("Внимание", "Введите название колоды")
        
        tk.Button(btn_frame, text="Создать", command=save, bg=Colors.PRIMARY, fg=Colors.WHITE, padx=25, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, padx=25, pady=5).pack(side=tk.LEFT, padx=5)
    
    def edit_deck(self, deck):
        """Редактирование колоды"""
        dialog = tk.Toplevel(self)
        dialog.title("Редактирование колоды")
        dialog.geometry("450x350")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        tk.Label(dialog, text="Название колоды:", font=Fonts.BODY).pack(pady=(20, 5), padx=20, anchor=tk.W)
        name_entry = tk.Entry(dialog, font=Fonts.BODY, width=45)
        name_entry.insert(0, deck.name)
        name_entry.pack(padx=20, pady=5, fill=tk.X)
        
        tk.Label(dialog, text="Описание:", font=Fonts.BODY).pack(pady=(10, 5), padx=20, anchor=tk.W)
        desc_text = tk.Text(dialog, height=6, font=Fonts.BODY, width=45)
        desc_text.insert("1.0", deck.description)
        desc_text.pack(padx=20, pady=5, fill=tk.X)
        
        btn_frame = tk.Frame(dialog, bg=Colors.BG_LIGHT)
        btn_frame.pack(pady=20)
        
        def save():
            name = name_entry.get().strip()
            if name:
                description = desc_text.get("1.0", tk.END).strip()
                self.deck_repo.update(deck.id, name, description)
                dialog.destroy()
                self.load_decks()
                messagebox.showinfo("Успех", f"Колода '{name}' обновлена!")
            else:
                messagebox.showwarning("Внимание", "Введите название колоды")
        
        tk.Button(btn_frame, text="Сохранить", command=save, bg=Colors.PRIMARY, fg=Colors.WHITE, padx=25, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, padx=25, pady=5).pack(side=tk.LEFT, padx=5)
    
    def delete_deck(self, deck):
        """Удаление колоды"""
        if messagebox.askyesno("Подтверждение", f"Вы действительно хотите удалить колоду '{deck.name}'?\nВсе карточки будут также удалены!"):
            self.deck_repo.delete(deck.id)
            self.load_decks()
            messagebox.showinfo("Успех", f"Колода '{deck.name}' удалена")