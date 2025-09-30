"""
Database service for saving and retrieving simulation data.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, ProgrammingError
from .database import SessionLocal, SimulationRun, HandResult, DeckCard
from .models import HandResult as SimHandResult
from .db_init import check_tables_exist, create_tables_if_not_exist


class DatabaseService:
    """Service for database operations."""
    
    def __init__(self):
        self.session = SessionLocal()
        # Ensure tables exist before using the service
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Ensure database tables exist, create them if they don't."""
        try:
            if not check_tables_exist():
                print("🔧 Creating missing database tables...")
                create_tables_if_not_exist()
        except Exception as e:
            print(f"⚠️  Warning: Could not verify/create tables: {e}")
            # Continue anyway - the actual database operations will handle errors
    
    def save_simulation_run(
        self,
        deck_source: str,
        deck_name: str,
        total_hands: int,
        hand_results: List[SimHandResult],
        decklist: List[Dict[str, Any]],
        user_name: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        Save a complete simulation run to the database.
        
        Args:
            deck_source: URL or file path of the deck
            deck_name: Name of the deck
            total_hands: Number of hands simulated
            hand_results: List of hand results
            decklist: List of cards in the deck
            user_name: Optional user name
            notes: Optional notes
            
        Returns:
            Simulation run ID
        """
        try:
            # Create simulation run
            simulation_run = SimulationRun(
                deck_source=deck_source,
                deck_name=deck_name,
                total_hands=total_hands,
                user_name=user_name,
                notes=notes
            )
            
            self.session.add(simulation_run)
            self.session.flush()  # Get the ID
            
            # Save deck cards
            for card in decklist:
                deck_card = DeckCard(
                    simulation_run_id=simulation_run.id,
                    card_name=card['name'],
                    quantity=card['quantity'],
                    card_type=card.get('type'),
                    mana_cost=card.get('mana_cost')
                )
                self.session.add(deck_card)
            
            # Save hand results
            for hand_result in hand_results:
                db_hand_result = HandResult(
                    simulation_run_id=simulation_run.id,
                    hand_number=hand_result.hand_number,
                    seed=hand_result.seed,
                    cards_in_hand=hand_result.cards_in_hand,
                    cards=hand_result.cards,
                    play_or_draw=hand_result.play_or_draw,
                    mulligan_number=hand_result.mulligan_number,
                    user_decision=hand_result.user_decision,
                    cards_to_put_bottom=hand_result.cards_to_keep
                )
                self.session.add(db_hand_result)
            
            self.session.commit()
            return str(simulation_run.id)
            
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.session.close()
    
    def get_simulation_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent simulation runs.
        
        Args:
            limit: Maximum number of runs to return
            
        Returns:
            List of simulation run data
        """
        runs = self.session.query(SimulationRun).order_by(
            SimulationRun.created_at.desc()
        ).limit(limit).all()
        
        return [
            {
                'id': str(run.id),
                'created_at': run.created_at,
                'deck_source': run.deck_source,
                'deck_name': run.deck_name,
                'total_hands': run.total_hands,
                'user_name': run.user_name,
                'notes': run.notes
            }
            for run in runs
        ]
    
    def get_simulation_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific simulation run with all hand results.
        
        Args:
            run_id: Simulation run ID
            
        Returns:
            Simulation run data with hand results
        """
        run = self.session.query(SimulationRun).filter(
            SimulationRun.id == run_id
        ).first()
        
        if not run:
            return None
        
        hand_results = self.session.query(HandResult).filter(
            HandResult.simulation_run_id == run_id
        ).order_by(HandResult.hand_number).all()
        
        return {
            'id': str(run.id),
            'created_at': run.created_at,
            'deck_source': run.deck_source,
            'deck_name': run.deck_name,
            'total_hands': run.total_hands,
            'user_name': run.user_name,
            'notes': run.notes,
            'hand_results': [
                {
                    'hand_number': hr.hand_number,
                    'seed': hr.seed,
                    'cards_in_hand': hr.cards_in_hand,
                    'cards': hr.cards,
                    'play_or_draw': hr.play_or_draw,
                    'mulligan_number': hr.mulligan_number,
                    'user_decision': hr.user_decision,
                    'cards_to_put_bottom': hr.cards_to_put_bottom,
                    'created_at': hr.created_at
                }
                for hr in hand_results
            ]
        }
    
    def get_simulation_stats(self, run_id: str) -> Dict[str, Any]:
        """
        Get statistics for a simulation run.
        
        Args:
            run_id: Simulation run ID
            
        Returns:
            Statistics dictionary
        """
        hand_results = self.session.query(HandResult).filter(
            HandResult.simulation_run_id == run_id
        ).all()
        
        if not hand_results:
            return {}
        
        total_hands = len(hand_results)
        keep_count = sum(1 for hr in hand_results if hr.user_decision == "keep")
        mulligan_count = total_hands - keep_count
        
        # Mulligan distribution
        mulligan_dist = {}
        for hr in hand_results:
            mulligan_num = hr.mulligan_number
            mulligan_dist[mulligan_num] = mulligan_dist.get(mulligan_num, 0) + 1
        
        # Play/draw distribution
        play_count = sum(1 for hr in hand_results if hr.play_or_draw == "play")
        draw_count = total_hands - play_count
        
        return {
            'total_hands': total_hands,
            'keep_count': keep_count,
            'mulligan_count': mulligan_count,
            'keep_rate': keep_count / total_hands if total_hands > 0 else 0,
            'mulligan_distribution': mulligan_dist,
            'play_count': play_count,
            'draw_count': draw_count,
            'play_rate': play_count / total_hands if total_hands > 0 else 0
        }
    
    def close(self):
        """Close the database session."""
        self.session.close()
