"""Настройка SQLite базы данных и модели"""

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Создаем базовый класс для моделей
Base = declarative_base()


class Deck(Base):
    """Модель колоды (модуля) с карточками"""
    __tablename__ = 'decks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), default="")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Связь с карточками
    cards = relationship("Card", back_populates="deck", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Deck(id={self.id}, name='{self.name}')>"


class Card(Base):
    """Модель флеш-карточки"""
    __tablename__ = 'cards'
    
    id = Column(Integer, primary_key=True)
    word = Column(String(200), nullable=False)
    translation = Column(String(200), nullable=False)
    example = Column(String(500), default="")
    transcription = Column(String(100), default="")
    status = Column(String(50), default="not_studied")  # not_studied, studied, for_review
    
    # Внешний ключ к колоде
    deck_id = Column(Integer, ForeignKey('decks.id'), nullable=False)
    
    # Связь с колодой
    deck = relationship("Deck", back_populates="cards")
    
    # Статистика повторений
    review_count = Column(Integer, default=0)
    last_reviewed_at = Column(DateTime, nullable=True)
    correct_percentage = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<Card(id={self.id}, word='{self.word}')>"


# Настройка подключения к базе данных
DATABASE_URL = "sqlite:///flashcard.db"

# Создаем движок
engine = create_engine(DATABASE_URL, echo=False)

# Создаем все таблицы
Base.metadata.create_all(engine)

# Фабрика сессий
SessionLocal = sessionmaker(bind=engine)


def get_session():
    """Получить сессию для работы с БД"""
    return SessionLocal()


def init_db():
    """Инициализация БД (создание таблиц)"""
    Base.metadata.create_all(engine)
    print("База данных инициализирована")