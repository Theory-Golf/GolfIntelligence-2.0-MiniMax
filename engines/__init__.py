"""
Golf Analytics Engines Package
Contains specialized calculation engines for different aspects of golf performance
"""

from .strokes_gained import StrokesGainedEngine
from .tiger5 import Tiger5Engine
from .driving import DrivingEngine
from .approach import ApproachEngine
from .short_game import ShortGameEngine
from .putting import PuttingEngine
from .overview import OverviewEngine
from .coach_corner import CoachCornerEngine
from .comparison import ComparisonEngine

__all__ = [
    'StrokesGainedEngine',
    'Tiger5Engine',
    'DrivingEngine',
    'ApproachEngine',
    'ShortGameEngine',
    'PuttingEngine',
    'OverviewEngine',
    'CoachCornerEngine',
    'ComparisonEngine'
]
