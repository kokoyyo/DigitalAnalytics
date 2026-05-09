"""Главное окно приложения с навигацией"""

import tkinter as tk
from tkinter import ttk
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
        
        # Настройка стилей
        setup_styles()
        
        # Переменные
        self.current_screen = None
        self.current_frame = None
        
        # Создание интерфейса
        self.create_widgets()
        
        # Показываем начальный экран
        self.show_home_screen()
    
    def create_widgets(self):
        """Создание виджетов"""
        # Создаем основной контейнер
        main_container = tk.Frame(self.root, bg=Colors.BG_LIGHT)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Контейнер для содержимого
        self.content_container = tk.Frame(main_container, bg=Colors.BG_LIGHT)
        self.content_container.pack(fill=tk.BOTH, expand=True)
        
        # Нижняя навигационная панель
        self.create_navigation_bar(main_container)
    
    def create_navigation_bar(self, parent):
        """Создание нижней навигационной панели"""
        nav_frame = tk.Frame(parent, bg=Colors.PRIMARY, height=60)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X)
        nav_frame.pack_propagate(False)
        
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
        if self.current_frame:
            self.current_frame.destroy()
    
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