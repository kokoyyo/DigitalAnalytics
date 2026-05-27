"""Репозитории для работы с данными"""

import sqlite3
import os
from datetime import datetime, date, timedelta


# Путь к базе данных
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'flashcard.db')


def get_db_connection():
    """Получить соединение с БД"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Инициализация базы данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Создание таблицы колод
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создание таблицы карточек
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            translation TEXT NOT NULL,
            example TEXT,
            transcription TEXT,
            status TEXT DEFAULT 'not_studied',
            review_count INTEGER DEFAULT 0,
            last_reviewed_at TIMESTAMP,
            correct_percentage REAL DEFAULT 0,
            FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE
        )
    ''')
    
    # Создание таблицы для статистики тестов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER NOT NULL,
            test_date DATE NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            time_spent INTEGER DEFAULT 0,
            FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE
        )
    ''')
    
    # В init_db() измените создание таблицы daily_stats:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stat_date DATE NOT NULL UNIQUE,
            cards_studied INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            total_answers INTEGER DEFAULT 0,
            time_spent REAL DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()


class DeckRepository:
    """Репозиторий для работы с колодами"""
    
    def __init__(self):
        self._cache = None
    
    def _clear_cache(self):
        """Очистка кэша"""
        self._cache = None
    
    def get_all(self):
        """Получить все колоды"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM decks ORDER BY id DESC')
        decks = cursor.fetchall()
        conn.close()
        
        class Deck:
            pass
        
        result = []
        for deck in decks:
            d = Deck()
            d.id = deck['id']
            d.name = deck['name']
            d.description = deck['description'] if deck['description'] else ""
            d.created_at = deck['created_at']
            d.updated_at = deck['updated_at']
            result.append(d)
        
        return result
    
    def get_by_id(self, deck_id):
        """Получить колоду по ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM decks WHERE id = ?', (deck_id,))
        deck = cursor.fetchone()
        conn.close()
        
        if deck:
            class Deck:
                pass
            
            d = Deck()
            d.id = deck['id']
            d.name = deck['name']
            d.description = deck['description'] if deck['description'] else ""
            d.created_at = deck['created_at']
            d.updated_at = deck['updated_at']
            return d
        return None
    
    def create(self, name, description=""):
        """Создать новую колоду"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO decks (name, description) VALUES (?, ?)',
            (name, description)
        )
        conn.commit()
        deck_id = cursor.lastrowid
        conn.close()
        self._clear_cache()
        return self.get_by_id(deck_id)
    
    def update(self, deck_id, name=None, description=None):
        """Обновить колоду"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if name and description is not None:
            cursor.execute(
                'UPDATE decks SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (name, description, deck_id)
            )
        elif name:
            cursor.execute(
                'UPDATE decks SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (name, deck_id)
            )
        elif description is not None:
            cursor.execute(
                'UPDATE decks SET description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (description, deck_id)
            )
        
        conn.commit()
        conn.close()
        self._clear_cache()
        return self.get_by_id(deck_id)
    
    def delete(self, deck_id):
        """Удалить колоду"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM decks WHERE id = ?', (deck_id,))
        conn.commit()
        conn.close()
        self._clear_cache()
        return True


class CardRepository:
    """Репозиторий для работы с карточками"""
    
    def __init__(self):
        self._cache = {}
    
    def _clear_cache(self):
        """Очистка кэша"""
        self._cache = {}
    
    def get_by_deck(self, deck_id, status_filter=None):
        """Получить карточки колоды с фильтром"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if status_filter and status_filter != 'all':
            cursor.execute(
                'SELECT * FROM cards WHERE deck_id = ? AND status = ? ORDER BY id',
                (deck_id, status_filter)
            )
        else:
            cursor.execute(
                'SELECT * FROM cards WHERE deck_id = ? ORDER BY id',
                (deck_id,)
            )
        
        cards = cursor.fetchall()
        conn.close()
        
        class Card:
            pass
        
        result = []
        for card in cards:
            c = Card()
            c.id = card['id']
            c.deck_id = card['deck_id']
            c.word = card['word']
            c.translation = card['translation']
            c.example = card['example'] if card['example'] else ""
            c.transcription = card['transcription'] if card['transcription'] else ""
            c.status = card['status']
            c.review_count = card['review_count'] if card['review_count'] else 0
            c.last_reviewed_at = card['last_reviewed_at']
            c.correct_percentage = card['correct_percentage'] if card['correct_percentage'] else 0.0
            result.append(c)
        
        return result
    
    def get_by_id(self, card_id):
        """Получить карточку по ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cards WHERE id = ?', (card_id,))
        card = cursor.fetchone()
        conn.close()
        
        if card:
            class Card:
                pass
            
            c = Card()
            c.id = card['id']
            c.deck_id = card['deck_id']
            c.word = card['word']
            c.translation = card['translation']
            c.example = card['example'] if card['example'] else ""
            c.transcription = card['transcription'] if card['transcription'] else ""
            c.status = card['status']
            c.review_count = card['review_count'] if card['review_count'] else 0
            c.last_reviewed_at = card['last_reviewed_at']
            c.correct_percentage = card['correct_percentage'] if card['correct_percentage'] else 0.0
            return c
        return None
    
    def create(self, deck_id, word, translation, example="", transcription=""):
        """Создать новую карточку"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO cards (deck_id, word, translation, example, transcription, status) VALUES (?, ?, ?, ?, ?, ?)',
            (deck_id, word, translation, example, transcription, 'not_studied')
        )
        conn.commit()
        card_id = cursor.lastrowid
        conn.close()
        self._clear_cache()
        return self.get_by_id(card_id)
    
    def update(self, card_id, **kwargs):
        """Обновить карточку"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['word', 'translation', 'example', 'transcription', 'status']:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if updates:
            values.append(card_id)
            cursor.execute(
                f'UPDATE cards SET {", ".join(updates)} WHERE id = ?',
                values
            )
            conn.commit()
        
        conn.close()
        self._clear_cache()
        return self.get_by_id(card_id)
    
    def delete(self, card_id):
        """Удалить карточку"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cards WHERE id = ?', (card_id,))
        conn.commit()
        conn.close()
        self._clear_cache()
        return True
    
    def update_status(self, card_id, status):
        """Обновить статус карточки"""
        conn = get_db_connection()
        cursor = conn.cursor()
        if status == 'studied':
            cursor.execute(
                'UPDATE cards SET status = ?, last_reviewed_at = CURRENT_TIMESTAMP WHERE id = ?',
                (status, card_id)
            )
        else:
            cursor.execute('UPDATE cards SET status = ? WHERE id = ?', (status, card_id))
        conn.commit()
        conn.close()
        self._clear_cache()
    
    def mark_deck_cards_as_studied(self, deck_id):
        """Отметить все карточки колоды как изученные"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE cards SET status = "studied", last_reviewed_at = CURRENT_TIMESTAMP WHERE deck_id = ? AND status != "studied"',
            (deck_id,)
        )
        conn.commit()
        conn.close()
        self._clear_cache()


class StatisticsRepository:
    """Репозиторий для работы со статистикой"""
    
    def __init__(self):
        self._cache = {}
    
    def _clear_cache(self):
        """Очистка кэша"""
        self._cache = {}
    
    def refresh(self):
        """Принудительное обновление статистики"""
        self._clear_cache()
    
    def add_test_result(self, deck_id, total_questions, correct_answers, time_spent=0):
        """Добавление результата теста"""
        conn = get_db_connection()
        cursor = conn.cursor()
        today = date.today().isoformat()
        
        cursor.execute(
            'INSERT INTO test_results (deck_id, test_date, total_questions, correct_answers, time_spent) VALUES (?, ?, ?, ?, ?)',
            (deck_id, today, total_questions, correct_answers, time_spent)
        )
        conn.commit()
        conn.close()
        
        # Обновляем ежедневную статистику
        self.update_daily_stats(correct_answers, total_questions, time_spent)
        self._clear_cache()
    
    def update_daily_stats(self, correct_answers, total_answers, time_spent):
        """Обновление ежедневной статистики"""
        conn = get_db_connection()
        cursor = conn.cursor()
        today = date.today().isoformat()
        
        cursor.execute('''
            INSERT INTO daily_stats (stat_date, cards_studied, correct_answers, total_answers, time_spent)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(stat_date) DO UPDATE SET
                cards_studied = cards_studied + ?,
                correct_answers = correct_answers + ?,
                total_answers = total_answers + ?,
                time_spent = time_spent + ?
        ''', (today, total_answers, correct_answers, total_answers, time_spent,
              total_answers, correct_answers, total_answers, time_spent))
        
        conn.commit()
        conn.close()
        self._clear_cache()
    
    def get_current_streak(self):
        """Получить текущую серию дней (streak)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT stat_date FROM daily_stats ORDER BY stat_date DESC')
        dates = cursor.fetchall()
        conn.close()
        
        if not dates:
            return 0
        
        streak = 0
        current_date = date.today()
        
        for i, row in enumerate(dates):
            try:
                stat_date = datetime.strptime(row['stat_date'], '%Y-%m-%d').date()
                if stat_date == current_date - timedelta(days=i):
                    streak += 1
                else:
                    break
            except:
                break
        
        return streak
    
    def get_total_studied_cards(self):
        """Получить общее количество изученных карточек за все время"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM cards WHERE status = 'studied' AND deck_id IN (SELECT id FROM decks)")
        result = cursor.fetchone()
        conn.close()

        return result[0] if result else 0
    
    def get_studied_cards_period(self, days=7):
        """Получить количество изученных карточек за период"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        start_date = (date.today() - timedelta(days=days)).isoformat()
        cursor.execute('''
            SELECT stat_date, cards_studied 
            FROM daily_stats 
            WHERE stat_date >= ? 
            ORDER BY stat_date
        ''', (start_date,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [(row['stat_date'], row['cards_studied']) for row in results]
    
    def get_today_stats(self):
        """Получить статистику за сегодня"""
        conn = get_db_connection()
        cursor = conn.cursor()
        today = date.today().isoformat()
        
        cursor.execute('SELECT * FROM daily_stats WHERE stat_date = ?', (today,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            correct_percent = (result['correct_answers'] / result['total_answers'] * 100) if result['total_answers'] > 0 else 0
            # time_spent хранится в минутах, преобразуем в секунды для форматирования
            time_minutes = result['time_spent']
            return {
                'cards_studied': result['cards_studied'],
                'correct_percent': round(correct_percent, 1),
                'time_spent_minutes': time_minutes,  # сохраняем минуты отдельно
                'time_spent': time_minutes  # для обратной совместимости
            }
        return {'cards_studied': 0, 'correct_percent': 0, 'time_spent': 0, 'time_spent_minutes': 0}
    
    def get_global_stats(self):
        """Получить глобальную статистику (без кэширования)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM cards WHERE deck_id IN (SELECT id FROM decks)")
        result = cursor.fetchone()
        total_cards = result[0] if result else 0

        cursor.execute("SELECT COUNT(*) FROM cards WHERE status = 'studied' AND deck_id IN (SELECT id FROM decks)")
        result = cursor.fetchone()
        studied_cards = result[0] if result else 0
        
        conn.close()
        
        percent = (studied_cards / total_cards * 100) if total_cards > 0 else 0
        
        return {
            'total_cards': total_cards,
            'studied_cards': studied_cards,
            'remaining_cards': total_cards - studied_cards,
            'percent': round(percent, 1)
        }

    def force_refresh_all(self):
        """Принудительное обновление всех данных"""
        self._clear_cache()

# Инициализируем базу данных при первом импорте
init_db()