"""
Tests for the CLI modules.
"""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from mulligan_simulator.cli import main
from mulligan_simulator.db_cli import db


class TestMainCLI:
    """Test the main CLI."""
    
    def test_cli_with_file(self, sample_deck_file):
        """Test CLI with file input."""
        runner = CliRunner()
        
        with patch('mulligan_simulator.cli.MulliganSimulator') as mock_simulator_class:
            mock_simulator = MagicMock()
            mock_simulator_class.from_text.return_value = mock_simulator
            mock_simulator.deck = ["card1", "card2"] * 40  # 80 cards
            mock_simulator.run_simulation.return_value = None
            
            result = runner.invoke(main, ['--file', sample_deck_file, '--hands', '1', '--no-db'])
            
            assert result.exit_code == 0
            mock_simulator_class.from_text.assert_called_once()
            mock_simulator.run_simulation.assert_called_once_with(1)
    
    def test_cli_with_url(self):
        """Test CLI with URL input."""
        runner = CliRunner()
        
        with patch('mulligan_simulator.cli.MulliganSimulator') as mock_simulator_class:
            mock_simulator = MagicMock()
            mock_simulator_class.from_url.return_value = mock_simulator
            mock_simulator.deck = ["card1", "card2"] * 40  # 80 cards
            mock_simulator.run_simulation.return_value = None
            
            result = runner.invoke(main, ['--url', 'https://example.com/deck', '--hands', '1', '--no-db'])
            
            assert result.exit_code == 0
            mock_simulator_class.from_url.assert_called_once()
            mock_simulator.run_simulation.assert_called_once_with(1)
    
    def test_cli_without_input(self):
        """Test CLI without file or URL."""
        runner = CliRunner()
        
        result = runner.invoke(main, ['--hands', '1'])
        
        assert result.exit_code == 0
        assert "Error: Must provide either --url or --file" in result.output
    
    def test_cli_with_save_option(self, sample_deck_file):
        """Test CLI with save option."""
        runner = CliRunner()
        
        with patch('mulligan_simulator.cli.MulliganSimulator') as mock_simulator_class:
            mock_simulator = MagicMock()
            mock_simulator_class.from_text.return_value = mock_simulator
            mock_simulator.deck = ["card1", "card2"] * 40  # 80 cards
            mock_simulator.run_simulation.return_value = None
            mock_simulator.save_results.return_value = None
            
            result = runner.invoke(main, ['--file', sample_deck_file, '--hands', '1', '--save', 'test.json', '--no-db'])
            
            assert result.exit_code == 0
            mock_simulator.save_results.assert_called_once_with('test.json')
    
    def test_cli_with_deck_name(self, sample_deck_file):
        """Test CLI with deck name."""
        runner = CliRunner()
        
        with patch('mulligan_simulator.cli.MulliganSimulator') as mock_simulator_class:
            mock_simulator = MagicMock()
            mock_simulator_class.from_text.return_value = mock_simulator
            mock_simulator.deck = ["card1", "card2"] * 40  # 80 cards
            mock_simulator.run_simulation.return_value = None
            
            result = runner.invoke(main, ['--file', sample_deck_file, '--hands', '1', '--deck-name', 'My Deck', '--no-db'])
            
            assert result.exit_code == 0
            mock_simulator_class.from_text.assert_called_once()
            # Check that deck_name was passed
            call_args = mock_simulator_class.from_text.call_args
            assert call_args[1]['deck_name'] == 'My Deck'


class TestDatabaseCLI:
    """Test the database CLI."""
    
    def test_db_init_command(self):
        """Test the db init command."""
        runner = CliRunner()
        
        with patch('mulligan_simulator.db_cli.create_tables') as mock_create_tables:
            result = runner.invoke(db, ['init'])
            
            assert result.exit_code == 0
            assert "Database tables created successfully" in result.output or "All required tables exist" in result.output
            mock_create_tables.assert_called_once() if "Database tables created successfully" in result.output else mock_create_tables.assert_not_called()
    
    def test_db_drop_command(self):
        """Test the db drop command."""
        runner = CliRunner()
        
        with patch('mulligan_simulator.db_cli.drop_tables') as mock_drop_tables:
            result = runner.invoke(db, ['drop'])
            
            assert result.exit_code == 0
            assert "Database tables dropped successfully" in result.output
            mock_drop_tables.assert_called_once()
    
    def test_db_list_runs_command(self):
        """Test the db list-runs command."""
        runner = CliRunner()
        
        with patch('mulligan_simulator.db_cli.DatabaseService') as mock_db_service_class:
            mock_db_service = MagicMock()
            mock_db_service_class.return_value = mock_db_service
            mock_db_service.get_simulation_runs.return_value = [
                {
                    'id': 'test-id',
                    'created_at': '2024-01-01T12:00:00',
                    'deck_name': 'Test Deck',
                    'total_hands': 10,
                    'deck_source': 'test_url'
                }
            ]
            
            result = runner.invoke(db, ['list-runs', '--limit', '5'])
            
            assert result.exit_code == 0
            mock_db_service.get_simulation_runs.assert_called_once_with(limit=5)
            mock_db_service.close.assert_called_once()
    
    def test_db_show_run_command(self):
        """Test the db show-run command."""
        runner = CliRunner()
        
        with patch('mulligan_simulator.db_cli.DatabaseService') as mock_db_service_class:
            mock_db_service = MagicMock()
            mock_db_service_class.return_value = mock_db_service
            mock_db_service.get_simulation_run.return_value = {
                'id': 'test-id',
                'deck_name': 'Test Deck',
                'deck_source': 'test_url',
                'total_hands': 10,
                'created_at': '2024-01-01T12:00:00',
                'user_name': 'Test User',
                'notes': 'Test notes',
                'hand_results': []
            }
            
            result = runner.invoke(db, ['show-run', 'test-id'])
            
            assert result.exit_code == 0
            mock_db_service.get_simulation_run.assert_called_once_with('test-id')
            mock_db_service.close.assert_called_once()
    
    def test_db_stats_command(self):
        """Test the db stats command."""
        runner = CliRunner()
        
        with patch('mulligan_simulator.db_cli.DatabaseService') as mock_db_service_class:
            mock_db_service = MagicMock()
            mock_db_service_class.return_value = mock_db_service
            mock_db_service.get_simulation_stats.return_value = {
                'total_hands': 10,
                'keep_count': 7,
                'mulligan_count': 3,
                'keep_rate': 0.7,
                'play_count': 5,
                'draw_count': 5,
                'play_rate': 0.5,
                'mulligan_distribution': {1: 5, 2: 3, 3: 2}
            }
            
            result = runner.invoke(db, ['stats', 'test-id'])
            
            assert result.exit_code == 0
            mock_db_service.get_simulation_stats.assert_called_once_with('test-id')
            mock_db_service.close.assert_called_once()
