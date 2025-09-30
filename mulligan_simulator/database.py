"""
Database models and connection setup for the mulligan simulator.
"""

import os
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://mulligan_user:mulligan_password@localhost:5432/mulligan_simulator"
)

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SimulationRun(Base):
    """Represents a complete simulation session."""
    __tablename__ = "simulation_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    deck_source = Column(String(500))  # URL or file path
    deck_name = Column(String(200))
    total_hands = Column(Integer)
    user_name = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    hands = relationship("HandResult", back_populates="simulation_run", cascade="all, delete-orphan")


class HandResult(Base):
    """Represents a single hand result within a simulation."""
    __tablename__ = "hand_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_run_id = Column(UUID(as_uuid=True), ForeignKey("simulation_runs.id"))
    hand_number = Column(Integer)
    seed = Column(Integer)
    cards_in_hand = Column(Integer)
    cards = Column(JSON)  # List of card names
    play_or_draw = Column(String(10))  # "play" or "draw"
    mulligan_number = Column(Integer)
    user_decision = Column(String(20))  # "keep" or "mulligan"
    cards_to_put_bottom = Column(JSON, nullable=True)  # List of cards put on bottom
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    simulation_run = relationship("SimulationRun", back_populates="hands")


class DeckCard(Base):
    """Represents cards in a deck for analysis."""
    __tablename__ = "deck_cards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_run_id = Column(UUID(as_uuid=True), ForeignKey("simulation_runs.id"))
    card_name = Column(String(200))
    quantity = Column(Integer)
    card_type = Column(String(50), nullable=True)  # "land", "creature", "spell", etc.
    mana_cost = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)
