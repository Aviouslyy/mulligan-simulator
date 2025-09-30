"""
Tests for the database module.
"""

import pytest
from unittest.mock import patch, MagicMock
from mulligan_simulator.database import create_tables, drop_tables, get_db
from mulligan_simulator.db_service import DatabaseService
from mulligan_simulator.models import HandResult


class TestDatabaseService:
    """Test the DatabaseService class."""
    
    @patch('mulligan_simulator.db_service.SessionLocal')
    def test_save_simulation_run(self, mock_session_local):
        """Test saving a simulation run."""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        
        # Mock the simulation run object
        mock_run = MagicMock()
        mock_run.id = "test-run-id"
        
        # Mock the session methods
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.commit.return_value = None
        
        # Create a real DatabaseService instance
        db_service = DatabaseService()
        db_service.session = mock_session
        
        # Create test data
        hand_results = [
            HandResult(
                hand_number=1,
                seed=12345,
                cards_in_hand=7,
                cards=["Lightning Bolt", "Mountain"],
                play_or_draw="play",
                mulligan_number=1,
                user_decision="keep"
            )
        ]
        
        decklist = [
            {"name": "Lightning Bolt", "quantity": 4, "type": None, "mana_cost": None}
        ]
        
        # Mock the SimulationRun creation
        with patch('mulligan_simulator.db_service.SimulationRun') as mock_simulation_run_class:
            mock_simulation_run_class.return_value = mock_run
            
            run_id = db_service.save_simulation_run(
                deck_source="test_url",
                deck_name="Test Deck",
                total_hands=1,
                hand_results=hand_results,
                decklist=decklist
            )
            
            assert run_id == "test-run-id"
            mock_session.add.assert_called()
            mock_session.flush.assert_called()
            mock_session.commit.assert_called()
    
    @patch('mulligan_simulator.db_service.SessionLocal')
    def test_save_simulation_run_rollback_on_error(self, mock_session_local):
        """Test that rollback is called on error."""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_session.commit.side_effect = Exception("Database error")
        
        db_service = DatabaseService()
        
        with pytest.raises(Exception, match="Database error"):
            db_service.save_simulation_run(
                deck_source="test_url",
                deck_name="Test Deck",
                total_hands=1,
                hand_results=[],
                decklist=[]
            )
        
        mock_session.rollback.assert_called()
    
    @patch('mulligan_simulator.db_service.SessionLocal')
    def test_get_simulation_runs(self, mock_session_local):
        """Test getting simulation runs."""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        
        # Mock query results
        mock_run = MagicMock()
        mock_run.id = "test-run-id"
        mock_run.created_at = "2024-01-01T12:00:00"
        mock_run.deck_source = "test_url"
        mock_run.deck_name = "Test Deck"
        mock_run.total_hands = 10
        mock_run.user_name = "Test User"
        mock_run.notes = "Test notes"
        
        mock_query = MagicMock()
        mock_query.order_by.return_value.limit.return_value.all.return_value = [mock_run]
        mock_session.query.return_value = mock_query
        
        db_service = DatabaseService()
        runs = db_service.get_simulation_runs(limit=10)
        
        assert len(runs) == 1
        assert runs[0]["id"] == "test-run-id"
        assert runs[0]["deck_name"] == "Test Deck"
    
    @patch('mulligan_simulator.db_service.SessionLocal')
    def test_get_simulation_run_not_found(self, mock_session_local):
        """Test getting a simulation run that doesn't exist."""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        db_service = DatabaseService()
        result = db_service.get_simulation_run("nonexistent-id")
        
        assert result is None
    
    @patch('mulligan_simulator.db_service.SessionLocal')
    def test_get_simulation_stats(self, mock_session_local):
        """Test getting simulation statistics."""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        
        # Mock hand results
        mock_hand1 = MagicMock()
        mock_hand1.user_decision = "keep"
        mock_hand1.play_or_draw = "play"
        mock_hand1.mulligan_number = 1
        
        mock_hand2 = MagicMock()
        mock_hand2.user_decision = "mulligan"
        mock_hand2.play_or_draw = "draw"
        mock_hand2.mulligan_number = 2
        
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = [mock_hand1, mock_hand2]
        mock_session.query.return_value = mock_query
        
        db_service = DatabaseService()
        stats = db_service.get_simulation_stats("test-run-id")
        
        assert stats["total_hands"] == 2
        assert stats["keep_count"] == 1
        assert stats["mulligan_count"] == 1
        assert stats["keep_rate"] == 0.5
        assert stats["play_count"] == 1
        assert stats["draw_count"] == 1
        assert stats["play_rate"] == 0.5
        assert 1 in stats["mulligan_distribution"]
        assert 2 in stats["mulligan_distribution"]


class TestDatabaseFunctions:
    """Test database utility functions."""
    
    @patch('mulligan_simulator.database.Base.metadata.create_all')
    def test_create_tables(self, mock_create_all):
        """Test creating database tables."""
        create_tables()
        mock_create_all.assert_called_once()
    
    @patch('mulligan_simulator.database.Base.metadata.drop_all')
    def test_drop_tables(self, mock_drop_all):
        """Test dropping database tables."""
        drop_tables()
        mock_drop_all.assert_called_once()
    
    def test_get_db(self):
        """Test getting database session."""
        with patch('mulligan_simulator.database.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session
            
            db_gen = get_db()
            db = next(db_gen)
            
            assert db == mock_session
            
            # Test that close is called when the generator is exhausted
            try:
                next(db_gen)
            except StopIteration:
                pass
            
            mock_session.close.assert_called()
