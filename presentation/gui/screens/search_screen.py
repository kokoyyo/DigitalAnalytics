import re
import tkinter as tk
from tkinter import ttk
from presentation.gui.styles import Colors, Fonts
from data.repositories import DeckRepository, CardRepository


class SearchScreen(tk.Frame):
    """Экран глобального поиска"""

    def __init__(self, parent):
        super().__init__(parent, bg=Colors.BG_LIGHT)
        self.parent = parent
        self.deck_repo = DeckRepository()
        self.card_repo = CardRepository()
        self._search_after_id = None
        self._ignore_trace = False
        self._current_message = None
        self._all_cards_frames = []  # Список всех карточек для обновления
        self.create_widgets()

    def create_widgets(self):
        header_frame = tk.Frame(self, bg=Colors.BG_WHITE)
        header_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            header_frame,
            text="🔍 Глобальный поиск",
            font=Fonts.TITLE,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_DARK
        ).pack(pady=10)

        search_frame = tk.Frame(header_frame, bg=Colors.BG_WHITE)
        search_frame.pack(fill=tk.X, padx=50, pady=10)

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_trace)

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=Fonts.BODY,
            bg=Colors.BG_LIGHT,
            relief=tk.FLAT,
            insertbackground=Colors.PRIMARY
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))

        clear_btn = tk.Button(
            search_frame,
            text="✕",
            command=self.clear_search,
            bg=Colors.TEXT_GRAY,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            padx=15,
            cursor="hand2",
            relief=tk.FLAT,
            activebackground=Colors.TEXT_GRAY,
            activeforeground=Colors.WHITE,
        )
        clear_btn.pack(side=tk.RIGHT)
        self.create_tooltip(clear_btn, "Очистить поиск")

        results_frame = tk.LabelFrame(
            self,
            text="Результаты поиска",
            font=Fonts.SUBTITLE,
            bg=Colors.BG_WHITE,
            fg=Colors.PRIMARY
        )
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Canvas для скролла
        self.canvas = tk.Canvas(results_frame, bg=Colors.BG_WHITE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.canvas.yview)
        self.results_container = tk.Frame(self.canvas, bg=Colors.BG_WHITE)

        self.canvas.create_window((0, 0), window=self.results_container, anchor="nw", tags="results_window")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self._mousewheel_handler = self._make_mousewheel_handler()
        self._bind_mousewheel(self.canvas)
        self._bind_mousewheel(self.results_container)

        # Показываем приветственное сообщение
        self.after(100, lambda: self._show_message("🔎 Введите слово или фразу\nдля поиска по колодам и карточкам"))

    # ── trace ──────────────────────────────────────────────────────────────

    def _on_trace(self, *args):
        if self._ignore_trace:
            return
        
        if self._search_after_id:
            self.after_cancel(self._search_after_id)
            self._search_after_id = None

        query = self.search_var.get().strip()
        
        if not query:
            self._show_message("🔎 Введите слово или фразу\nдля поиска по колодам и карточкам")
        else:
            self._search_after_id = self.after(250, self._perform_search)

    # ── clear ──────────────────────────────────────────────────────────────

    def clear_search(self):
        if self._search_after_id:
            self.after_cancel(self._search_after_id)
            self._search_after_id = None

        self._ignore_trace = True
        self.search_var.set("")
        self._ignore_trace = False

        self.search_entry.focus()
        self._show_message("🔎 Введите слово или фразу\nдля поиска по колодам и карточкам")

    # ── message helpers ────────────────────────────────────────────────────

    def _show_message(self, text):
        """Показывает сообщение по центру canvas"""
        self._current_message = text
        self._all_cards_frames.clear()
        
        # Очищаем контейнер результатов
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        # Отключаем скролл
        self.results_container.unbind("<Configure>")
        
        # Очищаем canvas и создаём окно для контейнера
        self.canvas.delete("all")
        self.canvas.create_window((0, 0), window=self.results_container, anchor="nw", tags="results_window")
        self.canvas.configure(scrollregion=(0, 0, 0, 0))
        self.canvas.yview_moveto(0)
        
        # Получаем размеры canvas
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Если canvas ещё не отрисован, ждём
        if w <= 10 or h <= 10:
            self.after(50, lambda: self._show_message(text))
            return
        
        # Рисуем текст
        self.canvas.create_text(
            w // 2, h // 2,
            text=text,
            font=("Segoe UI", 12),
            fill=Colors.TEXT_GRAY,
            justify=tk.CENTER,
            tags="message"
        )
        
        self.canvas.tag_lower("results_window")
        self.canvas.tag_raise("message")

    def _enable_scroll(self):
        """Включает скролл для результатов"""
        self._current_message = None
        
        # Очищаем canvas и создаём окно для контейнера
        self.canvas.delete("all")
        self.canvas.create_window((0, 0), window=self.results_container, anchor="nw", tags="results_window")
        
        # Включаем отслеживание скролла
        self.results_container.bind(
            "<Configure>",
            self._update_scrollregion
        )

    def _update_scrollregion(self, event=None):
        """Обновляет область прокрутки"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # ── canvas resize ──────────────────────────────────────────────────────

    def _on_canvas_configure(self, event):
        """Обновление при изменении размера canvas"""
        if event.width > 0:
            # Обновляем ширину окна с results_container
            self.canvas.itemconfig("results_window", width=event.width)
            
            # Если есть результаты, обновляем ширину всех карточек
            if not self._current_message and self._all_cards_frames:
                self._update_all_cards_width(event.width - 40)
        
        # Если показываем сообщение, перерисовываем его с новыми размерами
        if self._current_message:
            self._show_message(self._current_message)

    def _update_all_cards_width(self, width):
        """Обновляет ширину всех карточек"""
        if width < 100:
            return
        
        wrap_width = width - 80
        if wrap_width < 200:
            wrap_width = 700
        
        for frame in self._all_cards_frames:
            if hasattr(frame, 'example_label'):
                frame.example_label.config(wraplength=wrap_width)
            if hasattr(frame, 'desc_label'):
                frame.desc_label.config(wraplength=wrap_width)
        
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # ── search ─────────────────────────────────────────────────────────────

    def _perform_search(self):
        self._search_after_id = None
        query = self.search_var.get().strip().lower()

        if not query:
            self._show_message("🔎 Введите слово или фразу\nдля поиска по колодам и карточкам")
            return

        results = []
        decks = self.deck_repo.get_all()

        for deck in decks:
            if self._word_starts(deck.name, query) or (
                deck.description and self._word_starts(deck.description, query)
            ):
                results.append(('deck', deck))

        for deck in decks:
            for card in self.card_repo.get_by_deck(deck.id):
                if (card.word.lower().startswith(query)
                        or self._word_starts(card.translation, query)
                        or (card.transcription and self._word_starts(card.transcription, query))
                        or (card.example and self._word_starts(card.example, query))):
                    results.append(('card', card, deck))

        if not results:
            self._show_message(f"😕 По запросу «{query}» ничего не найдено")
            return

        # Показываем результаты
        self._enable_scroll()
        self._all_cards_frames.clear()

        # Очищаем контейнер
        for widget in self.results_container.winfo_children():
            widget.destroy()

        # ПРИНУДИТЕЛЬНО ОБНОВЛЯЕМ ГЕОМЕТРИЮ ДЛЯ ПОЛУЧЕНИЯ ПРАВИЛЬНОЙ ШИРИНЫ
        self.canvas.update_idletasks()
        self.update_idletasks()
        
        # Получаем ширину canvas (если еще маленькая, используем ширину корневого окна)
        canvas_width = self.canvas.winfo_width()
        if canvas_width < 100:
            # Получаем ширину корневого окна и вычитаем отступы
            root_width = self.winfo_toplevel().winfo_width()
            canvas_width = root_width - 80  # отступы
            if canvas_width < 100:
                canvas_width = 800
        
        # Устанавливаем ширину окна в canvas
        self.canvas.itemconfig("results_window", width=canvas_width)
        
        wrap_width = canvas_width - 80
        if wrap_width < 200:
            wrap_width = 700

        # Добавляем счётчик
        count_label = tk.Label(
            self.results_container,
            text=f"Найдено: {len(results)}",
            font=Fonts.BODY_BOLD,
            bg=Colors.BG_WHITE,
            fg=Colors.PRIMARY,
            anchor=tk.W
        )
        count_label.pack(fill=tk.X, padx=10, pady=(10, 5))
        self._bind_mousewheel(count_label)

        # Добавляем результаты с правильной шириной
        for result in results:
            if result[0] == 'deck':
                self.display_deck_result(result[1], wrap_width)
            else:
                self.display_card_result(result[1], result[2], wrap_width)
        
        # Обновляем область прокрутки
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # ── display methods ────────────────────────────────────────────────────

    def display_deck_result(self, deck, wrap_width):
        """Отображение результата - колода"""
        frame = tk.Frame(self.results_container, bg=Colors.BG_WHITE, relief=tk.RIDGE, bd=1)
        frame.pack(fill=tk.X, pady=5, padx=10)
        self._all_cards_frames.append(frame)

        tk.Label(frame, text="📚 КОЛОДА", font=("Segoe UI", 9, "bold"),
                bg=Colors.BG_WHITE, fg=Colors.PRIMARY).pack(anchor=tk.W, padx=10, pady=(5, 0))
        tk.Label(frame, text=deck.name, font=("Segoe UI", 12, "bold"),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_DARK).pack(anchor=tk.W, padx=10, pady=(0, 2))

        if deck.description:
            desc_label = tk.Label(
                frame, 
                text=deck.description, 
                font=Fonts.SMALL,
                bg=Colors.BG_WHITE, 
                fg=Colors.TEXT_GRAY,
                wraplength=wrap_width,
                justify=tk.LEFT
            )
            desc_label.pack(anchor=tk.W, padx=10, pady=(0, 5))
            frame.desc_label = desc_label

        self._bind_mousewheel(frame)
        self._make_clickable(frame, deck.id)

    def display_card_result(self, card, deck, wrap_width):
        """Отображение результата - карточка"""
        frame = tk.Frame(self.results_container, bg=Colors.BG_WHITE, relief=tk.RIDGE, bd=1)
        frame.pack(fill=tk.X, pady=5, padx=10)
        self._all_cards_frames.append(frame)

        status = "✅" if card.status == "studied" else "📝"
        tk.Label(
            frame, 
            text=f"{status} КАРТОЧКА  ·  Колода: {deck.name}",
            font=("Segoe UI", 9, "bold"), 
            bg=Colors.BG_WHITE,
            fg=Colors.SUCCESS if card.status == "studied" else Colors.INFO
        ).pack(anchor=tk.W, padx=10, pady=(5, 0))

        word_frame = tk.Frame(frame, bg=Colors.BG_WHITE)
        word_frame.pack(anchor=tk.W, padx=10, pady=(2, 2))
        tk.Label(word_frame, text=card.word, font=("Segoe UI", 11, "bold"),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_DARK).pack(side=tk.LEFT)
        tk.Label(word_frame, text=f" → {card.translation}", font=("Segoe UI", 11),
                bg=Colors.BG_WHITE, fg=Colors.PRIMARY).pack(side=tk.LEFT)

        if card.transcription:
            tk.Label(frame, text=f"[{card.transcription}]", font=("Segoe UI", 9, "italic"),
                    bg=Colors.BG_WHITE, fg=Colors.TEXT_GRAY).pack(anchor=tk.W, padx=10, pady=(0, 2))

        if card.example:
            example_label = tk.Label(
                frame, 
                text=f"📖 {card.example[:120]}", 
                font=("Segoe UI", 9),
                bg=Colors.BG_WHITE, 
                fg=Colors.TEXT_GRAY,
                wraplength=wrap_width,
                justify=tk.LEFT
            )
            example_label.pack(anchor=tk.W, padx=10, pady=(0, 5))
            frame.example_label = example_label

        self._bind_mousewheel(frame)
        self._make_clickable(frame, deck.id)

    # ── helpers ────────────────────────────────────────────────────────────

    def _make_mousewheel_handler(self):
        def handler(event):
            if self._current_message:
                return
            if hasattr(event, 'delta') and event.delta != 0:
                delta = -1 * (event.delta // 30)
            elif event.num == 4:
                delta = -3
            elif event.num == 5:
                delta = 3
            else:
                return
            self.canvas.yview_scroll(delta, "units")
        return handler

    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._mousewheel_handler, add="+")
        widget.bind("<Button-4>", self._mousewheel_handler, add="+")
        widget.bind("<Button-5>", self._mousewheel_handler, add="+")
        for child in widget.winfo_children():
            self._bind_mousewheel(child)

    @staticmethod
    def _word_starts(text, prefix):
        words = re.split(r'[\s/,;()]+', text.lower())
        return any(w.startswith(prefix) for w in words if w)

    def create_tooltip(self, widget, text):
        tip_ref = [None]
        after_id = [None]

        def show_tooltip(event):
            if after_id[0]:
                widget.after_cancel(after_id[0])
            def _create():
                if tip_ref[0] is not None:
                    return
                tip = tk.Toplevel(widget)
                tip.wm_overrideredirect(True)
                tip.wm_geometry(f"+{event.x_root + 15}+{event.y_root + 15}")
                tk.Label(tip, text=text, background="#FFFFE0", relief="solid",
                         borderwidth=1, font=("Segoe UI", 9)).pack()
                tip_ref[0] = tip
            after_id[0] = widget.after(600, _create)

        def hide_tooltip(event=None):
            if after_id[0]:
                widget.after_cancel(after_id[0])
                after_id[0] = None
            if tip_ref[0] is not None:
                tip_ref[0].destroy()
                tip_ref[0] = None

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    def _open_deck(self, deck_id):
        from presentation.gui.screens.deck_detail_screen import DeckDetailScreen
        current = self
        parent_container = None
        while current:
            if hasattr(current, 'content_container'):
                parent_container = current.content_container
                break
            current = current.master
        if not parent_container:
            parent_container = self.master
        for widget in parent_container.winfo_children():
            widget.destroy()
        DeckDetailScreen(parent_container, deck_id).pack(fill=tk.BOTH, expand=True)

    def _make_clickable(self, frame, deck_id):
        widgets = []
        stack = [frame]
        while stack:
            w = stack.pop()
            widgets.append(w)
            stack.extend(w.winfo_children())

        def on_enter(e=None):
            for w in widgets:
                try: w.config(bg=Colors.HOVER)
                except Exception: pass

        def on_leave(e=None):
            for w in widgets:
                try: w.config(bg=Colors.BG_WHITE)
                except Exception: pass

        def on_click(e=None):
            self._open_deck(deck_id)

        for w in widgets:
            w.config(cursor="hand2")
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)