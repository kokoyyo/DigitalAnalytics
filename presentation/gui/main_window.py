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
    
    def create_widgets(self):
        """Создание виджетов"""
        # Создаем основной контейнер с grid
        main_container = tk.Frame(self.root, bg=Colors.BG_LIGHT)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Контейнер для содержимого
        self.content_container = tk.Frame(main_container, bg=Colors.BG_LIGHT)
        self.content_container.grid(row=0, column=0, sticky="nsew")
        
        # Нижняя навигационная панель
        self.create_navigation_bar(main_container)
    
    def create_navigation_bar(self, parent):
        """Создание нижней навигационной панели"""
        nav_frame = tk.Frame(parent, bg=Colors.PRIMARY, height=60)
        nav_frame.grid(row=1, column=0, sticky="ew")
        nav_frame.grid_propagate(False)
        
        for i in range(4):
            nav_frame.grid_columnconfigure(i, weight=1)
        
        buttons = [
            ("🏠 Мои колоды", self.show_home_screen, 0),
            ("📊 Прогресс", self.show_progress_screen, 1),
            ("🔍 Поиск", self.show_search_screen, 2),
            ("⚙️ Настройки", self.show_settings_screen, 3)
        ]
        
        for text, command, col in buttons:
            btn = tk.Button(
                nav_frame,
                text=text,
                command=command,
                bg=Colors.PRIMARY,
                fg=Colors.WHITE,
                font=Fonts.BUTTON,
                relief=tk.FLAT,
                cursor="hand2"
            )
            btn.grid(row=0, column=col, sticky="nsew", padx=1, pady=5)
            
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=Colors.PRIMARY_DARK))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=Colors.PRIMARY))
    
    def clear_content(self):
        """Очистка области содержимого"""
        for widget in self.content_container.winfo_children():
            widget.destroy()
    
    def show_home_screen(self):
        self.clear_content()
        self.current_frame = HomeScreen(self.content_container)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_progress_screen(self):
        self.clear_content()
        self.current_frame = ProgressScreen(self.content_container)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_search_screen(self):
        self.clear_content()
        self.current_frame = SearchScreen(self.content_container)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_settings_screen(self):
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