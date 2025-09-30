"""
Command line interface for the mulligan simulator.
"""

import click
from .simulator import MulliganSimulator


@click.command()
@click.option('--url', '-u', help='URL to a decklist')
@click.option('--file', '-f', help='Path to a decklist file')
@click.option('--hands', '-n', default=10, help='Number of hands to simulate')
@click.option('--save', '-s', help='Save results to file (JSON format)')
@click.option('--deck-name', help='Name for the deck')
@click.option('--no-db', is_flag=True, help='Skip database saving')
def main(url, file, hands, save, deck_name, no_db):
    """
    Magic: The Gathering Mulligan Simulator
    
    Interactive tool for simulating mulligans and recording user decisions.
    """
    try:
        # Create simulator
        if url:
            print(f"📥 Loading decklist from URL: {url}")
            simulator = MulliganSimulator.from_url(url, deck_name=deck_name or "")
        elif file:
            print(f"📥 Loading decklist from file: {file}")
            with open(file, 'r') as f:
                decklist_text = f.read()
            simulator = MulliganSimulator.from_text(decklist_text, deck_name=deck_name or "")
        else:
            print("❌ Error: Must provide either --url or --file")
            return
        
        print(f"✅ Loaded deck with {len(simulator.deck)} cards")
        
        # Run simulation
        simulator.run_simulation(hands)
        
        # Save results if requested
        if save:
            simulator.save_results(save)
        
        # Skip database saving if requested
        if no_db:
            print("⚠️  Database saving skipped (--no-db flag)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if click.get_current_context().params.get('verbose'):
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
