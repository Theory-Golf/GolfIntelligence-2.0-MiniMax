"""
Putting Engine
Analyzes putting performance
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class PuttingEngine:
    """
    Specialized engine for putting analysis.
    
    Calculates:
    - Putts per hole
    - 1-putt/3-putt rates
    - SG by distance
    - Make percentages
    """
    
    def __init__(self):
        """Initialize putting engine."""
        pass
    
    def analyze_putting(self, df: pd.DataFrame) -> Dict:
        """
        Complete putting analysis.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with all putting metrics
        """
        putts = df[df['shot_category'] == 'putting']
        
        if len(putts) == 0:
            return {'message': 'No putting data found'}
        
        total_putts = len(putts)
        
        # Hole-level statistics
        hole_stats = df.groupby('hole').agg({
            'score': 'max',
            'shot': 'count'
        }).reset_index()
        hole_stats.columns = ['hole', 'hole_score', 'strokes']
        
        # Putts per hole
        putts_per_hole = putts.groupby('hole').size()
        avg_putts_per_hole = putts_per_hole.mean()
        
        # 1-putt rate
        one_putts = (hole_stats['strokes'] == 2).sum()  # 1 putt = 2 strokes on hole
        one_putt_rate = (one_putts / len(hole_stats)) * 100
        
        # 3-putt rate
        three_putts = (hole_stats['strokes'] >= 4).sum()  # 3+ putts = 4+ strokes on hole
        three_putt_rate = (three_putts / len(hole_stats)) * 100
        
        # SG metrics
        sg_total = putts['strokes_gained'].sum()
        
        # Distance bucket analysis
        sg_by_bucket = self.analyze_by_distance_bucket(putts)
        
        # Make percentage
        makes = putts[putts['ending_distance'] == 0]
        make_percentage = (len(makes) / total_putts) * 100
        
        return {
            'total_putts': total_putts,
            'avg_putts_per_hole': avg_putts_per_hole,
            'one_putt_rate': one_putt_rate,
            'three_putt_rate': three_putt_rate,
            'sg_total': sg_total,
            'sg_per_putt': sg_total / total_putts,
            'make_percentage': make_percentage,
            'makes': len(makes),
            'sg_by_bucket': sg_by_bucket
        }
    
    def analyze_by_distance_bucket(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Analyze putting by distance bucket.
        
        Args:
            df: Putting shots DataFrame
            
        Returns:
            Dictionary with SG by distance bucket
        """
        buckets = ['0-3', '4-6', '7-10', '10-20', '20-30', '30+']
        sg_by_bucket = {}
        
        for bucket in buckets:
            mask = df['putting_bucket'] == bucket
            sg_by_bucket[bucket] = df.loc[mask, 'strokes_gained'].sum()
        
        return sg_by_bucket
    
    def calculate_make_percentage(self, df: pd.DataFrame) -> Dict:
        """
        Calculate make percentage by distance.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with make percentages
        """
        putts = df[df['shot_category'] == 'putting']
        
        makes = putts[putts['ending_distance'] == 0]
        
        return {
            'total_putts': len(putts),
            'total_makes': len(makes),
            'overall_make_rate': (len(makes) / len(putts)) * 100 if len(putts) > 0 else 0
        }
    
    def calculate_lag_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate lag putting metrics (20+ ft putts).
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with lag metrics
        """
        putts = df[df['shot_category'] == 'putting']
        
        lag_putts = putts[putts['starting_distance'] >= 20]
        
        if len(lag_putts) == 0:
            return {'message': 'No lag putting data found'}
        
        # Leave distance analysis
        leaves = lag_putts[lag_putts['ending_distance'] > 0]
        avg_leave = leaves['ending_distance'].mean() if len(leaves) > 0 else 0
        
        # 3-putt avoidance from lag
        three_putt_opportunities = df.groupby('hole').size()
        three_putt_holes = (three_putt_opportunities >= 4).sum()
        
        return {
            'lag_putts': len(lag_putts),
            'avg_leave_distance': avg_leave,
            'long_putts_made': len(lag_putts[lag_putts['ending_distance'] == 0]),
            'three_putt_prevention_rate': (three_putt_holes / len(three_putt_opportunities)) * 100
        }
    
    def calculate_3_putt_prevention(self, df: pd.DataFrame) -> Dict:
        """
        Calculate 3-putt prevention metrics.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with 3-putt analysis
        """
        hole_stats = df.groupby('hole').agg({
            'score': 'max',
            'shot': 'count'
        }).reset_index()
        hole_stats.columns = ['hole', 'hole_score', 'strokes']
        
        three_putts = hole_stats[hole_stats['strokes'] >= 4]
        
        # Analyze first putt distance on 3-putt holes
        three_putt_holes = three_putts['hole'].tolist()
        
        return {
            'three_putts': len(three_putts),
            'total_holes': len(hole_stats),
            'three_putt_rate': (len(three_putts) / len(hole_stats)) * 100,
            'opportunities_prevented': len(hole_stats) - len(three_putts)
        }
