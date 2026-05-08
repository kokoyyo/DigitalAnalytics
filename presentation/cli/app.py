"""Главный цикл CLI приложения с нижним меню"""

import sys
import os

# Для Windows поддержки цветов
if sys.platform == "win32":
    os.system("color")


class Colors:
    """ANSI цвета для терминала"""
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    BG_BLUE = '\033[44m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    CLEAR = '\033[2J\033[H'


from presentation.cli.utils.router import get_router


class CLIApp:
    """Главное приложение CLI"""
    
    def __init__(self):
        self.router = get_router()
        self.current_screen = "home"
        self.running = True
        
        # Меню пункты
        self.menu_items = ["Мои колоды", "Прогресс", "Поиск", "Настройки"]
        self.menu_icons = ["📚", "📊", "🔍", "⚙️"]
        
    def clear_screen(self):
        """Очистка экрана"""
        if sys.platform == "win32":
            os.system('cls')
        else:
            print(Colors.CLEAR, end="")
    
    def print_header(self):
        """Печать заголовка"""
        print(f"{Colors.BOLD}{Colors.BLUE}╔{'═' * 60}╗{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}║{Colors.RESET}  {Colors.BOLD}📖 Flashcard English{Colors.RESET} - Изучение английского по флеш-карточкам{Colors.BLUE}  ║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}╚{'═' * 60}╝{Colors.RESET}")
        print()
    
    def render_current_screen(self):
        """Отобразить текущий экран"""
        self.clear_screen()
        self.print_header()
        
        # Получаем и рендерим текущий экран через роутер
        screen_content = self.router.render_screen(self.current_screen)
        print(screen_content)
        print()
        self.render_menu()
    
    def render_menu(self):
        """Отобразить нижнее меню из 4 кнопок"""
        print(f"{Colors.BOLD}{Colors.BLUE}{'─' * 60}{Colors.RESET}")
        
        menu_line = ""
        for i, (icon, item) in enumerate(zip(self.menu_icons, self.menu_items)):
            # Определяем активный пункт меню
            is_active = (
                (i == 0 and self.current_screen == "home") or
                (i == 1 and self.current_screen == "progress") or
                (i == 2 and self.current_screen == "search") or
                (i == 3 and self.current_screen == "settings")
            )
            
            if is_active:
                menu_line += f"{Colors.BOLD}{Colors.WHITE}{Colors.BG_BLUE} {icon} {item} {Colors.RESET}  "
            else:
                menu_line += f"{Colors.DIM}{Colors.WHITE} {icon} {item} {Colors.RESET}  "
        
        print(menu_line)
        print(f"{Colors.DIM}← → - навигация  |  Enter - выбрать  |  q - выход{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'─' * 60}{Colors.RESET}")
    
    def get_key_windows(self):
        """Получение клавиши в Windows"""
        import msvcrt
        key = msvcrt.getch()
        
        if key == b'\xe0':  # Специальные клавиши (стрелки, F1-F12)
            key = msvcrt.getch()
            if key == b'H':  # Стрелка вверх
                return 'up'
            elif key == b'P':  # Стрелка вниз
                return 'down'
            elif key == b'K':  # Стрелка влево
                return 'left'
            elif key == b'M':  # Стрелка вправо
                return 'right'
            else:
                return None
        elif key == b'\r':  # Enter
            return 'enter'
        elif key == b'q' or key == b'Q':  # q или Q
            return 'quit'
        else:
            return None
    
    def get_key_unix(self):
        """Получение клавиши в Unix (Linux/Mac)"""
        import sys
        import tty
        import termios
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            
            if ch == 'q' or ch == 'Q':
                return 'quit'
            elif ch == '\x1b':  # Escape последовательность
                ch2 = sys.stdin.read(1)
                ch3 = sys.stdin.read(1)
                if ch2 == '[':
                    if ch3 == 'D':
                        return 'left'
                    elif ch3 == 'C':
                        return 'right'
                    elif ch3 == 'A':
                        return 'up'
                    elif ch3 == 'B':
                        return 'down'
            elif ch == '\r':
                return 'enter'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None
    
    def handle_input(self):
        """Обработка ввода пользователя"""
        if sys.platform == "win32":
            key = self.get_key_windows()
        else:
            key = self.get_key_unix()
        
        if key == 'quit':
            self.running = False
            self.clear_screen()
            print(f"{Colors.YELLOW}До свидания! 👋{Colors.RESET}")
        elif key == 'left':
            self.navigate_prev()
        elif key == 'right':
            self.navigate_next()
        elif key == 'enter':
            self.select_current_menu()
    
    def navigate_prev(self):
        """Переключение на предыдущий пункт меню"""
        menu_map = {0: "home", 1: "progress", 2: "search", 3: "settings"}
        current_index = None
        
        for idx, screen in menu_map.items():
            if self.current_screen == screen:
                current_index = idx
                break
        
        if current_index is not None:
            new_index = (current_index - 1) % 4
            self.current_screen = menu_map[new_index]
            self.render_current_screen()
    
    def navigate_next(self):
        """Переключение на следующий пункт меню"""
        menu_map = {0: "home", 1: "progress", 2: "search", 3: "settings"}
        current_index = None
        
        for idx, screen in menu_map.items():
            if self.current_screen == screen:
                current_index = idx
                break
        
        if current_index is not None:
            new_index = (current_index + 1) % 4
            self.current_screen = menu_map[new_index]
            self.render_current_screen()
    
    def select_current_menu(self):
        """Выбор текущего пункта меню"""
        self.clear_screen()
        print(f"{Colors.GREEN}Вы выбрали: {self.current_screen}{Colors.RESET}")
        print(f"{Colors.DIM}Нажмите Enter для продолжения...{Colors.RESET}")
        
        if sys.platform == "win32":
            import msvcrt
            msvcrt.getch()
        else:
            input()
        
        self.render_current_screen()
    
    def run(self):
        """Запуск главного цикла приложения"""
        self.render_current_screen()
        
        while self.running:
            self.handle_input()


def run_cli():
    """Запуск CLI интерфейса"""
    app = CLIApp()
    app.run()