"""Стили и темы оформления"""

from tkinter import ttk
import tkinter as tk


class Colors:
    """Цветовая схема - простая версия"""
    # Основные цвета
    PRIMARY = "#2196F3"
    PRIMARY_DARK = "#1976D2"
    PRIMARY_LIGHT = "#BBDEFB"
    SECONDARY = "#FF9800"
    SECONDARY_DARK = "#F57C00"
    
    # Фоновые цвета
    BG_LIGHT = "#F5F5F5"
    BG_WHITE = "#FFFFFF"
    BG_CARD = "#FFFFFF"
    
    # Текст
    TEXT_DARK = "#212121"
    TEXT_GRAY = "#757575"
    TEXT_LIGHT = "#FFFFFF"
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    
    # Статусы
    SUCCESS = "#4CAF50"
    ERROR = "#F44336"
    WARNING = "#FFC107"
    INFO = "#2196F3"
    
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
    
    style.configure(
        "Success.Horizontal.TProgressbar",
        troughcolor=Colors.BORDER,
        background=Colors.SUCCESS,
        thickness=12,
        relief=tk.FLAT
    )
    
    style.configure(
        "TProgressbar",
        troughcolor=Colors.BORDER,
        background=Colors.PRIMARY,
        thickness=10
    )