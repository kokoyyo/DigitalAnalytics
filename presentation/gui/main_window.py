"""Главное окно приложения с навигацией"""

import tkinter as tk
from tkinter import ttk
import json
import os
from presentation.gui.styles import Colors, Fonts, setup_styles
from presentation.gui.screens.home_screen import HomeScreen
from presentation.gui.screens.progress_screen import ProgressScreen
from presentation.gui.screens.search_screen import SearchScreen
from presentation.gui.screens.settings_screen import SettingsScreen


class MainApplication:
    """Главное приложение с нижней навигацией"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Flashcard English - Изучение английского")
        self.root.geometry("1000x700")
        self.root.minsize(600, 500)
        
        # Загружаем сохраненную тему
        self.load_saved_theme()
        
        # Настройка корневого окна для grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Сохраняем ссылку на себя
        self.root.main_app = self
        
        # Настройка стилей
        setup_styles()
        
        # Переменные
        self.current_screen = None
        self.current_frame = None
        
        # Создание интерфейса
        self.create_widgets()
        
        # Показываем начальный экран
        self.show_home_screen()
    
    def load_saved_theme(self):
        """Загрузка сохраненной темы"""
        settings_file = "settings.json"
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    theme = settings.get("theme", "light")
                    self.apply_theme(theme)
            except:
                self.apply_theme("light")
        else:
            self.apply_theme("light")
    
    def apply_theme(self, theme):
        """Применение темы"""
        from presentation.gui.styles import Colors
        
        if theme == "dark":
            Colors.BG_LIGHT = "#121212"
            Colors.BG_WHITE = "#1E1E1E"
            Colors.BG_CARD = "#2D2D2D"
            Colors.TEXT_DARK = "#FFFFFF"
            Colors.TEXT_GRAY = "#B0B0B0"
            Colors.BORDER = "#404040"
            Colors.HOVER = "#2C2C2C"
        else:
            Colors.BG_LIGHT = "#F5F5F5"
            Colors.BG_WHITE = "#FFFFFF"
            Colors.BG_CARD = "#FFFFFF"
            Colors.TEXT_DARK = "#212121"
            Colors.TEXT_GRAY = "#757575"
            Colors.BORDER = "#E0E0E0"
            Colors.HOVER = "#E3F2FD"
        
        # Применяем фон к корневому окну
        self.root.configure(bg=Colors.BG_LIGHT)
    
    # Цвета навигации
    _NAV_BG        = "#1565C0"   # фон панели
    _NAV_HOVER     = "#1769AA"   # наведение
    _NAV_ACTIVE    = "#1976D2"   # активная вкладка
    _NAV_INDICATOR = "#FFFFFF"   # нижний индикатор активной вкладки
    _NAV_FG        = "#BBDEFB"   # текст неактивных
    _NAV_FG_ACTIVE = "#FFFFFF"   # текст активной

    def create_widgets(self):
        """Создание виджетов"""
        main_container = tk.Frame(self.root, bg=Colors.BG_LIGHT)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        self.content_container = tk.Frame(main_container, bg=Colors.BG_LIGHT)
        self.content_container.grid(row=0, column=0, sticky="nsew")

        self.create_navigation_bar(main_container)

    def create_navigation_bar(self, parent):
        """Создание нижней навигационной панели"""
        self._active_tab = None
        self._nav_tabs = {}

        # Разделитель-тень сверху
        tk.Frame(parent, bg="#0D47A1", height=2).grid(row=1, column=0, sticky="ew")

        nav_frame = tk.Frame(parent, bg=self._NAV_BG, height=72)
        nav_frame.grid(row=2, column=0, sticky="ew")
        nav_frame.grid_propagate(False)

        for i in range(4):
            nav_frame.grid_columnconfigure(i, weight=1)

        tabs = [
            ("home",     "🏠", "Мои колоды", self.show_home_screen),
            ("progress", "📊", "Прогресс",   self.show_progress_screen),
            ("search",   "🔍", "Поиск",       self.show_search_screen),
            ("settings", "⚙️",  "Настройки",  self.show_settings_screen),
        ]

        for col, (tab_id, icon, label, command) in enumerate(tabs):
            tab = tk.Frame(nav_frame, bg=self._NAV_BG, cursor="hand2")
            tab.grid(row=0, column=col, sticky="nsew")

            # Отступ сверху
            tk.Frame(tab, bg=self._NAV_BG, height=8).pack(side=tk.TOP)

            icon_lbl = tk.Label(tab, text=icon, font=("Segoe UI", 17),
                                bg=self._NAV_BG, fg=self._NAV_FG, cursor="hand2")
            icon_lbl.pack(side=tk.TOP)

            text_lbl = tk.Label(tab, text=label, font=("Segoe UI", 9),
                                bg=self._NAV_BG, fg=self._NAV_FG, cursor="hand2")
            text_lbl.pack(side=tk.TOP)

            # Индикатор активной вкладки — белая полоска у нижнего края
            indicator = tk.Frame(tab, bg=self._NAV_BG, height=3)
            indicator.pack(side=tk.BOTTOM, fill=tk.X)

            self._nav_tabs[tab_id] = {
                "tab": tab,
                "icon": icon_lbl,
                "text": text_lbl,
                "indicator": indicator,
            }

            all_widgets = [tab, icon_lbl, text_lbl, indicator]
            for w in all_widgets:
                w.bind("<Button-1>", lambda e, tid=tab_id, cmd=command:
                       self._nav_select(tid, cmd))
                w.bind("<Enter>",    lambda e, tid=tab_id: self._nav_hover(tid, True))
                w.bind("<Leave>",    lambda e, tid=tab_id: self._nav_hover(tid, False))

    def _nav_select(self, tab_id, command):
        self._nav_set_active(tab_id)
        command()

    def _nav_hover(self, tab_id, entering):
        if tab_id == self._active_tab:
            return
        color = self._NAV_HOVER if entering else self._NAV_BG
        t = self._nav_tabs[tab_id]
        for w in [t["tab"], t["icon"], t["text"], t["indicator"]]:
            w.config(bg=color)

    def _nav_set_active(self, tab_id):
        if not hasattr(self, "_nav_tabs"):
            return
        # Сбрасываем старую активную вкладку
        if self._active_tab and self._active_tab in self._nav_tabs:
            old = self._nav_tabs[self._active_tab]
            for w in [old["tab"], old["icon"], old["text"]]:
                w.config(bg=self._NAV_BG)
            old["icon"].config(fg=self._NAV_FG)
            old["text"].config(fg=self._NAV_FG)
            old["indicator"].config(bg=self._NAV_BG)
        # Активируем новую
        self._active_tab = tab_id
        cur = self._nav_tabs[tab_id]
        for w in [cur["tab"], cur["icon"], cur["text"]]:
            w.config(bg=self._NAV_ACTIVE)
        cur["icon"].config(fg=self._NAV_FG_ACTIVE)
        cur["text"].config(fg=self._NAV_FG_ACTIVE)
        cur["indicator"].config(bg=self._NAV_INDICATOR)
    
    def clear_content(self):
        """Очистка области содержимого"""
        for widget in self.content_container.winfo_children():
            widget.destroy()
    
    def show_home_screen(self):
        self._nav_set_active("home")
        self.clear_content()
        self.current_frame = HomeScreen(self.content_container)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_progress_screen(self):
        self._nav_set_active("progress")
        self.clear_content()
        self.current_frame = ProgressScreen(self.content_container)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_search_screen(self):
        self._nav_set_active("search")
        self.clear_content()
        self.current_frame = SearchScreen(self.content_container)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_settings_screen(self):
        self._nav_set_active("settings")
        self.clear_content()
        self.current_frame = SettingsScreen(self.content_container)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def refresh_current_screen(self):
        """Обновить текущий экран"""
        if hasattr(self.current_frame, 'refresh'):
            self.current_frame.refresh()
        elif hasattr(self.current_frame, 'load_data'):
            self.current_frame.load_data()
        elif hasattr(self.current_frame, 'load_decks'):
            self.current_frame.load_decks()

    def refresh_all_screens(self):
        """Принудительное обновление всех экранов"""
        # Очищаем кэш репозиториев
        from data.repositories import StatisticsRepository
        stats_repo = StatisticsRepository()
        stats_repo.refresh()
        
        # Обновляем текущий экран
        if hasattr(self.current_frame, 'refresh'):
            self.current_frame.refresh()
        elif hasattr(self.current_frame, 'load_data'):
            self.current_frame.load_data()
        elif hasattr(self.current_frame, 'load_decks'):
            self.current_frame.load_decks()