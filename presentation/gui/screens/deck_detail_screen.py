"""Экран просмотра и редактирования колоды"""

import tkinter as tk
from tkinter import ttk, messagebox
from presentation.gui.styles import Colors, Fonts
from data.repositories import DeckRepository, CardRepository


class DeckDetailScreen(tk.Frame):
    """Экран с деталями колоды"""
    
    def __init__(self, parent, deck_id):
        super().__init__(parent, bg=Colors.BG_LIGHT)
        self.deck_id = deck_id
        self.deck_repo = DeckRepository()
        self.card_repo = CardRepository()
        self.deck = self.deck_repo.get_by_id(deck_id)
        self.current_filter = "all"
        self.cards = []
        self.card_frames = []
        
        self.create_widgets()
        self.load_cards()
        
        # Привязываем событие изменения размера
        self.bind("<Configure>", self.on_resize)
    
    def on_resize(self, event):
        """Обновление при изменении размера"""
        if hasattr(self, 'empty_label') and self.empty_label:
            self.center_empty_message()
        else:
            self.update_cards_width()
    
    def center_empty_message(self):
        """Центрирование сообщения об отсутствии карточек"""
        if hasattr(self, 'empty_label') and self.empty_label:
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def update_cards_width(self):
        """Обновление ширины карточек"""
        if hasattr(self, 'canvas') and self.canvas.winfo_width() > 0:
            new_width = self.canvas.winfo_width() - 30
            for card_frame in self.card_frames:
                try:
                    card_frame.config(width=new_width)
                    for child in card_frame.winfo_children():
                        if hasattr(child, 'example_label'):
                            child.example_label.config(wraplength=new_width - 60)
                except:
                    pass
    
    
    def create_widgets(self):
        """Создание виджетов"""
        # Верхняя панель с использованием Frame и pack для лучшего контроля
        header_frame = tk.Frame(self, bg=Colors.BG_WHITE)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Верхняя строка с названием и кнопками
        top_row = tk.Frame(header_frame, bg=Colors.BG_WHITE)
        top_row.pack(fill=tk.X, pady=(10, 5))
        
        # Название колоды (слева)
        self.name_label = tk.Label(
            top_row,
            text=self.deck.name,
            font=Fonts.TITLE,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_DARK
        )
        self.name_label.pack(side=tk.LEFT, padx=20)
        
        # Фрейм для кнопок (справа)
        btn_frame = tk.Frame(top_row, bg=Colors.BG_WHITE)
        btn_frame.pack(side=tk.RIGHT, padx=20)
        
        # Кнопки действий
        test_btn = tk.Button(
            btn_frame,
            text="📝 Тест",
            command=self.start_test,
            bg=Colors.SECONDARY,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        test_btn.pack(side=tk.LEFT, padx=3)
        self.create_tooltip(test_btn, "Начать тестирование по колоде")
        
        edit_btn = tk.Button(
            btn_frame,
            text="✏️ Редактировать",
            command=self.edit_deck,
            bg=Colors.INFO,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        edit_btn.pack(side=tk.LEFT, padx=3)
        self.create_tooltip(edit_btn, "Редактировать название и описание колоды")
        
        delete_btn = tk.Button(
            btn_frame,
            text="🗑️ Удалить",
            command=self.delete_deck,
            bg=Colors.ERROR,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        delete_btn.pack(side=tk.LEFT, padx=3)
        self.create_tooltip(delete_btn, "Удалить колоду и все карточки")
        
        back_btn = tk.Button(
            btn_frame,
            text="← Назад",
            command=self.go_back,
            bg=Colors.TEXT_GRAY,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        back_btn.pack(side=tk.LEFT, padx=3)
        self.create_tooltip(back_btn, "Вернуться к списку колод")
        
        # Добавляем разделительную линию
        separator = tk.Frame(header_frame, bg=Colors.BORDER, height=2)
        separator.pack(fill=tk.X, pady=(10, 5))
        
        # Фильтры
        filters_frame = tk.Frame(self, bg=Colors.BG_LIGHT)
        filters_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(filters_frame, text="Фильтр:", font=Fonts.BODY, bg=Colors.BG_LIGHT).pack(side=tk.LEFT)
        
        self.filter_var = tk.StringVar(value="all")
        filters = [("📚 Все", "all"), ("✅ Изученные", "studied"), ("⭕ Неизученные", "not_studied")]
        
        for text, value in filters:
            rb = tk.Radiobutton(
                filters_frame,
                text=text,
                variable=self.filter_var,
                value=value,
                command=self.apply_filter,
                bg=Colors.BG_LIGHT,
                font=Fonts.BODY
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Список карточек
        cards_frame = tk.LabelFrame(self, text="Карточки", font=Fonts.SUBTITLE, bg=Colors.BG_WHITE, fg=Colors.PRIMARY)
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Canvas для скроллинга
        self.canvas = tk.Canvas(cards_frame, bg=Colors.BG_WHITE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(cards_frame, orient="vertical", command=self.canvas.yview)
        self.cards_container = tk.Frame(self.canvas, bg=Colors.BG_WHITE)
        
        self.cards_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.cards_container, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
    # Привязываем колесико мыши
    def _on_mousewheel(event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    self.canvas.bind("<MouseWheel>", _on_mousewheel)
    self.cards_container.bind("<MouseWheel>", _on_mousewheel)
    self.canvas.bind("<Configure>", self.on_canvas_configure)
    
    # Кнопка добавления карточки
    add_btn = tk.Button(
        self,
        text="+ Добавить карточку",
        command=self.add_card,
        bg=Colors.PRIMARY,
        fg=Colors.WHITE,
        font=Fonts.BUTTON,
        padx=20,
        pady=10,
        cursor="hand2"
    )
    add_btn.pack(side=tk.BOTTOM, pady=20)
    self.create_tooltip(add_btn, "Добавить новую карточку в колоду")


    def on_canvas_configure(self, event):
        """Обновление ширины при изменении canvas"""
        if event.width > 0:
            self.canvas.itemconfig(1, width=event.width)
            self.update_cards_width()
    
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
    
    def load_cards(self):
        """Загрузка карточек с фильтром"""
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        
        self.card_frames.clear()
        self.cards = self.card_repo.get_by_deck(self.deck_id, self.current_filter)
        
        if not self.cards:
            self.empty_label = tk.Label(
                self.cards_container,
                text="📭 Нет карточек в этой колоде.\n\nНажмите кнопку '+ Добавить карточку'\nчтобы создать первую карточку",
                font=("Segoe UI", 12),
                bg=Colors.BG_WHITE,
                fg=Colors.TEXT_GRAY,
                justify=tk.CENTER
            )
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.empty_label = None
            for card in self.cards:
                self.create_card_item(card)
    
    def create_card_item(self, card):
        """Создание элемента карточки"""
        current_width = self.canvas.winfo_width() if self.canvas.winfo_width() > 0 else 800
        
        card_frame = tk.Frame(
            self.cards_container, 
            bg=Colors.BG_WHITE, 
            relief=tk.RIDGE, 
            bd=1
        )
        card_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.card_frames.append(card_frame)
        
        inner_frame = tk.Frame(card_frame, bg=Colors.BG_WHITE)
        inner_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Слово и перевод
        word_frame = tk.Frame(inner_frame, bg=Colors.BG_WHITE)
        word_frame.pack(fill=tk.X, pady=(0, 5))
        
        word_label = tk.Label(
            word_frame, 
            text=card.word, 
            font=("Segoe UI", 14, "bold"), 
            bg=Colors.BG_WHITE, 
            fg=Colors.TEXT_DARK
        )
        word_label.pack(side=tk.LEFT)
        
        translation_text = f"→ {card.translation}"
        trans_label = tk.Label(
            word_frame, 
            text=translation_text, 
            font=("Segoe UI", 12), 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        trans_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Статус
        status_icon = "✅" if card.status == "studied" else "⭕"
        status_text = "Изучено" if card.status == "studied" else "Не изучено"
        
        status_frame = tk.Frame(word_frame, bg=Colors.BG_WHITE)
        status_frame.pack(side=tk.RIGHT)
        
        status_label = tk.Label(
            status_frame, 
            text=status_icon, 
            font=("Segoe UI", 12), 
            bg=Colors.BG_WHITE, 
            fg=Colors.SUCCESS if card.status == "studied" else Colors.TEXT_GRAY
        )
        status_label.pack(side=tk.LEFT)
        
        status_text_label = tk.Label(
            status_frame,
            text=status_text,
            font=("Segoe UI", 9),
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_GRAY
        )
        status_text_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Транскрипция
        if card.transcription:
            transcr_label = tk.Label(
                inner_frame,
                text=f"[{card.transcription}]",
                font=("Segoe UI", 10, "italic"),
                bg=Colors.BG_WHITE,
                fg=Colors.TEXT_GRAY
            )
            transcr_label.pack(anchor=tk.W, pady=(0, 3))
        
        # Пример
        if card.example:
            example_label = tk.Label(
                inner_frame,
                text=f"📖 Пример: {card.example}",
                font=("Segoe UI", 9),
                bg=Colors.BG_WHITE,
                fg=Colors.TEXT_GRAY,
                wraplength=current_width - 60,
                justify=tk.LEFT
            )
            example_label.pack(anchor=tk.W)
            inner_frame.example_label = example_label
        
        # Кнопки действий
        actions_frame = tk.Frame(inner_frame, bg=Colors.BG_WHITE)
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        separator = tk.Frame(actions_frame, bg=Colors.BORDER, height=1)
        separator.pack(fill=tk.X, pady=(0, 8))
        
        # Кнопка изменения статуса
        status_btn_text = "✅ Отметить изученным" if card.status == "not_studied" else "🔄 Отметить неизученным"
        status_btn = tk.Button(
            actions_frame,
            text=status_btn_text,
            font=("Segoe UI", 9),
            bg=Colors.SUCCESS if card.status == "not_studied" else Colors.TEXT_GRAY,
            fg=Colors.WHITE,
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=3,
            command=lambda: self.toggle_status(card)
        )
        status_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(status_btn, "Изменить статус изучения карточки")
        
        # Кнопка редактирования
        edit_btn = tk.Button(
            actions_frame,
            text="✏️ Редактировать",
            font=("Segoe UI", 9),
            bg=Colors.INFO,
            fg=Colors.WHITE,
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=3,
            command=lambda: self.edit_card(card)
        )
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(edit_btn, "Редактировать слово, перевод, транскрипцию и пример")
        
        # Кнопка удаления
        delete_btn = tk.Button(
            actions_frame,
            text="🗑️ Удалить",
            font=("Segoe UI", 9),
            bg=Colors.ERROR,
            fg=Colors.WHITE,
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=3,
            command=lambda: self.delete_card(card)
        )
        delete_btn.pack(side=tk.LEFT)
        self.create_tooltip(delete_btn, "Удалить карточку из колоды")
    
    def apply_filter(self):
        """Применение фильтра"""
        self.current_filter = self.filter_var.get()
        self.load_cards()
    
    def toggle_status(self, card):
        """Изменение статуса карточки"""
        new_status = "studied" if card.status == "not_studied" else "not_studied"
        self.card_repo.update_status(card.id, new_status)
        self.load_cards()
    
    def add_card(self):
        """Добавление карточки"""
        dialog = tk.Toplevel(self)
        dialog.title("Добавление карточки")
        dialog.geometry("550x600")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"550x600+{x}+{y}")
        
        tk.Label(dialog, text="Слово (на английском):", font=Fonts.BODY).pack(pady=(20, 5), padx=20, anchor=tk.W)
        word_entry = tk.Entry(dialog, font=Fonts.BODY, width=50)
        word_entry.pack(padx=20, pady=5, fill=tk.X)
        
        tk.Label(dialog, text="Перевод:", font=Fonts.BODY).pack(pady=(10, 5), padx=20, anchor=tk.W)
        trans_entry = tk.Entry(dialog, font=Fonts.BODY, width=50)
        trans_entry.pack(padx=20, pady=5, fill=tk.X)
        
        tk.Label(dialog, text="Транскрипция (необязательно):", font=Fonts.BODY).pack(pady=(10, 5), padx=20, anchor=tk.W)
        transcr_entry = tk.Entry(dialog, font=Fonts.BODY, width=50)
        transcr_entry.pack(padx=20, pady=5, fill=tk.X)
        
        tk.Label(dialog, text="Пример использования (необязательно):", font=Fonts.BODY).pack(pady=(10, 5), padx=20, anchor=tk.W)
        example_text = tk.Text(dialog, height=5, font=Fonts.BODY, width=50)
        example_text.pack(padx=20, pady=5, fill=tk.X)
        
        btn_frame = tk.Frame(dialog, bg=Colors.BG_LIGHT)
        btn_frame.pack(pady=20)
        
        def save():
            word = word_entry.get().strip()
            translation = trans_entry.get().strip()
            
            if word and translation:
                transcription = transcr_entry.get().strip()
                example = example_text.get("1.0", tk.END).strip()
                
                self.card_repo.create(self.deck_id, word, translation, example, transcription)
                dialog.destroy()
                self.load_cards()
                messagebox.showinfo("Успех", "Карточка добавлена!")
            else:
                messagebox.showwarning("Внимание", "Заполните слово и перевод!")
        
        tk.Button(btn_frame, text="Сохранить", command=save, bg=Colors.PRIMARY, fg=Colors.WHITE, padx=25, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, padx=25, pady=5).pack(side=tk.LEFT, padx=5)
    
    def edit_card(self, card):
        """Редактирование карточки"""
        dialog = tk.Toplevel(self)
        dialog.title("Редактирование карточки")
        dialog.geometry("550x600")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"550x600+{x}+{y}")
        
        tk.Label(dialog, text="Слово (на английском):", font=Fonts.BODY).pack(pady=(20, 5), padx=20, anchor=tk.W)
        word_entry = tk.Entry(dialog, font=Fonts.BODY, width=50)
        word_entry.insert(0, card.word)
        word_entry.pack(padx=20, pady=5, fill=tk.X)
        
        tk.Label(dialog, text="Перевод:", font=Fonts.BODY).pack(pady=(10, 5), padx=20, anchor=tk.W)
        trans_entry = tk.Entry(dialog, font=Fonts.BODY, width=50)
        trans_entry.insert(0, card.translation)
        trans_entry.pack(padx=20, pady=5, fill=tk.X)
        
        tk.Label(dialog, text="Транскрипция:", font=Fonts.BODY).pack(pady=(10, 5), padx=20, anchor=tk.W)
        transcr_entry = tk.Entry(dialog, font=Fonts.BODY, width=50)
        transcr_entry.insert(0, card.transcription)
        transcr_entry.pack(padx=20, pady=5, fill=tk.X)
        
        tk.Label(dialog, text="Пример использования:", font=Fonts.BODY).pack(pady=(10, 5), padx=20, anchor=tk.W)
        example_text = tk.Text(dialog, height=5, font=Fonts.BODY, width=50)
        example_text.insert("1.0", card.example)
        example_text.pack(padx=20, pady=5, fill=tk.X)
        
        btn_frame = tk.Frame(dialog, bg=Colors.BG_LIGHT)
        btn_frame.pack(pady=20)
        
        def save():
            word = word_entry.get().strip()
            translation = trans_entry.get().strip()
            
            if word and translation:
                transcription = transcr_entry.get().strip()
                example = example_text.get("1.0", tk.END).strip()
                
                self.card_repo.update(card.id, word=word, translation=translation, 
                                     transcription=transcription, example=example)
                dialog.destroy()
                self.load_cards()
                messagebox.showinfo("Успех", "Карточка обновлена!")
            else:
                messagebox.showwarning("Внимание", "Заполните слово и перевод!")
        
        tk.Button(btn_frame, text="Сохранить", command=save, bg=Colors.PRIMARY, fg=Colors.WHITE, padx=25, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, padx=25, pady=5).pack(side=tk.LEFT, padx=5)
    
    def delete_card(self, card):
        """Удаление карточки"""
        if messagebox.askyesno("Подтверждение", f"Удалить карточку '{card.word}'?"):
            self.card_repo.delete(card.id)
            self.load_cards()
            messagebox.showinfo("Успех", "Карточка удалена")
    
    def edit_deck(self):
        """Редактирование колоды"""
        dialog = tk.Toplevel(self)
        dialog.title("Редактирование колоды")
        dialog.geometry("450x350")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f"450x350+{x}+{y}")
        
        tk.Label(dialog, text="Название колоды:", font=Fonts.BODY).pack(pady=(20, 5), padx=20, anchor=tk.W)
        name_entry = tk.Entry(dialog, font=Fonts.BODY, width=45)
        name_entry.insert(0, self.deck.name)
        name_entry.pack(padx=20, pady=5, fill=tk.X)
        
        tk.Label(dialog, text="Описание:", font=Fonts.BODY).pack(pady=(10, 5), padx=20, anchor=tk.W)
        desc_text = tk.Text(dialog, height=6, font=Fonts.BODY, width=45)
        desc_text.insert("1.0", self.deck.description)
        desc_text.pack(padx=20, pady=5, fill=tk.X)
        
        btn_frame = tk.Frame(dialog, bg=Colors.BG_LIGHT)
        btn_frame.pack(pady=20)
        
        def save():
            name = name_entry.get().strip()
            if name:
                description = desc_text.get("1.0", tk.END).strip()
                self.deck_repo.update(self.deck_id, name, description)
                self.deck = self.deck_repo.get_by_id(self.deck_id)
                self.name_label.config(text=self.deck.name)
                dialog.destroy()
                messagebox.showinfo("Успех", f"Колода '{name}' обновлена!")
            else:
                messagebox.showwarning("Внимание", "Введите название колоды")
        
        tk.Button(btn_frame, text="Сохранить", command=save, bg=Colors.PRIMARY, fg=Colors.WHITE, padx=25, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=dialog.destroy, padx=25, pady=5).pack(side=tk.LEFT, padx=5)
    
    def delete_deck(self):
        """Удаление колоды"""
        if messagebox.askyesno("Подтверждение", f"Удалить колоду '{self.deck.name}'?\nВсе карточки будут также удалены!"):
            self.deck_repo.delete(self.deck_id)
            self.go_back()
            messagebox.showinfo("Успех", "Колода удалена")
    
    def start_test(self):
        """Начать тестирование"""
        messagebox.showinfo("Тест", "Режим тестирования будет добавлен в следующей версии")
    
    def go_back(self):
        """Вернуться к списку колод"""
        # Находим корневое окно
        root = self.winfo_toplevel()
        
        # Ищем MainApplication (у него есть content_container)
        main_app = None
        for widget in root.winfo_children():
            if hasattr(widget, 'content_container'):
                main_app = widget
                break
        
        if main_app:
            # Очищаем content_container
            for widget in main_app.content_container.winfo_children():
                widget.destroy()
            
            # Создаем новый HomeScreen
            from presentation.gui.screens.home_screen import HomeScreen
            home_screen = HomeScreen(main_app.content_container)
            home_screen.pack(fill=tk.BOTH, expand=True)
            
            # Уничтожаем текущий экран
            self.destroy()