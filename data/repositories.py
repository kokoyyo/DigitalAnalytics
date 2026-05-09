"""Репозитории для работы с базой данных"""

from sqlalchemy.orm import Session
from data.database import get_session, Deck, Card
from datetime import datetime


class DeckRepository:
    """Репозиторий для работы с колодами"""
    
    def __init__(self):
        self.session: Session = get_session()
    
    def get_all(self):
        """Получить все колоды"""
        return self.session.query(Deck).all()
    
    def get_by_id(self, deck_id):
        """Получить колоду по ID"""
        return self.session.query(Deck).filter(Deck.id == deck_id).first()
    
    def create(self, name, description=""):
        """Создать новую колоду"""
        deck = Deck(name=name, description=description)
        self.session.add(deck)
        self.session.commit()
        return deck
    
    def update(self, deck_id, name=None, description=None):
        """Обновить колоду"""
        deck = self.get_by_id(deck_id)
        if deck:
            if name:
                deck.name = name
            if description is not None:
                deck.description = description
            deck.updated_at = datetime.now()
            self.session.commit()
        return deck
    
    def delete(self, deck_id):
        """Удалить колоду"""
        deck = self.get_by_id(deck_id)
        if deck:
            self.session.delete(deck)
            self.session.commit()
            return True
        return False
    
    def close(self):
        self.session.close()


class CardRepository:
    """Репозиторий для работы с карточками"""
    
    def __init__(self):
        self.session: Session = get_session()
    
    def get_by_deck(self, deck_id, status_filter=None):
        """Получить карточки колоды с фильтром по статусу"""
        query = self.session.query(Card).filter(Card.deck_id == deck_id)
        if status_filter and status_filter != 'all':
            query = query.filter(Card.status == status_filter)
        return query.all()
    
    def get_by_id(self, card_id):
        """Получить карточку по ID"""
        return self.session.query(Card).filter(Card.id == card_id).first()
    
    def create(self, deck_id, word, translation, example="", transcription=""):
        """Создать новую карточку"""
        card = Card(
            deck_id=deck_id,
            word=word,
            translation=translation,
            example=example,
            transcription=transcription,
            status="not_studied"
        )
        self.session.add(card)
        self.session.commit()
        return card
    
    def update(self, card_id, **kwargs):
        """Обновить карточку"""
        card = self.get_by_id(card_id)
        if card:
            for key, value in kwargs.items():
                if hasattr(card, key):
                    setattr(card, key, value)
            self.session.commit()
        return card
    
    def delete(self, card_id):
        """Удалить карточку"""
        card = self.get_by_id(card_id)
        if card:
            self.session.delete(card)
            self.session.commit()
            return True
        return False
    
    def update_status(self, card_id, status):
        """Обновить статус карточки"""
        return self.update(card_id, status=status)
    
    def close(self):
        self.session.close()