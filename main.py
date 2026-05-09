#!/usr/bin/env python3
"""
Flashcard English - Графическое приложение для изучения английского по флеш-карточкам
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Точка входа в приложение"""
    from presentation.gui.main_window import MainApplication
    import tkinter as tk
    
    root = tk.Tk()
    root.title("Flashcard English - Изучение английского")
    root.geometry("900x700")
    root.minsize(600, 500)  # Минимальный размер окна
    
    app = MainApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()