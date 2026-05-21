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
    
    def create_widgets(self):
        """Создание виджетов с прокруткой"""
        # Canvas для прокрутки
        canvas = tk.Canvas(self, bg=Colors.BG_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BG_LIGHT)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Заголовок
        header_frame = tk.Frame(scrollable_frame, bg=Colors.BG_WHITE)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text="⚙️ Настройки",
            font=Fonts.TITLE,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_DARK
        ).pack(pady=20)
        
        # ===== НАСТРОЙКА ПРИЛОЖЕНИЯ =====
        app_frame = tk.LabelFrame(
            scrollable_frame, 
            text="🎨 Настройка приложения", 
            font=Fonts.SUBTITLE, 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        app_frame.pack(fill=tk.X, padx=20, pady=10)
        
        theme_frame = tk.Frame(app_frame, bg=Colors.BG_WHITE)
        theme_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(
            theme_frame, 
            text="Тема оформления:", 
            font=Fonts.BODY, 
            bg=Colors.BG_WHITE, 
            fg=Colors.TEXT_DARK
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "light"))
        
        light_radio = tk.Radiobutton(
            theme_frame, 
            text="Светлая", 
            variable=self.theme_var, 
            value="light", 
            bg=Colors.BG_WHITE, 
            font=Fonts.BODY,
            command=self.change_theme
        )
        light_radio.pack(side=tk.LEFT, padx=10)
        
        dark_radio = tk.Radiobutton(
            theme_frame, 
            text="Темная", 
            variable=self.theme_var, 
            value="dark", 
            bg=Colors.BG_WHITE, 
            font=Fonts.BODY,
            command=self.change_theme
        )
        dark_radio.pack(side=tk.LEFT, padx=10)
        
        theme_info = tk.Label(
            theme_frame,
            text="(для применения изменений перезапустите приложение)",
            font=Fonts.SMALL,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_GRAY
        )
        theme_info.pack(side=tk.LEFT, padx=15)
        
        # ===== УПРАВЛЕНИЕ ДАННЫМИ =====
        data_frame = tk.LabelFrame(
            scrollable_frame, 
            text="💾 Управление данными", 
            font=Fonts.SUBTITLE, 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        data_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Статистика
        stats_frame = tk.Frame(data_frame, bg=Colors.BG_WHITE)
        stats_frame.pack(pady=15, padx=20)
        
        decks_count = len(self.deck_repo.get_all())
        cards_count = 0
        for deck in self.deck_repo.get_all():
            cards_count += len(self.card_repo.get_by_deck(deck.id))
        
        self.stats_label = tk.Label(
            stats_frame,
            text=f"📊 Данные: {decks_count} колод, {cards_count} карточек",
            font=Fonts.BODY,
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_GRAY
        )
        self.stats_label.pack()
        
        # Кнопки экспорта
        export_frame = tk.LabelFrame(data_frame, text="📤 Экспорт данных", font=Fonts.BODY, bg=Colors.BG_WHITE, fg=Colors.TEXT_DARK)
        export_frame.pack(fill=tk.X, padx=20, pady=10)
        
        export_btn_frame = tk.Frame(export_frame, bg=Colors.BG_WHITE)
        export_btn_frame.pack(pady=15)
        
        export_json_btn = tk.Button(
            export_btn_frame,
            text="📄 Экспорт в JSON",
            command=self.export_to_json,
            bg=Colors.INFO,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        export_json_btn.pack(side=tk.LEFT, padx=10)
        self.create_tooltip(export_json_btn, "Экспортировать все данные в JSON файл")
        
        export_csv_btn = tk.Button(
            export_btn_frame,
            text="📊 Экспорт в CSV",
            command=self.export_to_csv,
            bg=Colors.SUCCESS,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        export_csv_btn.pack(side=tk.LEFT, padx=10)
        self.create_tooltip(export_csv_btn, "Экспортировать все данные в CSV файл")
        
        # Кнопки импорта
        import_frame = tk.LabelFrame(data_frame, text="📥 Импорт данных", font=Fonts.BODY, bg=Colors.BG_WHITE, fg=Colors.TEXT_DARK)
        import_frame.pack(fill=tk.X, padx=20, pady=10)
        
        import_btn_frame = tk.Frame(import_frame, bg=Colors.BG_WHITE)
        import_btn_frame.pack(pady=15)
        
        import_json_btn = tk.Button(
            import_btn_frame,
            text="📄 Импорт из JSON",
            command=self.import_from_json,
            bg=Colors.PRIMARY,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        import_json_btn.pack(side=tk.LEFT, padx=10)
        self.create_tooltip(import_json_btn, "Импортировать данные из JSON файла")
        
        import_csv_btn = tk.Button(
            import_btn_frame,
            text="📊 Импорт из CSV",
            command=self.import_from_csv,
            bg=Colors.SECONDARY,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        import_csv_btn.pack(side=tk.LEFT, padx=10)
        self.create_tooltip(import_csv_btn, "Импортировать данные из CSV файла")
        
        # Кнопка сброса
        reset_btn = tk.Button(
            data_frame,
            text="🗑️ Сбросить все данные",
            command=self.reset_all_data,
            bg=Colors.ERROR,
            fg=Colors.WHITE,
            font=Fonts.BUTTON,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        reset_btn.pack(pady=(10, 15))
        self.create_tooltip(reset_btn, "Удалить все колоды и карточки (необратимое действие)")
        
        # ===== О ПРОГРАММЕ =====
        about_frame = tk.LabelFrame(
            scrollable_frame, 
            text="ℹ️ О программе", 
            font=Fonts.SUBTITLE, 
            bg=Colors.BG_WHITE, 
            fg=Colors.PRIMARY
        )
        about_frame.pack(fill=tk.X, padx=20, pady=10)
        
        about_text = """
Flashcard English v1.0.0

Приложение для изучения английского языка по методу флеш-карточек
Разработано с использованием Python и Tkinter

Функции:
• Создание и управление колодами карточек
• Добавление карточек со словом, переводом, транскрипцией и примером
• Тестирование с множественным выбором
• Отслеживание прогресса и достижений
• Глобальный поиск по словам и переводам
• Экспорт и импорт данных (JSON, CSV)

© 2026 Все права защищены
        """
        
        tk.Label(
            about_frame, 
            text=about_text, 
            font=Fonts.BODY, 
            bg=Colors.BG_WHITE, 
            fg=Colors.TEXT_GRAY, 
            justify=tk.LEFT
        ).pack(pady=20)
        
        # Нижний отступ
        tk.Frame(scrollable_frame, height=20, bg=Colors.BG_LIGHT).pack()
    
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
    
    def change_theme(self):
        """Изменение темы оформления"""
        new_theme = self.theme_var.get()
        self.settings["theme"] = new_theme
        self.save_settings()
        
        # Применяем тему
        self.apply_theme(new_theme)
        
        themes = {"light": "Светлая", "dark": "Темная"}
        messagebox.showinfo(
            "Настройки сохранены", 
            f"Тема '{themes[new_theme]}' выбрана.\nДля применения изменений перезапустите приложение."
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