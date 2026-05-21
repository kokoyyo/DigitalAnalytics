"""Стили и темы оформления"""

from tkinter import ttk
import tkinter as tk

class Colors:
    """Цветовая схема"""
    # Значения по умолчанию (светлая тема)
    PRIMARY = "#2196F3"
    PRIMARY_DARK = "#1976D2"
    SECONDARY = "#FF9800"
    SECONDARY_DARK = "#F57C00"
    BG_LIGHT = "#F5F5F5"
    BG_WHITE = "#FFFFFF"
    BG_CARD = "#FFFFFF"
    TEXT_DARK = "#212121"
    TEXT_GRAY = "#757575"
    TEXT_LIGHT = "#FFFFFF"
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    SUCCESS = "#4CAF50"
    ERROR = "#F44336"
    WARNING = "#FFC107"
    INFO = "#2196F3"
    BORDER = "#E0E0E0"
    HOVER = "#E3F2FD"
    
    @classmethod
    def set_theme(cls, theme):
        """Установка темы"""
        if theme == "dark":
            cls.PRIMARY = "#2196F3"
            cls.PRIMARY_DARK = "#1976D2"
            cls.BG_LIGHT = "#121212"
            cls.BG_WHITE = "#1E1E1E"
            cls.BG_CARD = "#2D2D2D"
            cls.TEXT_DARK = "#FFFFFF"
            cls.TEXT_GRAY = "#B0B0B0"
            cls.BORDER = "#404040"
            cls.HOVER = "#2C2C2C"
        else:
            cls.PRIMARY = "#2196F3"
            cls.PRIMARY_DARK = "#1976D2"
            cls.BG_LIGHT = "#F5F5F5"
            cls.BG_WHITE = "#FFFFFF"
            cls.BG_CARD = "#FFFFFF"
            cls.TEXT_DARK = "#212121"
            cls.TEXT_GRAY = "#757575"
            cls.BORDER = "#E0E0E0"
            cls.HOVER = "#E3F2FD"


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