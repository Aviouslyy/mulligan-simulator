"""
Tests for the models module.
"""

import pytest
from datetime import datetime
from mulligan_simulator.models import HandResult


class TestHandResult:
    """Test the HandResult model."""
    
    def test_hand_result_creation(self):
        """Test creating a HandResult instance."""
        result = HandResult(
            hand_number=1,
            seed=12345,
            cards_in_hand=7,
            cards=["Lightning Bolt", "Mountain", "Goblin Guide"],
            play_or_draw="play",
            mulligan_number=1,
            user_decision="keep"
        )
        
        assert result.hand_number == 1
        assert result.seed == 12345
        assert result.cards_in_hand == 7
        assert result.cards == ["Lightning Bolt", "Mountain", "Goblin Guide"]
        assert result.play_or_draw == "play"
        assert result.mulligan_number == 1
        assert result.user_decision == "keep"
        assert result.cards_to_keep is None
        assert result.timestamp == ""
    
    def test_hand_result_with_optional_fields(self):
        """Test creating a HandResult with optional fields."""
        result = HandResult(
            hand_number=2,
            seed=67890,
            cards_in_hand=6,
            cards=["Lightning Bolt", "Mountain", "Goblin Guide", "Mountain", "Lightning Bolt", "Mountain"],
            play_or_draw="draw",
            mulligan_number=2,
            user_decision="mulligan",
            cards_to_keep=["Lightning Bolt", "Goblin Guide"],
            timestamp="2024-01-01T12:00:00"
        )
        
        assert result.cards_to_keep == ["Lightning Bolt", "Goblin Guide"]
        assert result.timestamp == "2024-01-01T12:00:00"
    
    def test_hand_result_defaults(self):
        """Test HandResult with default values."""
        result = HandResult(
            hand_number=1,
            seed=123,
            cards_in_hand=7,
            cards=["Card1"],
            play_or_draw="play",
            mulligan_number=1,
            user_decision="keep"
        )
        
        assert result.cards_to_keep is None
        assert result.timestamp == ""
