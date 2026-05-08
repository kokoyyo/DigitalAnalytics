#!/usr/bin/env python3
"""
Flashcard English - Приложение для изучения английского по флеш-карточкам
"""

import sys
import os

# Добавляем корневую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Точка входа в приложение"""
    
    # Пока только CLI, в будущем можно добавить выбор
    # if len(sys.argv) > 1 and sys.argv[1] == "--gui":
    #     from presentation.gui.app import run_gui
    #     run_gui()
    # else:
    from presentation.cli.app import run_cli
    run_cli()


if __name__ == "__main__":
    main()