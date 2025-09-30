"""
Magic: The Gathering Mulligan Simulator

An interactive tool for simulating mulligans and recording user decisions.
"""

from .simulator import MulliganSimulator
from .models import HandResult

__version__ = "0.1.0"
__all__ = ["MulliganSimulator", "HandResult"]
