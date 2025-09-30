#!/usr/bin/env python3
"""
Database setup script for the mulligan simulator.
"""

import sys
from mulligan_simulator.db_init import initialize_database


def main():
    """Setup the database for the mulligan simulator."""
    success = initialize_database()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
