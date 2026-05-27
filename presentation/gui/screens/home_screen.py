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
        
        # Верхняя строка с заголовком и кнопкой
        top_row = tk.Frame(self.header_frame, bg=Colors.BG_WHITE)
        top_row.pack(fill=tk.X)
        
        # Заголовок
        title_label = tk.Label(
            top_row,
            text="Мои колоды",
            font=Fonts.TITLE,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_DARK
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=(15, 0))
        
        # Кнопка добавления
        add_btn = tk.Button(
            top_row,
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
        
        # Блок статистики - с возможностью переноса текста
        self.stats_frame = tk.Frame(self.header_frame, bg=Colors.BG_WHITE)
        self.stats_frame.pack(fill=tk.X, padx=20, pady=(10, 10))

        self.stats_total_label = tk.Label(
            self.stats_frame,
            text="",
            font=Fonts.BODY,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_GRAY,
        )
        self.stats_total_label.pack(side=tk.LEFT)

        self.stats_studied_label = tk.Label(
            self.stats_frame,
            text="",
            font=Fonts.BODY,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_GRAY,
        )
        self.stats_studied_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Область для списка колод (остается без изменений)
        canvas_container = tk.Frame(self, bg=Colors.BG_LIGHT)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.canvas = tk.Canvas(canvas_container, bg=Colors.BG_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)

        self.decks_frame = tk.Frame(self.canvas, bg=Colors.BG_LIGHT)
        self.decks_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self._decks_window_id = self.canvas.create_window((0, 0), window=self.decks_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Универсальный обработчик скролла
        self._mousewheel_handler = self._make_mousewheel_handler()
        self._bind_mousewheel(self.canvas)
        self._bind_mousewheel(self.decks_frame)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
    
    def _make_mousewheel_handler(self):
        """Возвращает плавный обработчик скролла колесиком"""
        def handler(event):
            # Плавный скролл с ускорением
            if hasattr(event, 'delta') and event.delta != 0:
                # Для Windows: delta обычно 120
                delta = -1 * (event.delta // 30)
            elif event.num == 4:
                delta = -3
            elif event.num == 5:
                delta = 3
            else:
                return
            
            # Плавная прокрутка с анимацией
            current_pos = self.canvas.yview()[0]
            new_pos = current_pos + (delta / 100)
            new_pos = max(0, min(1, new_pos))
            self.canvas.yview_moveto(new_pos)
            
            # Принудительное обновление
            self.canvas.update_idletasks()
        return handler

    def _bind_mousewheel(self, widget):
        """Привязывает плавный скролл к виджету и всем его дочерним элементам"""
        handler = self._make_mousewheel_handler()
        widget.bind("<MouseWheel>", handler, add="+")
        widget.bind("<Button-4>", handler, add="+")
        widget.bind("<Button-5>", handler, add="+")
        for child in widget.winfo_children():
            self._bind_mousewheel(child)
    
    def _on_canvas_configure(self, event):
        """Обновление ширины контента при изменении размера canvas"""
        if event.width > 0:
            self.canvas.itemconfig(self._decks_window_id, width=event.width)
            self.update_deck_widths(event.width)
    
    def on_resize(self, event):
        if hasattr(self, 'canvas') and self.canvas.winfo_width() > 0:
            self.update_deck_widths(self.canvas.winfo_width())
            self.update_statistics()
        # Обновляем wraplength stats при ресайзе
        if hasattr(self, 'stats_frame'):
            w = self.stats_frame.winfo_width()
            if w > 0:
                self.stats_total_label.config(wraplength=w // 2)
                self.stats_studied_label.config(wraplength=w // 2)
    
    def update_deck_widths(self, width):
        if width > 0:
            for frame in self.deck_frames:
                if hasattr(frame, 'desc_label') and frame.desc_label:
                    frame.desc_label.config(wraplength=width - 80)
    
    def update_statistics(self):
        total_cards = 0
        studied_cards = 0

        for deck in self.decks:
            cards = self.card_repo.get_by_deck(deck.id)
            total_cards += len(cards)
            studied_cards += sum(1 for c in cards if c.status == 'studied')

        percent = (studied_cards / total_cards * 100) if total_cards > 0 else 0

        self.stats_total_label.config(text=f"📊 Всего карточек: {total_cards}")
        self.stats_studied_label.config(text=f"  |  ✅ Изучено: {studied_cards} ({percent:.0f}%)")
    
    def load_decks(self):
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
            self._bind_mousewheel(empty_label)
        else:
            for deck in self.decks:
                self.create_deck_card(deck)
        
        self.update_statistics()
        
        if hasattr(self, 'canvas') and self.canvas.winfo_width() > 0:
            self.update_deck_widths(self.canvas.winfo_width())
    
    def open_deck_by_id(self, deck_id):
        """Открыть колоду по ID"""
        print(f"open_deck_by_id ВЫЗВАН для ID: {deck_id}")
        
        deck = self.deck_repo.get_by_id(deck_id)
        if deck:
            self.open_deck(deck)
        else:
            print(f"Колода с ID {deck_id} не найдена!")

    def create_deck_card(self, deck):
        cards = self.card_repo.get_by_deck(deck.id)
        total_cards = len(cards)
        studied_cards = sum(1 for c in cards if c.status == 'studied')
        progress = (studied_cards / total_cards * 100) if total_cards > 0 else 0

        current_width = self.canvas.winfo_width() if hasattr(self, 'canvas') and self.canvas.winfo_width() > 0 else 800
        deck_id = deck.id

        card_frame = tk.Frame(
            self.decks_frame,
            bg=Colors.BG_WHITE,
            relief=tk.RAISED,
            bd=2,
            cursor="hand2"
        )
        card_frame.pack(fill=tk.X, pady=10, padx=5)
        self.deck_frames.append(card_frame)

        inner_frame = tk.Frame(card_frame, bg=Colors.BG_WHITE, cursor="hand2")
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

        top_frame = tk.Frame(inner_frame, bg=Colors.BG_WHITE, cursor="hand2")
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

        menu_btn = tk.Button(
            top_frame,
            text="⋮",
            font=("Segoe UI", 16),
            bg=Colors.BG_WHITE,
            activebackground=Colors.BG_WHITE,
            fg=Colors.TEXT_GRAY,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=lambda d=deck: self.show_context_menu(d)
        )
        menu_btn.pack(side=tk.RIGHT)

        desc_label = None
        if deck.description:
            desc_label = tk.Label(
                inner_frame,
                text=deck.description,
                font=("Segoe UI", 10),
                bg=Colors.BG_WHITE,
                fg=Colors.TEXT_GRAY,
                wraplength=current_width - 80,
                justify=tk.LEFT,
                cursor="hand2"
            )
            desc_label.pack(anchor=tk.W, pady=(0, 10))
            card_frame.desc_label = desc_label

        stats_progress_frame = tk.Frame(inner_frame, bg=Colors.BG_WHITE, cursor="hand2")
        stats_progress_frame.pack(fill=tk.X, pady=(0, 5))

        stats_label = tk.Label(
            stats_progress_frame,
            text=f"📝 {total_cards} карточек  |  ✅ {studied_cards} изучено",
            font=("Segoe UI", 10),
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_GRAY,
            cursor="hand2"
        )
        stats_label.pack(side=tk.LEFT)

        percent_label = tk.Label(
            stats_progress_frame,
            text=f"{progress:.0f}%",
            font=("Segoe UI", 11, "bold"),
            bg=Colors.BG_WHITE,
            fg=Colors.SUCCESS,
            cursor="hand2"
        )
        percent_label.pack(side=tk.RIGHT)

        progress_frame = tk.Frame(inner_frame, bg=Colors.BG_WHITE)
        progress_frame.pack(fill=tk.X)

        progress_bar = ttk.Progressbar(
            progress_frame,
            style="Success.Horizontal.TProgressbar",
            maximum=100,
            value=progress
        )
        progress_bar.pack(fill=tk.X, expand=True)

        # Привязываем скролл ко всем виджетам карточки
        self._bind_mousewheel(card_frame)
        
        # Виджеты, на которые вешаем клик и hover
        clickable = [card_frame, inner_frame, top_frame, name_label,
                     stats_progress_frame, stats_label, percent_label, progress_frame]
        if desc_label:
            clickable.append(desc_label)

        hover_bg_widgets = [w for w in clickable
                            if isinstance(w, (tk.Frame, tk.Label))]

        def open_deck(event=None):
            self.open_deck_by_id(deck_id)

        def on_enter(event=None):
            card_frame.config(relief=tk.RIDGE)
            for w in hover_bg_widgets:
                w.config(bg=Colors.HOVER)

        def on_leave(event=None):
            card_frame.config(relief=tk.RAISED)
            for w in hover_bg_widgets:
                w.config(bg=Colors.BG_WHITE)

        for w in clickable:
            w.bind("<Button-1>", open_deck)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
    
    def open_deck(self, deck):
        """Открыть колоду"""
        print(f"open_deck ВЫЗВАН для колоды: {deck.name} (ID: {deck.id})")
        
        from presentation.gui.screens.deck_detail_screen import DeckDetailScreen
        
        current = self
        parent_container = None
        while current:
            if hasattr(current, 'content_container'):
                parent_container = current.content_container
                print("Нашли content_container!")
                break
            current = current.master
        
        if not parent_container:
            print("Не нашли content_container, используем self.master")
            parent_container = self.master
        
        print(f"Очищаем контент")
        for widget in parent_container.winfo_children():
            widget.destroy()
        
        print(f"Создаем DeckDetailScreen")
        deck_screen = DeckDetailScreen(parent_container, deck.id)
        deck_screen.pack(fill=tk.BOTH, expand=True)
        print("DeckDetailScreen создан")
    
    def show_context_menu(self, deck):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="✏️ Редактировать", command=lambda: self.edit_deck(deck))
        menu.add_separator()
        menu.add_command(label="🗑️ Удалить", command=lambda: self.delete_deck(deck))
        menu.post(self.winfo_pointerx(), self.winfo_pointery())
    
    def add_deck(self):
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
    
    def update_progress_screen_stats(self):
        """Обновление статистики на экране прогресса"""
        root = self.winfo_toplevel()
        if hasattr(root, 'main_app'):
            main_app = root.main_app
            for widget in main_app.content_container.winfo_children():
                if hasattr(widget, 'load_data'):
                    widget.load_data()

    def delete_deck(self, deck):
        """Удаление колоды"""
        if messagebox.askyesno("Подтверждение", f"Вы действительно хотите удалить колоду '{deck.name}'?\nВсе карточки будут также удалены!"):
            self.deck_repo.delete(deck.id)
            self.load_decks()
            self.refresh_progress_screen()
            messagebox.showinfo("Успех", f"Колода '{deck.name}' удалена")

    def refresh_progress_screen(self):
        """Обновление экрана прогресса"""
        root = self.winfo_toplevel()
        if hasattr(root, 'main_app'):
            root.main_app.refresh_current_screen()

    def refresh(self):
        """Обновление главного экрана"""
        self.load_decks()
        self.update_statistics()

    def refresh_all_stats(self):
        """Обновление статистики на всех экранах"""
        root = self.winfo_toplevel()
        if hasattr(root, 'main_app'):
            main_app = root.main_app
            for widget in main_app.content_container.winfo_children():
                if hasattr(widget, 'load_data'):
                    widget.load_data()
                if hasattr(widget, 'refresh'):
                    widget.refresh()