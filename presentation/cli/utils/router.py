"""Роутер для переключения между экранами"""

class Colors:
    """ANSI цвета для терминала"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'


class Router:
    """Роутер для навигации между экранами"""
    
    def __init__(self):
        self.screens = {
            "home": self.render_home_screen,
            "progress": self.render_progress_screen,
            "search": self.render_search_screen,
            "settings": self.render_settings_screen,
        }
        
        self.screen_titles = {
            "home": "Мои колоды",
            "progress": "Прогресс",
            "search": "Поиск",
            "settings": "Настройки",
        }
    
    def render_screen(self, screen_name: str) -> str:
        """Рендеринг указанного экрана"""
        if screen_name in self.screens:
            return self.screens[screen_name]()
        return f"{Colors.RED}Экран не найден{Colors.RESET}"
    
    def get_screen_title(self, screen_name: str) -> str:
        """Получить заголовок экрана"""
        return self.screen_titles.get(screen_name, "Неизвестно")
    
    def render_home_screen(self):
        """Главный экран с колодами"""
        content = f"""
{Colors.BOLD}{Colors.YELLOW}🏠 Главный экран{Colors.RESET}

{Colors.BOLD}{Colors.CYAN}📊 Статистика:{Colors.RESET}
   Всего колод: 0
   Всего карточек: 0
   Изучено: 0 (0%)

{Colors.GREEN}➕ Добавить колоду{Colors.RESET}

{Colors.BOLD}{Colors.CYAN}📚 Мои колоды:{Colors.RESET}
   {Colors.DIM}Нет созданных колод. Нажмите Enter на кнопке "Добавить колоду"{Colors.RESET}
"""
        return content
    
    def render_progress_screen(self):
        """Экран прогресса и достижений"""
        content = f"""
{Colors.BOLD}{Colors.YELLOW}📊 Прогресс{Colors.RESET}

{Colors.BOLD}{Colors.CYAN}🏆 Достижения:{Colors.RESET}
   🔥 Текущая серия: 0 дней
   📚 Изучено сегодня: 0 слов
   🎯 Всего изучено: 0 слов

{Colors.BOLD}{Colors.CYAN}📈 Общая статистика:{Colors.RESET}
   📋 Всего карточек: 0
   ✅ Изучено: 0
   ⏳ Осталось: 0

{Colors.BOLD}{Colors.CYAN}📅 Статистика за сегодня:{Colors.RESET}
   🎴 Изучено карточек: 0
   ✓ Правильных ответов: 0%
   ⏱ Время: 0 мин
"""
        return content
    
    def render_search_screen(self):
        """Экран глобального поиска"""
        content = f"""
{Colors.BOLD}{Colors.YELLOW}🔍 Глобальный поиск{Colors.RESET}

🔎 Строка поиска: {Colors.DIM}(введите слово){Colors.RESET}

{Colors.BOLD}{Colors.CYAN}Результаты поиска:{Colors.RESET}
   {Colors.DIM}Введите запрос для поиска{Colors.RESET}
"""
        return content
    
    def render_settings_screen(self):
        """Экран настроек"""
        content = f"""
{Colors.BOLD}{Colors.YELLOW}⚙️ Настройки{Colors.RESET}

{Colors.BOLD}{Colors.CYAN}🎨 Настройка приложения:{Colors.RESET}
   🌓 Тема оформления: {Colors.DIM}Светлая (в разработке){Colors.RESET}

{Colors.BOLD}{Colors.CYAN}💾 Управление данными:{Colors.RESET}
   📤 Экспортировать данные
   📥 Импортировать данные

{Colors.BOLD}{Colors.CYAN}ℹ️ О программе:{Colors.RESET}
   Flashcard English v0.1.0
   Приложение для изучения английского по флеш-карточкам
"""
        return content


# Синглтон роутера
_router_instance = None


def get_router() -> Router:
    """Получить экземпляр роутера (синглтон)"""
    global _router_instance
    if _router_instance is None:
        _router_instance = Router()
    return _router_instance