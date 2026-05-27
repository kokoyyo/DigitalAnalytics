"""Экран настроек"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import os
from datetime import datetime
from presentation.gui.styles import Colors, Fonts
from data.repositories import DeckRepository, CardRepository, StatisticsRepository


class SettingsScreen(tk.Frame):
    """Экран настроек"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=Colors.BG_LIGHT)
        self.parent = parent
        self.deck_repo = DeckRepository()
        self.card_repo = CardRepository()
        self.stats_repo = StatisticsRepository()
        
        # Загружаем настройки
        self.settings = self.load_settings()
        
        self.create_widgets()
    
    def load_settings(self):
        """Загрузка настроек из файла"""
        settings_file = "settings.json"
        default_settings = {"theme": "light"}
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default_settings
        return default_settings
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        settings_file = "settings.json"
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    # ── вспомогательные методы вёрстки ───────────────────────────────────────

    def _section(self, parent, icon, title, accent):
        """Карточка-секция с цветным акцентом слева."""
        outer = tk.Frame(parent, bg=Colors.BG_WHITE, relief=tk.FLAT, bd=0)
        outer.pack(fill=tk.X, padx=20, pady=8)

        # тонкая цветная полоска
        tk.Frame(outer, bg=accent, width=4).pack(side=tk.LEFT, fill=tk.Y)

        body = tk.Frame(outer, bg=Colors.BG_WHITE)
        body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # заголовок секции
        hdr = tk.Frame(body, bg=accent)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=f"  {icon}  {title}", font=Fonts.BODY_BOLD,
                 bg=accent, fg=Colors.WHITE, pady=8).pack(side=tk.LEFT)

        content = tk.Frame(body, bg=Colors.BG_WHITE)
        content.pack(fill=tk.BOTH, padx=16, pady=14)
        return content

    def _btn(self, parent, text, command, color, tooltip_text=None):
        """Кнопка без мерцания (activebackground = bg)."""
        btn = tk.Button(
            parent, text=text, command=command,
            bg=color, activebackground=color,
            fg=Colors.WHITE, activeforeground=Colors.WHITE,
            font=Fonts.BUTTON, relief=tk.FLAT,
            padx=18, pady=7, cursor="hand2",
            bd=0, highlightthickness=0,
        )
        if tooltip_text:
            self.create_tooltip(btn, tooltip_text)
        return btn

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

    # ── основной метод ────────────────────────────────────────────────────────

    def create_widgets(self):
        """Создание виджетов"""
        NAV_BG = "#1565C0"

        # ── Canvas + скролл ──────────────────────────────────────────────────
        canvas = tk.Canvas(self, bg=Colors.BG_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=Colors.BG_LIGHT)   # scrollable_frame
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        self._sf_win = canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(
            self._sf_win, width=e.width))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas = canvas
        self.scrollable_frame = sf
        
        # Универсальный обработчик скролла
        self._mousewheel_handler = self._make_mousewheel_handler()
        self._bind_mousewheel(canvas)
        self._bind_mousewheel(sf)

        # ── Шапка (синяя, как навбар) ─────────────────────────────────────────
        header = tk.Frame(sf, bg=NAV_BG)
        header.pack(fill=tk.X)
        tk.Label(header, text="⚙️  Настройки", font=("Segoe UI", 20, "bold"),
                 bg=NAV_BG, fg="#FFFFFF", pady=20).pack(side=tk.LEFT, padx=28)

        # ── Секция: Оформление ────────────────────────────────────────────────
        sec1 = self._section(sf, "🎨", "Оформление", Colors.PRIMARY)

        tk.Label(sec1, text="Тема интерфейса:", font=Fonts.BODY,
                 bg=Colors.BG_WHITE, fg=Colors.TEXT_DARK).pack(anchor=tk.W)

        radio_row = tk.Frame(sec1, bg=Colors.BG_WHITE)
        radio_row.pack(anchor=tk.W, pady=(6, 0))

        self.theme_var = tk.StringVar(value=self.settings.get("theme", "light"))
        for label, val in [("☀️  Светлая", "light"), ("🌙  Тёмная", "dark")]:
            tk.Radiobutton(radio_row, text=label, variable=self.theme_var,
                           value=val, bg=Colors.BG_WHITE, fg=Colors.TEXT_DARK,
                           selectcolor=Colors.BG_WHITE, activebackground=Colors.BG_WHITE,
                           font=Fonts.BODY, command=self.change_theme
                           ).pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(sec1, text="Перезапустите приложение для применения темы",
                 font=Fonts.SMALL, bg=Colors.BG_WHITE, fg=Colors.TEXT_GRAY
                 ).pack(anchor=tk.W, pady=(4, 0))

        # ── Секция: Данные ────────────────────────────────────────────────────
        sec2 = self._section(sf, "💾", "Управление данными", "#1976D2")

        # мини-статистика
        decks_count = len(self.deck_repo.get_all())
        cards_count = sum(len(self.card_repo.get_by_deck(d.id))
                          for d in self.deck_repo.get_all())
        stat_row = tk.Frame(sec2, bg="#EEF4FF", bd=0)
        stat_row.pack(fill=tk.X, pady=(0, 14))
        self.stats_label = tk.Label(
            stat_row,
            text=f"  📋  {decks_count} колод   ·   {cards_count} карточек",
            font=Fonts.BODY, bg="#EEF4FF", fg=Colors.PRIMARY, pady=8, anchor=tk.W)
        self.stats_label.pack(fill=tk.X)

        # экспорт
        tk.Label(sec2, text="Экспорт", font=Fonts.BODY_BOLD,
                 bg=Colors.BG_WHITE, fg=Colors.TEXT_GRAY).pack(anchor=tk.W)
        exp_row = tk.Frame(sec2, bg=Colors.BG_WHITE)
        exp_row.pack(anchor=tk.W, pady=(6, 14))
        self._btn(exp_row, "📄  JSON", self.export_to_json,
                  Colors.INFO, "Экспортировать все данные в JSON").pack(side=tk.LEFT, padx=(0, 10))
        self._btn(exp_row, "📊  CSV",  self.export_to_csv,
                  Colors.SUCCESS, "Экспортировать все данные в CSV").pack(side=tk.LEFT)

        # импорт
        tk.Label(sec2, text="Импорт", font=Fonts.BODY_BOLD,
                 bg=Colors.BG_WHITE, fg=Colors.TEXT_GRAY).pack(anchor=tk.W)
        imp_row = tk.Frame(sec2, bg=Colors.BG_WHITE)
        imp_row.pack(anchor=tk.W, pady=(6, 14))
        self._btn(imp_row, "📄  JSON", self.import_from_json,
                  Colors.PRIMARY, "Импортировать данные из JSON").pack(side=tk.LEFT, padx=(0, 10))
        self._btn(imp_row, "📊  CSV",  self.import_from_csv,
                  Colors.SECONDARY, "Импортировать данные из CSV").pack(side=tk.LEFT)

        # разделитель
        tk.Frame(sec2, bg=Colors.BORDER, height=1).pack(fill=tk.X, pady=(4, 14))

        self._btn(sec2, "🗑️  Сбросить все данные", self.reset_all_data,
                  Colors.ERROR, "Удалить все колоды и карточки (необратимо)"
                  ).pack(anchor=tk.W)

        # ── Секция: О программе ───────────────────────────────────────────────
        sec3 = self._section(sf, "ℹ️", "О программе", "#546E7A")

        about_items = [
            ("Flashcard English", "v1.0.0", Colors.PRIMARY),
            ("Язык", "Python + Tkinter", Colors.TEXT_GRAY),
            ("Возможности", "колоды · карточки · тесты · прогресс · поиск · импорт/экспорт",
             Colors.TEXT_GRAY),
            ("", "© 2026  Все права защищены", Colors.TEXT_GRAY),
        ]
        for label, value, color in about_items:
            row = tk.Frame(sec3, bg=Colors.BG_WHITE)
            row.pack(fill=tk.X, pady=2)
            if label:
                tk.Label(row, text=f"{label}:", font=Fonts.BODY_BOLD, width=14,
                         bg=Colors.BG_WHITE, fg=Colors.TEXT_DARK, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=value, font=Fonts.BODY,
                     bg=Colors.BG_WHITE, fg=color, anchor=tk.W,
                     wraplength=600, justify=tk.LEFT).pack(side=tk.LEFT)

        tk.Frame(sf, height=24, bg=Colors.BG_LIGHT).pack()
        
        # Привязываем скролл ко всем созданным виджетам
        self._bind_mousewheel(sf)
    
    def create_tooltip(self, widget, text):
        """Создание всплывающей подсказки"""
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
    
    def change_theme(self):
        """Изменение темы оформления"""
        new_theme = self.theme_var.get()
        old_theme = self.settings.get("theme", "light")
        
        if new_theme == old_theme:
            return
        
        self.settings["theme"] = new_theme
        self.save_settings()
        
        themes = {"light": "☀️ Светлая", "dark": "🌙 Тёмная"}
        
        messagebox.showinfo(
            "Настройки сохранены",
            f"Выбрана тема: {themes[new_theme]}\n\n"
            f"🔁 Для применения изменений перезапустите приложение.\n\n"
            f"После перезапуска интерфейс откроется в выбранной теме."
        )
    
    def apply_theme(self, theme):
        """Применение темы к интерфейсу"""
        from presentation.gui.styles import Colors
        
        if theme == "dark":
            Colors.BG_LIGHT = "#121212"
            Colors.BG_WHITE = "#1E1E1E"
            Colors.TEXT_DARK = "#FFFFFF"
            Colors.TEXT_GRAY = "#B0B0B0"
            Colors.BORDER = "#404040"
        else:
            Colors.BG_LIGHT = "#F5F5F5"
            Colors.BG_WHITE = "#FFFFFF"
            Colors.TEXT_DARK = "#212121"
            Colors.TEXT_GRAY = "#757575"
            Colors.BORDER = "#E0E0E0"
        
        # Обновляем фон главного окна
        root = self.winfo_toplevel()
        root.configure(bg=Colors.BG_LIGHT)
    
    def export_to_json(self):
        """Экспорт в JSON"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Сохранить данные как JSON"
        )
        
        if filename:
            try:
                data = {
                    "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "version": "1.0",
                    "decks": []
                }
                
                decks = self.deck_repo.get_all()
                for deck in decks:
                    deck_data = {
                        "name": deck.name,
                        "description": deck.description,
                        "cards": []
                    }
                    
                    cards = self.card_repo.get_by_deck(deck.id)
                    for card in cards:
                        card_data = {
                            "word": card.word,
                            "translation": card.translation,
                            "example": card.example,
                            "transcription": card.transcription,
                            "status": card.status
                        }
                        deck_data["cards"].append(card_data)
                    
                    data["decks"].append(deck_data)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                decks_count = len(data["decks"])
                cards_count = sum(len(deck["cards"]) for deck in data["decks"])
                
                messagebox.showinfo(
                    "Экспорт завершен", 
                    f"Данные успешно экспортированы в JSON!\n\n"
                    f"Колод: {decks_count}\n"
                    f"Карточек: {cards_count}\n"
                    f"Файл: {os.path.basename(filename)}"
                )
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать данные:\n{str(e)}")
    
    def export_to_csv(self):
        """Экспорт в CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Сохранить данные как CSV"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    writer.writerow(['Колода', 'Слово', 'Перевод', 'Транскрипция', 'Пример', 'Статус'])
                    
                    decks = self.deck_repo.get_all()
                    total_cards = 0
                    
                    for deck in decks:
                        cards = self.card_repo.get_by_deck(deck.id)
                        for card in cards:
                            writer.writerow([
                                deck.name,
                                card.word,
                                card.translation,
                                card.transcription,
                                card.example,
                                'Изучено' if card.status == 'studied' else 'Не изучено'
                            ])
                            total_cards += 1
                    
                    messagebox.showinfo(
                        "Экспорт завершен", 
                        f"Данные успешно экспортированы в CSV!\n\n"
                        f"Колод: {len(decks)}\n"
                        f"Карточек: {total_cards}\n"
                        f"Файл: {os.path.basename(filename)}"
                    )
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать данные:\n{str(e)}")
    
    def import_from_json(self):
        """Импорт из JSON"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Выберите JSON файл для импорта"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if "decks" not in data:
                    messagebox.showerror("Ошибка", "Неверный формат JSON файла!")
                    return
                
                decks_count = len(data["decks"])
                cards_count = sum(len(deck.get("cards", [])) for deck in data["decks"])
                
                if not messagebox.askyesno(
                    "Подтверждение импорта",
                    f"Будут импортированы следующие данные:\n\n"
                    f"Колод: {decks_count}\n"
                    f"Карточек: {cards_count}\n\n"
                    f"Данные будут ДОБАВЛЕНЫ к существующим.\n"
                    f"Продолжить?"
                ):
                    return
                
                imported_decks = 0
                imported_cards = 0
                
                for deck_data in data["decks"]:
                    deck_name = deck_data.get("name", "Без названия")
                    deck_description = deck_data.get("description", "")
                    
                    new_deck = self.deck_repo.create(deck_name, deck_description)
                    imported_decks += 1
                    
                    for card_data in deck_data.get("cards", []):
                        word = card_data.get("word", "")
                        translation = card_data.get("translation", "")
                        
                        if word and translation:
                            self.card_repo.create(
                                new_deck.id,
                                word,
                                translation,
                                card_data.get("example", ""),
                                card_data.get("transcription", "")
                            )
                            imported_cards += 1
                
                messagebox.showinfo(
                    "Импорт завершен", 
                    f"Данные успешно импортированы из JSON!\n\n"
                    f"Добавлено колод: {imported_decks}\n"
                    f"Добавлено карточек: {imported_cards}\n"
                    f"Файл: {os.path.basename(filename)}"
                )
                
                self.refresh_stats()
                self.update_main_screen()
                
            except json.JSONDecodeError:
                messagebox.showerror("Ошибка", "Не удалось прочитать JSON файл!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать данные:\n{str(e)}")
    
    def import_from_csv(self):
        """Импорт из CSV"""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Выберите CSV файл для импорта"
        )
        
        if filename:
            try:
                # Пробуем разные кодировки
                encodings = ['utf-8-sig', 'utf-8', 'cp1251', 'latin-1']
                data = None
                
                for encoding in encodings:
                    try:
                        with open(filename, 'r', encoding=encoding) as csvfile:
                            reader = csv.reader(csvfile)
                            data = list(reader)
                        print(f"Успешно прочитано с кодировкой: {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if not data:
                    messagebox.showerror("Ошибка", "Не удалось прочитать файл. Проверьте кодировку.")
                    return
                
                if len(data) < 2:
                    messagebox.showerror("Ошибка", "Файл не содержит данных!")
                    return
                
                rows = data[1:]  # Пропускаем заголовки
                
                # Собираем данные по колодам
                decks_data = {}
                skipped_rows = 0
                
                for row_num, row in enumerate(rows, start=2):
                    if len(row) < 6:
                        skipped_rows += 1
                        continue
                    
                    deck_name = row[0].strip()
                    word = row[1].strip()
                    translation = row[2].strip()
                    transcription = row[3].strip() if len(row) > 3 else ""
                    example = row[4].strip() if len(row) > 4 else ""
                    status = row[5].strip() if len(row) > 5 else "Не изучено"
                    
                    if not deck_name or not word or not translation:
                        skipped_rows += 1
                        continue
                    
                    if deck_name not in decks_data:
                        decks_data[deck_name] = {'cards': []}
                    
                    # Проверяем на дубликаты в пределах одного импорта
                    is_duplicate = False
                    for existing_card in decks_data[deck_name]['cards']:
                        if existing_card['word'].lower() == word.lower():
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        decks_data[deck_name]['cards'].append({
                            'word': word,
                            'translation': translation,
                            'transcription': transcription,
                            'example': example,
                            'status': 'studied' if status == 'Изучено' else 'not_studied'
                        })
                    else:
                        skipped_rows += 1
                
                if not decks_data:
                    messagebox.showerror("Ошибка", "CSV файл не содержит валидных данных!")
                    return
                
                total_decks = len(decks_data)
                total_cards = sum(len(data['cards']) for data in decks_data.values())
                
                if not messagebox.askyesno(
                    "Подтверждение импорта",
                    f"Будут импортированы следующие данные:\n\n"
                    f"Колод: {total_decks}\n"
                    f"Карточек: {total_cards}\n"
                    f"Пропущено строк: {skipped_rows}\n\n"
                    f"Данные будут ДОБАВЛЕНЫ к существующим.\n"
                    f"Продолжить?"
                ):
                    return
                
                imported_decks = 0
                imported_cards = 0
                skipped_cards = 0
                
                for deck_name, deck_data in decks_data.items():
                    # Проверяем, существует ли уже такая колода
                    existing_decks = self.deck_repo.get_all()
                    existing_deck = None
                    for d in existing_decks:
                        if d.name == deck_name:
                            existing_deck = d
                            break
                    
                    if existing_deck:
                        current_deck = existing_deck
                        imported_decks += 1
                    else:
                        current_deck = self.deck_repo.create(deck_name, "")
                        imported_decks += 1
                    
                    for card_data in deck_data['cards']:
                        # Проверяем, нет ли уже такой карточки в БД
                        existing_cards = self.card_repo.get_by_deck(current_deck.id)
                        word_exists = False
                        for c in existing_cards:
                            if c.word.lower() == card_data['word'].lower():
                                word_exists = True
                                break
                        
                        if not word_exists:
                            self.card_repo.create(
                                current_deck.id,
                                card_data['word'],
                                card_data['translation'],
                                card_data['example'],
                                card_data['transcription']
                            )
                            imported_cards += 1
                        else:
                            skipped_cards += 1
                
                messagebox.showinfo(
                    "Импорт завершен", 
                    f"Данные успешно импортированы из CSV!\n\n"
                    f"Добавлено колод: {imported_decks}\n"
                    f"Добавлено карточек: {imported_cards}\n"
                    f"Пропущено дубликатов: {skipped_cards}\n"
                    f"Файл: {os.path.basename(filename)}"
                )
                
                self.refresh_stats()
                self.update_main_screen()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать данные:\n{str(e)}")
    
    def refresh_stats(self):
        """Обновление статистики"""
        decks_count = len(self.deck_repo.get_all())
        cards_count = 0
        for deck in self.deck_repo.get_all():
            cards_count += len(self.card_repo.get_by_deck(deck.id))
        
        self.stats_label.config(text=f"📊 Данные: {decks_count} колод, {cards_count} карточек")
    
    def reset_all_data(self):
        """Сброс всех данных"""
        if messagebox.askyesno(
            "Подтверждение сброса",
            "⚠️ ВНИМАНИЕ! ⚠️\n\n"
            "Это действие удалит ВСЕ колоды и карточки.\n"
            "Восстановить данные будет невозможно.\n\n"
            "Вы действительно хотите продолжить?"
        ):
            try:
                decks = self.deck_repo.get_all()
                for deck in decks:
                    self.deck_repo.delete(deck.id)
                
                messagebox.showinfo("Сброс выполнен", "Все данные успешно удалены!")
                self.refresh_stats()
                self.update_main_screen()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить данные:\n{str(e)}")
    
    def refresh_all_screens(self):
        """Принудительное обновление всех экранов"""
        root = self.winfo_toplevel()
        if hasattr(root, 'main_app'):
            main_app = root.main_app
            
            # Принудительно обновляем статистику в репозитории
            self.stats_repo.refresh()
            
            # Обновляем главный экран
            main_app.show_home_screen()
            
            # Обновляем текущий экран настроек
            self.refresh_stats()
    
    def update_main_screen(self):
        """Обновление главного экрана"""
        root = self.winfo_toplevel()
        if hasattr(root, 'main_app'):
            main_app = root.main_app
            main_app.show_home_screen()