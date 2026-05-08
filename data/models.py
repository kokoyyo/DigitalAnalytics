from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class Deck(Base):
    __tablename__ = 'decks'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    cards = relationship("Card", back_populates="deck", cascade="all, delete-orphan")

class Card(Base):
    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True)
    word = Column(String)
    translation = Column(String)
    example = Column(String, nullable=True)
    transcription = Column(String, nullable=True)
    status = Column(String)  # not_studied / studied / for_review
    deck_id = Column(Integer, ForeignKey('decks.id'))
    deck = relationship("Deck", back_populates="cards")