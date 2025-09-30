"""
Interactive mulligan simulator that records user decisions.
"""

import random
import json
from typing import List, Dict, Any, Optional
from dataclasses import asdict
from datetime import datetime

import mtg_parser
from .models import HandResult
from .db_service import DatabaseService


class MulliganSimulator:
    """
    Interactive mulligan simulator that shows hands and records user decisions.
    """
    
    def __init__(self, decklist: List[mtg_parser.Card], deck_source: str = "", deck_name: str = ""):
        """
        Initialize the simulator with a decklist.
        
        Args:
            decklist: List of Card objects from mtg_parser
            deck_source: Source of the deck (URL or file path)
            deck_name: Name of the deck
        """
        self.decklist = decklist
        self.deck_source = deck_source
        self.deck_name = deck_name
        self.results: List[HandResult] = []
        self.db_service = DatabaseService()
        self._build_deck()
    
    def _build_deck(self) -> None:
        """Build the deck list for simulation."""
        self.deck = []
        for card in self.decklist:
            for _ in range(card.quantity):
                self.deck.append(card.name)
        
        if not self.deck:
            raise ValueError("Decklist is empty")
    
    def run_simulation(self, num_hands: int) -> None:
        """
        Run the interactive simulation.
        
        Args:
            num_hands: Number of hands to simulate
        """
        print(f"\n🎯 Starting Mulligan Simulation with {num_hands} hands")
        print("=" * 50)
        
        for hand_num in range(1, num_hands + 1):
            print(f"\n📋 Hand #{hand_num}")
            print("-" * 30)
            
            # Generate random seed
            seed = random.randint(1, 1000000)
            random.seed(seed)
            
            # Determine mulligan state (60% 7 cards, 30% 6 cards, 10% 5 cards)
            mulligan_roll = random.random()
            if mulligan_roll < 0.6:
                final_cards_in_hand = 7
                mulligan_number = 1
            elif mulligan_roll < 0.9:
                final_cards_in_hand = 6
                mulligan_number = 2
            else:
                final_cards_in_hand = 5
                mulligan_number = 3
            
            # Always draw 7 cards initially
            hand = random.sample(self.deck, 7)
            
            # Determine play or draw (50/50)
            play_or_draw = "play" if random.random() < 0.5 else "draw"
            
            # Show the hand
            self._display_hand(hand, play_or_draw, mulligan_number, final_cards_in_hand)
            
            # Get user decision
            decision = self._get_user_decision()
            
            # Get cards to put on bottom if keeping a mulliganed hand
            cards_to_put_bottom = None
            if decision == "keep" and final_cards_in_hand < 7:
                cards_to_put_bottom = self._get_cards_to_put_bottom(hand, final_cards_in_hand)
            
            # Record the result
            result = HandResult(
                hand_number=hand_num,
                seed=seed,
                cards_in_hand=final_cards_in_hand,
                cards=hand,
                play_or_draw=play_or_draw,
                mulligan_number=mulligan_number,
                user_decision=decision,
                cards_to_keep=cards_to_put_bottom,
                timestamp=datetime.now().isoformat()
            )
            
            self.results.append(result)
            
            print(f"✅ Recorded: {decision.upper()}")
        
        # Show summary
        self._show_summary()
        
        # Save to database
        self._save_to_database(num_hands)
    
    def _display_hand(self, hand: List[str], play_or_draw: str, mulligan_number: int, final_cards: int) -> None:
        """Display the hand to the user."""
        print(f"🎲 Seed: {random.getstate()[1][0] if hasattr(random.getstate(), '__getitem__') else 'N/A'}")
        print(f"🎯 On the: {play_or_draw.upper()}")
        print(f"🔄 Mulligan: #{mulligan_number} (keep {final_cards} cards)")
        print(f"🃏 Your hand (7 cards):")
        
        for i, card in enumerate(hand, 1):
            print(f"  {i}. {card}")
    
    def _get_user_decision(self) -> str:
        """Get user's decision on whether to keep or mulligan."""
        while True:
            decision = input("\n🤔 Decision (keep/mulligan): ").lower().strip()
            if decision in ["keep", "k", "mulligan", "m"]:
                return "keep" if decision in ["keep", "k"] else "mulligan"
            print("❌ Please enter 'keep' or 'mulligan'")
    
    def _get_cards_to_put_bottom(self, hand: List[str], final_cards: int) -> Optional[List[str]]:
        """Get which cards the user wants to put on the bottom when keeping a mulliganed hand."""
        cards_to_put_bottom = 7 - final_cards
        print(f"\n📝 You're keeping this hand, but need to put {cards_to_put_bottom} card(s) on the bottom (keep {final_cards})")
        print("   Which cards do you want to put on the bottom? (enter numbers separated by spaces)")
        print("   Example: 1 3 (to put cards 1 and 3 on the bottom)")
        
        while True:
            try:
                bottom_input = input("Cards to put on bottom: ").strip()
                if not bottom_input:
                    return []
                
                indices = [int(x) - 1 for x in bottom_input.split()]
                cards_to_put_bottom = [hand[i] for i in indices if 0 <= i < len(hand)]
                
                if len(cards_to_put_bottom) == (7 - final_cards):
                    print(f"✅ Putting on bottom: {', '.join(cards_to_put_bottom)}")
                    return cards_to_put_bottom
                else:
                    print(f"❌ You need to put exactly {7 - final_cards} card(s) on the bottom")
                    
            except (ValueError, IndexError):
                print("❌ Invalid input. Please enter numbers separated by spaces.")
    
    def _count_lands(self, hand: List[str]) -> int:
        """Count the number of lands in a hand."""
        # This is a simplified version - in practice, you'd use the CardAnalyzer
        land_keywords = ['land', 'plains', 'island', 'swamp', 'mountain', 'forest', 'wastes']
        count = 0
        for card in hand:
            if any(keyword in card.lower() for keyword in land_keywords):
                count += 1
        return count
    
    def _show_summary(self) -> None:
        """Show a summary of all results."""
        print("\n" + "=" * 50)
        print("📊 SIMULATION SUMMARY")
        print("=" * 50)
        
        total_hands = len(self.results)
        keep_count = sum(1 for r in self.results if r.user_decision == "keep")
        mulligan_count = total_hands - keep_count
        
        print(f"Total hands: {total_hands}")
        print(f"Kept: {keep_count} ({keep_count/total_hands:.1%})")
        print(f"Mulliganed: {mulligan_count} ({mulligan_count/total_hands:.1%})")
        
        # Show mulligan distribution
        mulligan_dist = {}
        for result in self.results:
            mulligan_num = result.mulligan_number
            mulligan_dist[mulligan_num] = mulligan_dist.get(mulligan_num, 0) + 1
        
        print(f"\nMulligan distribution:")
        for mulligan_num in sorted(mulligan_dist.keys()):
            count = mulligan_dist[mulligan_num]
            print(f"  Mulligan #{mulligan_num}: {count} hands ({count/total_hands:.1%})")
        
        # Show play/draw distribution
        play_count = sum(1 for r in self.results if r.play_or_draw == "play")
        draw_count = total_hands - play_count
        print(f"\nPlay/Draw distribution:")
        print(f"  Play: {play_count} ({play_count/total_hands:.1%})")
        print(f"  Draw: {draw_count} ({draw_count/total_hands:.1%})")
    
    def _save_to_database(self, num_hands: int) -> None:
        """Save simulation results to the database."""
        try:
            # Prepare decklist data
            decklist_data = []
            for card in self.decklist:
                decklist_data.append({
                    'name': card.name,
                    'quantity': card.quantity,
                    'type': None,  # Could be enhanced to detect card types
                    'mana_cost': None  # Could be enhanced to parse mana costs
                })
            
            # Save to database
            run_id = self.db_service.save_simulation_run(
                deck_source=self.deck_source,
                deck_name=self.deck_name or f"Deck {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                total_hands=num_hands,
                hand_results=self.results,
                decklist=decklist_data
            )
            
            print(f"\n💾 Results saved to database (Run ID: {run_id})")
            
        except Exception as e:
            print(f"\n⚠️  Warning: Could not save to database: {e}")
            print("   Results are still available in memory")
    
    def save_results(self, filename: str = "mulligan_results.json") -> None:
        """Save results to a JSON file."""
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "total_hands": len(self.results),
            "results": [asdict(result) for result in self.results]
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n💾 Results saved to {filename}")
    
    @classmethod
    def from_url(cls, url: str, deck_name: str = "") -> "MulliganSimulator":
        """
        Create a MulliganSimulator from a decklist URL.
        
        Args:
            url: URL to a decklist
            deck_name: Optional name for the deck
            
        Returns:
            MulliganSimulator instance
        """
        cards = list(mtg_parser.parse_deck(url))
        return cls(cards, deck_source=url, deck_name=deck_name)
    
    @classmethod
    def from_text(cls, decklist_text: str, deck_name: str = "") -> "MulliganSimulator":
        """
        Create a MulliganSimulator from a text decklist.
        
        Args:
            decklist_text: Text format decklist
            deck_name: Optional name for the deck
            
        Returns:
            MulliganSimulator instance
        """
        cards_result = mtg_parser.parse_deck(decklist_text)
        if cards_result is None:
            raise ValueError("Decklist is empty")
        cards = list(cards_result)
        if not cards:
            raise ValueError("Decklist is empty")
        return cls(cards, deck_source="text_input", deck_name=deck_name)
