"""
Pytest configuration and fixtures for the mulligan simulator tests.
"""

import pytest
import tempfile
import os
from mulligan_simulator import MulliganSimulator
from mulligan_simulator.models import HandResult


@pytest.fixture
def sample_decklist():
    """Sample decklist for testing."""
    return """
4 Lightning Bolt
4 Goblin Guide
4 Monastery Swiftspear
4 Eidolon of the Great Revel
4 Lava Spike
4 Rift Bolt
4 Searing Blaze
4 Skullcrack
4 Lightning Helix
4 Boros Charm
4 Path to Exile
4 Arid Mesa
4 Scalding Tarn
4 Sacred Foundry
4 Mountain
4 Plains
4 Inspiring Vantage
4 Sunbaked Canyon
4 Fiery Islet
4 Horizon Canopy
"""


@pytest.fixture
def sample_deck_file(sample_decklist):
    """Create a temporary deck file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_decklist)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def simulator(sample_decklist):
    """Create a simulator instance for testing."""
    return MulliganSimulator.from_text(sample_decklist, deck_name="Test Deck")


@pytest.fixture
def sample_hand_result():
    """Sample hand result for testing."""
    return HandResult(
        hand_number=1,
        seed=12345,
        cards_in_hand=7,
        cards=["Lightning Bolt", "Mountain", "Goblin Guide", "Mountain", "Lightning Bolt", "Mountain", "Goblin Guide"],
        play_or_draw="play",
        mulligan_number=1,
        user_decision="keep",
        cards_to_keep=None,
        timestamp="2024-01-01T12:00:00"
    )
