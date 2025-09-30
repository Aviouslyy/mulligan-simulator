#!/usr/bin/env python3
"""
Example usage of the Mulligan Simulator.

This script demonstrates how to use the simulator with different decklist sources.
"""

from mulligan_simulator import MulliganSimulator


def example_with_text_decklist():
    """Example using a text decklist."""
    print("=== Example: Text Decklist ===")
    
    # Sample decklist in text format
    decklist_text = """
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
    
    try:
        simulator = MulliganSimulator.from_text(decklist_text)
        print(f"✅ Loaded deck with {len(simulator.deck)} cards")
        
        # Run a small simulation
        simulator.run_simulation(num_hands=3)
        
        # Save results
        simulator.save_results("example_results.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_with_url():
    """Example using a decklist URL."""
    print("\n=== Example: URL Decklist ===")
    
    # Note: Replace with an actual decklist URL
    deck_url = "https://www.moxfield.com/decks/example-deck-id"
    
    try:
        print(f"📥 Loading decklist from URL: {deck_url}")
        simulator = MulliganSimulator.from_url(deck_url)
        print(f"✅ Loaded deck with {len(simulator.deck)} cards")
        
        # Run simulation
        simulator.run_simulation(num_hands=5)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the URL points to a valid decklist")


if __name__ == "__main__":
    print("🎯 Mulligan Simulator Examples")
    print("=" * 40)
    
    # Run text decklist example
    example_with_text_decklist()
    
    # Uncomment to try URL example (requires valid URL)
    # example_with_url()
    
    print("\n✅ Examples completed!")
    print("💡 Try running: poetry run mulligan-simulator --file example_deck.txt --hands 10")
