"""
Database initialization and management utilities.
"""

import os
import sys
from typing import Optional
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError
from .database import Base, engine, DATABASE_URL


def check_database_connection() -> bool:
    """
    Check if the database connection is working.
    
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def check_tables_exist() -> bool:
    """
    Check if the required tables exist in the database.
    
    Returns:
        True if all required tables exist, False otherwise
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        required_tables = {
            'simulation_runs',
            'hand_results', 
            'deck_cards'
        }
        
        missing_tables = required_tables - set(existing_tables)
        
        if missing_tables:
            print(f"⚠️  Missing tables: {', '.join(missing_tables)}")
            return False
        
        print("✅ All required tables exist")
        return True
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False


def create_tables_if_not_exist() -> bool:
    """
    Create tables if they don't exist.
    
    Returns:
        True if tables were created successfully or already exist, False otherwise
    """
    try:
        # Check if tables already exist
        if check_tables_exist():
            return True
        
        print("🔧 Creating missing tables...")
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        if check_tables_exist():
            print("✅ Tables created successfully")
            return True
        else:
            print("❌ Failed to create tables")
            return False
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


def initialize_database(force_recreate: bool = False) -> bool:
    """
    Initialize the database with all required tables.
    
    Args:
        force_recreate: If True, drop and recreate all tables
        
    Returns:
        True if initialization was successful, False otherwise
    """
    print("🚀 Initializing Mulligan Simulator Database")
    print("=" * 50)
    
    # Check database connection
    if not check_database_connection():
        print("\n💡 Troubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your DATABASE_URL environment variable")
        print("3. Run 'docker-compose up -d postgres' to start the database")
        return False
    
    # Force recreate if requested
    if force_recreate:
        print("🗑️  Dropping existing tables...")
        try:
            Base.metadata.drop_all(bind=engine)
            print("✅ Tables dropped successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not drop tables: {e}")
    
    # Create tables if they don't exist
    if not create_tables_if_not_exist():
        return False
    
    print("\n🎯 Database initialization complete!")
    print("\nNext steps:")
    print("1. Run simulations: poetry run mulligan-simulator --file example_deck.txt --hands 10")
    print("2. View results: poetry run python -m mulligan_simulator.db_cli list-runs")
    print("3. View stats: poetry run python -m mulligan_simulator.db_cli stats <run-id>")
    
    return True


def get_database_info() -> dict:
    """
    Get information about the current database state.
    
    Returns:
        Dictionary with database information
    """
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        info = {
            'database_url': DATABASE_URL,
            'connection_status': 'connected' if check_database_connection() else 'disconnected',
            'tables_exist': check_tables_exist(),
            'existing_tables': tables,
            'required_tables': ['simulation_runs', 'hand_results', 'deck_cards']
        }
        
        return info
        
    except Exception as e:
        return {
            'database_url': DATABASE_URL,
            'connection_status': 'error',
            'error': str(e),
            'tables_exist': False,
            'existing_tables': [],
            'required_tables': ['simulation_runs', 'hand_results', 'deck_cards']
        }


def main():
    """Main function for database initialization."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize Mulligan Simulator Database')
    parser.add_argument('--force', action='store_true', help='Force recreate all tables')
    parser.add_argument('--info', action='store_true', help='Show database information')
    parser.add_argument('--check', action='store_true', help='Check database status')
    
    args = parser.parse_args()
    
    if args.info:
        info = get_database_info()
        print("📊 Database Information:")
        print(f"  URL: {info['database_url']}")
        print(f"  Status: {info['connection_status']}")
        print(f"  Tables exist: {info['tables_exist']}")
        print(f"  Existing tables: {', '.join(info['existing_tables'])}")
        if 'error' in info:
            print(f"  Error: {info['error']}")
        return
    
    if args.check:
        if check_database_connection() and check_tables_exist():
            print("✅ Database is ready")
            sys.exit(0)
        else:
            print("❌ Database is not ready")
            sys.exit(1)
    
    # Initialize database
    success = initialize_database(force_recreate=args.force)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
