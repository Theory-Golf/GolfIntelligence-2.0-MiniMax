"""
Short Game Engine
Analyzes short game performance (shots within 25 yards)
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class ShortGameEngine:
    """
    Specialized engine for short game analysis.
    
    Calculates:
    - Up and down rate
    - Scrambling
    - SG by distance
    - Proximity by lie
    """
    
    def __init__(self):
        """Initialize short game engine."""
        pass
    
    def analyze_short_game(self, df: pd.DataFrame) -> Dict:
        """
        Complete short game analysis.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with all short game metrics
        """
        short_game = df[df['shot_category'] == 'short_game']
        
        if len(short_game) == 0:
            return {'message': 'No short game data found'}
        
        total_shots = len(short_game)
        
        # SG metrics
        sg_total = short_game['strokes_gained'].sum()
        
        # Green hit rate from short game
        greens = short_game[short_game['ending_location'] == 'Green']
        green_hit_rate = (len(greens) / total_shots) * 100
        
        # Proximity for greens hit
        proximity = greens['ending_distance'].mean() if len(greens) > 0 else 0
        
        # Distance bucket analysis
        sg_by_bucket = self.analyze_by_distance_bucket(short_game)
        
        # Lie analysis
        sg_by_lie = self.analyze_by_lie(short_game)
        
        return {
            'total_shots': total_shots,
            'sg_total': sg_total,
            'sg_per_shot': sg_total / total_shots,
            'green_hit_rate': green_hit_rate,
            'greens_hit': len(greens),
            'proximity': proximity,
            'sg_by_bucket': sg_by_bucket,
            'sg_by_lie': sg_by_lie
        }
    
    def analyze_by_distance_bucket(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Analyze short game by distance bucket.
        
        Args:
            df: Short game shots DataFrame
            
        Returns:
            Dictionary with SG by distance bucket
        """
        buckets = ['<10', '10-20', '20-30', '30-40', '40-50']
        sg_by_bucket = {}
        
        for bucket in buckets:
            mask = df['short_game_bucket'] == bucket
            sg_by_bucket[bucket] = df.loc[mask, 'strokes_gained'].sum()
        
        return sg_by_bucket
    
    def analyze_by_lie(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Analyze short game by lie type.
        
        Args:
            df: Short game shots DataFrame
            
        Returns:
            Dictionary with metrics by lie
        """
        lies = ['Fairway', 'Rough', 'Sand']
        results = {}
        
        for lie in lies:
            lie_shots = df[df['starting_location'] == lie]
            
            if len(lie_shots) == 0:
                continue
            
            greens = lie_shots[lie_shots['ending_location'] == 'Green']
            
            results[lie] = {
                'shots': len(lie_shots),
                'sg_total': lie_shots['strokes_gained'].sum(),
                'greens': len(greens),
                'green_rate': (len(greens) / len(lie_shots)) * 100,
                'avg_proximity': greens['ending_distance'].mean() if len(greens) > 0 else 0
            }
        
        return results
    
    def calculate_up_and_down_rate(self, df: pd.DataFrame) -> Dict:
        """
        Calculate up and down success rate.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with up and down metrics
        """
        short_game = df[df['shot_category'] == 'short_game']
        
        # Get holes with short game shots
        holes_with_short = short_game['hole'].unique()
        
        # Get shots that hit green
        greens = short_game[short_game['ending_location'] == 'Green']
        
        # Count up and downs (green hit + 1 putt or holed)
        up_and_downs = 0
        for hole in holes_with_short:
            hole_greens = greens[greens['hole'] == hole]
            if len(hole_greens) > 0:
                # Get total strokes on hole
                hole_shots = df[df['hole'] == hole]
                total_shots = len(hole_shots)
                # If green hit and total strokes <= 2 (green + 1 putt = 2)
                if total_shots <= 2:
                    up_and_downs += 1
        
        return {
            'up_and_downs': up_and_downs,
            'opportunities': len(holes_with_short),
            'up_and_down_rate': (up_and_downs / len(holes_with_short)) * 100 if len(holes_with_short) > 0 else 0
        }
    
    def calculate_scrambling_rate(self, df: pd.DataFrame) -> Dict:
        """
        Calculate scrambling rate (greens hit in regulation + save).
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with scrambling metrics
        """
        # This would need par information for proper calculation
        # Simplified version for now
        
        short_game = df[df['shot_category'] == 'short_game']
        
        return {
            'scrambling_opportunities': short_game['hole'].nunique(),
            'short_game_shots': len(short_game)
        }
