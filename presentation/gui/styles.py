"""Стили и темы оформления"""

from tkinter import ttk
import tkinter as tk


class Colors:
    """Цветовая схема"""
    # Основные цвета
    PRIMARY = "#2196F3"  # Синий
    PRIMARY_DARK = "#1976D2"
    PRIMARY_LIGHT = "#BBDEFB"
    SECONDARY = "#FF9800"  # Оранжевый
    SECONDARY_DARK = "#F57C00"
    
    # Фоновые цвета
    BG_LIGHT = "#F5F5F5"
    BG_WHITE = "#FFFFFF"
    BG_CARD = "#FFFFFF"
    
    # Текст
    TEXT_DARK = "#212121"
    TEXT_GRAY = "#757575"
    TEXT_LIGHT = "#FFFFFF"  # Добавлено! Для светлого текста на темном фоне
    WHITE = "#FFFFFF"  # Добавлено для обратной совместимости
    BLACK = "#000000"
    
    # Статусы
    SUCCESS = "#4CAF50"  # Зеленый
    ERROR = "#F44336"    # Красный
    WARNING = "#FFC107"  # Желтый
    INFO = "#2196F3"     # Синий
    
    # Дополнительные
    BORDER = "#E0E0E0"
    HOVER = "#E3F2FD"


class Fonts:
    """Шрифты"""
    TITLE = ("Segoe UI", 18, "bold")
    SUBTITLE = ("Segoe UI", 14, "bold")
    BODY = ("Segoe UI", 11)
    BODY_BOLD = ("Segoe UI", 11, "bold")
    BUTTON = ("Segoe UI", 11)
    SMALL = ("Segoe UI", 9)
    CARD_TITLE = ("Segoe UI", 13, "bold")


def setup_styles():
    """Настройка стилей для ttk виджетов"""
    style = ttk.Style()
    
    # Стиль для прогресс-бара
    style.configure(
        "Success.Horizontal.TProgressbar",
        troughcolor=Colors.BORDER,
        background=Colors.SUCCESS,
        thickness=12,  # Увеличенная толщина
        relief=tk.FLAT
    )
    
    # Настройка для всех прогресс-баров
    style.configure(
        "TProgressbar",
        troughcolor=Colors.BORDER,
        background=Colors.PRIMARY,
        thickness=10
    )