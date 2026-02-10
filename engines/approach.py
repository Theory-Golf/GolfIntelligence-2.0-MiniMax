"""
Approach Engine
Analyzes approach shot performance
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class ApproachEngine:
    """
    Specialized engine for approach shot analysis.
    
    Calculates:
    - Green hit rate (GIR)
    - Proximity
    - SG by distance
    - Fairway vs rough splits
    """
    
    def __init__(self):
        """Initialize approach engine."""
        pass
    
    def analyze_approach(self, df: pd.DataFrame) -> Dict:
        """
        Complete approach analysis.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with all approach metrics
        """
        approaches = df[df['shot_category'] == 'approach']
        
        if len(approaches) == 0:
            return {'message': 'No approach data found'}
        
        total_approaches = len(approaches)
        
        # Green hit rate
        greens = approaches[approaches['ending_location'] == 'Green']
        gir_rate = (len(greens) / total_approaches) * 100
        
        # SG metrics
        sg_total = approaches['strokes_gained'].sum()
        
        # Proximity (for greens hit)
        proximity = greens['ending_distance'].mean() if len(greens) > 0 else 0
        
        # Fairway vs Rough splits
        fairway_approaches = approaches[approaches['starting_location'] == 'Fairway']
        rough_approaches = approaches[approaches['starting_location'] == 'Rough']
        
        sg_fairway = fairway_approaches['strokes_gained'].sum()
        sg_rough = rough_approaches['strokes_gained'].sum()
        
        # Distance bucket analysis
        sg_by_bucket = self.analyze_by_distance_bucket(approaches)
        
        return {
            'total_approaches': total_approaches,
            'gir_rate': gir_rate,
            'greens_hit': len(greens),
            'proximity': proximity,
            'sg_total': sg_total,
            'sg_per_shot': sg_total / total_approaches,
            'sg_fairway': sg_fairway,
            'sg_rough': sg_rough,
            'approaches_from_fairway': len(fairway_approaches),
            'approaches_from_rough': len(rough_approaches),
            'sg_by_bucket': sg_by_bucket
        }
    
    def analyze_by_distance_bucket(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Analyze approach by distance bucket.
        
        Args:
            df: Approach shots DataFrame
            
        Returns:
            Dictionary with SG by distance bucket
        """
        buckets = ['50-100', '100-150', '150-200', '200+']
        sg_by_bucket = {}
        
        for bucket in buckets:
            mask = df['approach_bucket'] == bucket
            sg_by_bucket[bucket] = df.loc[mask, 'strokes_gained'].sum()
        
        return sg_by_bucket
    
    def calculate_gir_rate(self, df: pd.DataFrame) -> Dict:
        """
        Calculate greens in regulation rate.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with GIR metrics
        """
        approaches = df[df['shot_category'] == 'approach']
        
        if len(approaches) == 0:
            return {'gir_rate': 0, 'total_approaches': 0}
        
        greens = approaches[approaches['ending_location'] == 'Green']
        
        return {
            'gir_rate': (len(greens) / len(approaches)) * 100,
            'greens_hit': len(greens),
            'total_approaches': len(approaches)
        }
    
    def calculate_proximity(self, df: pd.DataFrame) -> Dict:
        """
        Calculate proximity to hole.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with proximity metrics
        """
        approaches = df[df['shot_category'] == 'approach']
        greens = approaches[approaches['ending_location'] == 'Green']
        
        if len(greens) == 0:
            return {'avg_proximity': 0, 'shots_analyzed': 0}
        
        return {
            'avg_proximity': greens['ending_distance'].mean(),
            'median_proximity': greens['ending_distance'].median(),
            'shots_analyzed': len(greens)
        }
    
    def analyze_fairway_rough_split(self, df: pd.DataFrame) -> Dict:
        """
        Analyze approach performance from fairway vs rough.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with split metrics
        """
        approaches = df[df['shot_category'] == 'approach']
        
        fairway = approaches[approaches['starting_location'] == 'Fairway']
        rough = approaches[approaches['starting_location'] == 'Rough']
        
        return {
            'fairway': {
                'count': len(fairway),
                'sg_total': fairway['strokes_gained'].sum(),
                'gir_rate': (fairway[fairway['ending_location'] == 'Green'].shape[0] / len(fairway)) * 100 if len(fairway) > 0 else 0
            },
            'rough': {
                'count': len(rough),
                'sg_total': rough['strokes_gained'].sum(),
                'gir_rate': (rough[rough['ending_location'] == 'Green'].shape[0] / len(rough)) * 100 if len(rough) > 0 else 0
            }
        }
