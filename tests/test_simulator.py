"""
Tests for the simulator module.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from mulligan_simulator import MulliganSimulator
from mulligan_simulator.models import HandResult


class TestMulliganSimulator:
    """Test the MulliganSimulator class."""
    
    def test_simulator_creation_from_text(self, sample_decklist):
        """Test creating a simulator from text."""
        simulator = MulliganSimulator.from_text(sample_decklist, deck_name="Test Deck")
        
        assert len(simulator.deck) == 80  # 20 cards * 4 copies each
        assert simulator.deck_name == "Test Deck"
        assert simulator.deck_source == "text_input"
        assert len(simulator.results) == 0
    
    def test_simulator_creation_from_file(self, sample_deck_file):
        """Test creating a simulator from file."""
        with open(sample_deck_file, 'r') as f:
            decklist_text = f.read()
        
        simulator = MulliganSimulator.from_text(decklist_text, deck_name="File Deck")
        
        assert len(simulator.deck) == 80
        assert simulator.deck_name == "File Deck"
    
    def test_build_deck(self, simulator):
        """Test the _build_deck method."""
        assert len(simulator.deck) == 80
        assert "Lightning Bolt" in simulator.deck
        assert "Mountain" in simulator.deck
        assert "Goblin Guide" in simulator.deck
        
        # Check that cards appear the correct number of times
        assert simulator.deck.count("Lightning Bolt") == 4
        assert simulator.deck.count("Mountain") == 4
        assert simulator.deck.count("Goblin Guide") == 4
    
    def test_empty_decklist_raises_error(self):
        """Test that empty decklist raises ValueError."""
        with pytest.raises(ValueError, match="Decklist is empty"):
            MulliganSimulator.from_text("")
    
    def test_display_hand(self, simulator, capsys):
        """Test the _display_hand method."""
        hand = ["Lightning Bolt", "Mountain", "Goblin Guide", "Mountain", "Lightning Bolt", "Mountain", "Goblin Guide"]
        
        simulator._display_hand(hand, "play", 1, 7)
        
        captured = capsys.readouterr()
        assert "Your hand (7 cards):" in captured.out
        assert "1. Lightning Bolt" in captured.out
        assert "2. Mountain" in captured.out
        assert "3. Goblin Guide" in captured.out
    
    def test_get_user_decision_keep(self, simulator):
        """Test getting user decision to keep."""
        with patch('builtins.input', return_value='keep'):
            decision = simulator._get_user_decision()
            assert decision == "keep"
    
    def test_get_user_decision_mulligan(self, simulator):
        """Test getting user decision to mulligan."""
        with patch('builtins.input', return_value='mulligan'):
            decision = simulator._get_user_decision()
            assert decision == "mulligan"
    
    def test_get_user_decision_shortcuts(self, simulator):
        """Test getting user decision with shortcuts."""
        with patch('builtins.input', return_value='k'):
            decision = simulator._get_user_decision()
            assert decision == "keep"
        
        with patch('builtins.input', return_value='m'):
            decision = simulator._get_user_decision()
            assert decision == "mulligan"
    
    def test_get_cards_to_put_bottom(self, simulator):
        """Test getting cards to put on bottom."""
        hand = ["Lightning Bolt", "Mountain", "Goblin Guide", "Mountain", "Lightning Bolt", "Mountain", "Goblin Guide"]
        
        with patch('builtins.input', return_value='2 4'):
            cards_to_put_bottom = simulator._get_cards_to_put_bottom(hand, 5)
            # Cards at positions 2 and 4 (1-indexed) are Mountain and Lightning Bolt
            # Position 2 (index 1): Mountain, Position 4 (index 3): Mountain
            assert cards_to_put_bottom == ["Mountain", "Mountain"]
    
    def test_get_cards_to_put_bottom_invalid_count(self, simulator):
        """Test getting cards to put on bottom with invalid count."""
        hand = ["Lightning Bolt", "Mountain", "Goblin Guide", "Mountain", "Lightning Bolt", "Mountain", "Goblin Guide"]
        
        with patch('builtins.input', side_effect=['1', '1 2 3']):  # First invalid (1 card), then valid (3 cards)
            cards_to_put_bottom = simulator._get_cards_to_put_bottom(hand, 4)  # Need 3 cards on bottom
            assert cards_to_put_bottom == ["Lightning Bolt", "Mountain", "Goblin Guide"]
    
    def test_count_lands(self, simulator):
        """Test counting lands in a hand."""
        hand = ["Lightning Bolt", "Mountain", "Goblin Guide", "Mountain", "Lightning Bolt", "Mountain", "Goblin Guide"]
        land_count = simulator._count_lands(hand)
        assert land_count == 3  # 3 Mountains
    
    def test_save_results(self, simulator, sample_hand_result, tmp_path):
        """Test saving results to JSON file."""
        simulator.results = [sample_hand_result]
        
        filename = tmp_path / "test_results.json"
        simulator.save_results(str(filename))
        
        assert filename.exists()
        
        import json
        with open(filename) as f:
            data = json.load(f)
        
        assert data["total_hands"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["hand_number"] == 1
    
    @patch('mulligan_simulator.simulator.DatabaseService')
    def test_save_to_database_success(self, mock_db_service, simulator, sample_hand_result):
        """Test successful database saving."""
        mock_service = MagicMock()
        mock_service.save_simulation_run.return_value = "test-run-id"
        mock_db_service.return_value = mock_service
        
        # Replace the db_service instance
        simulator.db_service = mock_service
        
        simulator.results = [sample_hand_result]
        simulator._save_to_database(1)
        
        mock_service.save_simulation_run.assert_called_once()
    
    @patch('mulligan_simulator.simulator.DatabaseService')
    def test_save_to_database_failure(self, mock_db_service, simulator, sample_hand_result, capsys):
        """Test database saving failure."""
        mock_service = MagicMock()
        mock_service.save_simulation_run.side_effect = Exception("Database error")
        mock_db_service.return_value = mock_service
        
        # Replace the db_service instance
        simulator.db_service = mock_service
        
        simulator.results = [sample_hand_result]
        simulator._save_to_database(1)
        
        captured = capsys.readouterr()
        assert "Warning: Could not save to database" in captured.out
        assert "Database error" in captured.out
