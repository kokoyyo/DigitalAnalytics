"""Экран глобального поиска"""

import re
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
        self._search_after_id = None
        self.search_var.trace('w', lambda *args: self._schedule_search())

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
        self.show_initial_message()

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

    @staticmethod
    def _word_starts(text, prefix):
        """Возвращает True если хотя бы одно слово в тексте начинается с prefix"""
        words = re.split(r'[\s/,;()]+', text.lower())
        return any(w.startswith(prefix) for w in words if w)

    def show_initial_message(self):
        for widget in self.results_container.winfo_children():
            widget.destroy()

        tk.Label(
            self.results_container,
            text="🔎 Введите слово или фразу для поиска по колодам и карточкам",
            font=("Segoe UI", 12),
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_GRAY,
            justify=tk.CENTER
        ).pack(expand=True, pady=100)

    def _schedule_search(self):
        if self._search_after_id:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(250, self.search)

    def clear_search(self):
        self.search_var.set("")
        self.search_entry.focus()
        self.show_initial_message()

    def search(self):
        self._search_after_id = None
        query = self.search_var.get().strip().lower()

        if not query:
            self.show_initial_message()
            return

        for widget in self.results_container.winfo_children():
            widget.destroy()

        results = []
        decks = self.deck_repo.get_all()

        for deck in decks:
            name_match = self._word_starts(deck.name, query)
            desc_match = deck.description and self._word_starts(deck.description, query)
            if name_match or desc_match:
                results.append(('deck', deck))

        for deck in decks:
            cards = self.card_repo.get_by_deck(deck.id)
            for card in cards:
                word_match    = card.word.lower().startswith(query)
                trans_match   = (len(query) >= 2
                                 and self._word_starts(card.translation, query))
                transcr_match = (len(query) >= 2 and card.transcription
                                 and self._word_starts(card.transcription, query))
                example_match = (len(query) >= 3 and card.example
                                 and self._word_starts(card.example, query))
                if word_match or trans_match or transcr_match or example_match:
                    results.append(('card', card, deck))

        if not results:
            tk.Label(
                self.results_container,
                text=f"😕 По запросу «{query}» ничего не найдено",
                font=("Segoe UI", 12),
                bg=Colors.BG_WHITE,
                fg=Colors.TEXT_GRAY,
                justify=tk.CENTER
            ).pack(expand=True, pady=100)
            return

        tk.Label(
            self.results_container,
            text=f"Найдено: {len(results)}",
            font=Fonts.BODY_BOLD,
            bg=Colors.BG_WHITE,
            fg=Colors.PRIMARY,
            anchor=tk.W
        ).pack(fill=tk.X, padx=10, pady=(10, 5))

        for result in results:
            if result[0] == 'deck':
                self.display_deck_result(result[1])
            else:
                self.display_card_result(result[1], result[2])

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
                try:
                    w.config(bg=Colors.HOVER)
                except Exception:
                    pass

        def on_leave(e=None):
            for w in widgets:
                try:
                    w.config(bg=Colors.BG_WHITE)
                except Exception:
                    pass

        def on_click(e=None):
            self._open_deck(deck_id)

        for w in widgets:
            w.config(cursor="hand2")
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

    def display_deck_result(self, deck):
        frame = tk.Frame(self.results_container, bg=Colors.BG_WHITE, relief=tk.RIDGE, bd=1)
        frame.pack(fill=tk.X, pady=5, padx=10)

        tk.Label(frame, text="📚 КОЛОДА", font=("Segoe UI", 9, "bold"),
                 bg=Colors.BG_WHITE, fg=Colors.PRIMARY).pack(anchor=tk.W, padx=10, pady=(5, 0))

        tk.Label(frame, text=deck.name, font=("Segoe UI", 12, "bold"),
                 bg=Colors.BG_WHITE, fg=Colors.TEXT_DARK).pack(anchor=tk.W, padx=10, pady=(0, 2))

        if deck.description:
            tk.Label(frame, text=deck.description, font=Fonts.SMALL,
                     bg=Colors.BG_WHITE, fg=Colors.TEXT_GRAY).pack(anchor=tk.W, padx=10, pady=(0, 5))

        frame.update_idletasks()
        self._make_clickable(frame, deck.id)

    def display_card_result(self, card, deck):
        frame = tk.Frame(self.results_container, bg=Colors.BG_WHITE, relief=tk.RIDGE, bd=1)
        frame.pack(fill=tk.X, pady=5, padx=10)

        status = "✅" if card.status == "studied" else "📝"
        tk.Label(frame, text=f"{status} КАРТОЧКА  ·  Колода: {deck.name}",
                 font=("Segoe UI", 9, "bold"), bg=Colors.BG_WHITE,
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
            tk.Label(frame, text=f"📖 {card.example[:120]}", font=("Segoe UI", 9),
                     bg=Colors.BG_WHITE, fg=Colors.TEXT_GRAY,
                     wraplength=700, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=(0, 5))

        frame.update_idletasks()
        self._make_clickable(frame, deck.id)
