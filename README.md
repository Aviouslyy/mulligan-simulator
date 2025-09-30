# Magic: The Gathering Mulligan Simulator

An interactive tool for simulating Magic: The Gathering mulligans and recording user decisions.

## Features

- **Interactive Simulation**: Shows random hands and records your decisions
- **Decklist Support**: Load decklists from URLs or text files using [mtg-parser](https://github.com/lheyberger/mtg-parser)
- **Decision Recording**: Tracks whether you keep or mulligan each hand
- **Mulligan States**: Simulates different mulligan scenarios (60% 7 cards, 30% 6 cards, 10% 5 cards)
- **Play/Draw**: Randomly determines if you're on the play or draw
- **Database Storage**: PostgreSQL database to track all simulation runs
- **Results Export**: Save your decisions to JSON for analysis
- **Docker Support**: Easy setup with Docker Compose

## Installation

### Option 1: Docker Setup (Recommended)

```bash
# Start the database
docker-compose up -d postgres

# Install dependencies
poetry install

# Setup the database
poetry run python setup_db.py
```

### Option 2: Local Setup

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Setup PostgreSQL locally and run:
poetry run python setup_db.py
```

## Usage

### Command Line Interface

```bash
# Simulate with a decklist URL
poetry run mulligan-simulator --url "https://www.moxfield.com/decks/your-deck-id" --hands 20

# Simulate with a local decklist file
poetry run mulligan-simulator --file "my_deck.txt" --hands 10

# Save results to a file (in addition to database)
poetry run mulligan-simulator --file example_deck.txt --hands 15 --save "results.json"

# Skip database saving
poetry run mulligan-simulator --file example_deck.txt --hands 10 --no-db

# Set a custom deck name
poetry run mulligan-simulator --file example_deck.txt --hands 10 --deck-name "My Burn Deck"
```

### Python API

```python
from mulligan_simulator import MulliganSimulator

# Load from URL
simulator = MulliganSimulator.from_url("https://www.moxfield.com/decks/your-deck-id")

# Load from text
decklist_text = """
4 Lightning Bolt
4 Counterspell
4 Brainstorm
...
"""
simulator = MulliganSimulator.from_text(decklist_text)

# Run simulation
simulator.run_simulation(num_hands=10)

# Save results
simulator.save_results("my_results.json")
```

### Database Management

```bash
# Initialize the database (auto-creates tables if missing)
poetry run python setup_db.py

# Or use the database CLI
poetry run python -m mulligan_simulator.db_cli init

# Check database status
poetry run python -m mulligan_simulator.db_cli status

# Verify database is ready
poetry run python -m mulligan_simulator.db_cli check

# List recent simulation runs
poetry run python -m mulligan_simulator.db_cli list-runs

# Show details of a specific run
poetry run python -m mulligan_simulator.db_cli show-run <run-id>

# Show statistics for a run
poetry run python -m mulligan_simulator.db_cli stats <run-id>

# Drop all database tables (careful!)
poetry run python -m mulligan_simulator.db_cli drop
```

## How It Works

1. **Load Decklist**: The simulator loads your deck from a URL or text file
2. **Generate Hands**: For each simulation, it:
   - Generates a random seed
   - Determines mulligan state (60% 7 cards, 30% 6 cards, 10% 5 cards)
   - Randomly determines play or draw
   - Draws a random hand from your deck
3. **Show Hand**: Displays the hand with card numbers
4. **Record Decision**: Asks if you want to keep or mulligan
5. **Track Cards**: If mulliganing, asks which cards you'd keep
6. **Save Results**: Optionally saves all decisions to a JSON file

## Supported Decklist Sources

- Moxfield.com
- Archidekt.com
- MTGGoldfish.com
- TappedOut.net
- Deckstats.net
- MTGO/MTGA text format
- And more (see [mtg-parser documentation](https://github.com/lheyberger/mtg-parser))

## Example Output

```
🎯 Starting Mulligan Simulation with 5 hands
==================================================

📋 Hand #1
------------------------------
🎲 Seed: 123456
🎯 On the: PLAY
🔄 Mulligan: #1 (7 cards)
🃏 Your hand:
  1. Lightning Bolt
  2. Mountain
  3. Goblin Guide
  4. Mountain
  5. Lightning Bolt
  6. Mountain
  7. Goblin Guide

🤔 Decision (keep/mulligan): keep
✅ Recorded: KEEP
```

## Results Format

Results are saved as JSON with the following structure:

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "total_hands": 10,
  "results": [
    {
      "hand_number": 1,
      "seed": 123456,
      "cards_in_hand": 7,
      "cards": ["Lightning Bolt", "Mountain", ...],
      "play_or_draw": "play",
      "mulligan_number": 1,
      "user_decision": "keep",
      "cards_to_keep": null,
      "timestamp": "2024-01-01T12:00:00"
    }
  ]
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.