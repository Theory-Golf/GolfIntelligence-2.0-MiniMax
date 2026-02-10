"""
Driving Engine
Analyzes driving performance metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class DrivingEngine:
    """
    Specialized engine for driving analysis.
    
    Calculates:
    - Fairway hit rate
    - Driving distance
    - SG metrics
    - OB/penalty rates
    """
    
    def __init__(self):
        """Initialize driving engine."""
        pass
    
    def analyze_driving(self, df: pd.DataFrame) -> Dict:
        """
        Complete driving analysis.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with all driving metrics
        """
        drives = df[df['shot_category'] == 'driving']
        
        if len(drives) == 0:
            return {'message': 'No driving data found'}
        
        total_drives = len(drives)
        
        # Fairway hit rate
        fairway_or_green = drives[drives['ending_location'].isin(['Fairway', 'Rough'])].shape[0]
        fairway_percentage = (fairway_or_green / total_drives) * 100
        
        # Playable drives (no penalty, in fairway/rough)
        playable = drives[
            (drives['ending_location'].isin(['Fairway', 'Rough'])) & 
            (drives['penalty'] != 'Yes')
        ]
        sg_playable = playable['strokes_gained'].sum()
        
        # OB/Re-tee detection
        drive_per_hole = drives.groupby('hole').size()
        ob_count = (drive_per_hole >= 2).sum()
        
        # SG metrics
        sg_total = drives['strokes_gained'].sum()
        
        # Distance metrics
        distances = drives['starting_distance'] - drives['ending_distance']
        avg_distance = distances.mean()
        
        return {
            'total_drives': total_drives,
            'fairway_percentage': fairway_percentage,
            'fairway_hits': fairway_or_green,
            'sg_total': sg_total,
            'sg_per_drive': sg_total / total_drives,
            'sg_playable': sg_playable,
            'sg_playable_per_drive': sg_playable / total_drives,
            'ob_count': ob_count,
            'ob_rate': (ob_count / total_drives) * 100,
            'avg_carry_distance': avg_distance,
            'penalty_count': (drives['penalty'] == 'Yes').sum(),
            'penalty_rate': (drives['penalty'] == 'Yes').sum() / total_drives * 100
        }
    
    def analyze_driving_by_distance(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Analyze driving by distance bucket.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with SG by distance bucket
        """
        drives = df[df['shot_category'] == 'driving']
        
        buckets = ['<200', '200-250', '250-300', '300+']
        sg_by_bucket = {}
        
        for bucket in buckets:
            mask = drives['driving_bucket'] == bucket
            sg_by_bucket[bucket] = drives.loc[mask, 'strokes_gained'].sum()
        
        return sg_by_bucket
    
    def calculate_fairway_percentage(self, df: pd.DataFrame) -> Dict:
        """
        Calculate fairway hit percentage.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with fairway metrics
        """
        drives = df[df['shot_category'] == 'driving']
        
        if len(drives) == 0:
            return {'fairway_percentage': 0, 'total_drives': 0}
        
        fairway_hits = drives[drives['ending_location'] == 'Fairway'].shape[0]
        fairway_percentage = (fairway_hits / len(drives)) * 100
        
        return {
            'fairway_percentage': fairway_percentage,
            'fairway_hits': fairway_hits,
            'total_drives': len(drives)
        }
    
    def calculate_trouble_to_bogey(self, df: pd.DataFrame) -> Dict:
        """
        Calculate trouble-to-bogey rate.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with trouble-to-bogey metrics
        """
        drives = df[df['shot_category'] == 'driving']
        
        # Drives ending in trouble (rough/recovery)
        trouble = drives[drives['ending_location'].isin(['Rough', 'Recovery'])]
        
        if len(trouble) == 0:
            return {'trouble_to_bogey_rate': 0, 'attempts': 0, 'fails': 0}
        
        # Get holes with trouble drives
        trouble_holes = trouble['hole'].unique()
        
        # Check if these holes resulted in bogey or worse
        hole_scores = df.groupby('hole')['score'].max()
        bogey_after_trouble = sum(
            1 for h in trouble_holes 
            if hole_scores.get(h, 3) >= 4  # Assuming par 3
        )
        
        return {
            'trouble_to_bogey_rate': (bogey_after_trouble / len(trouble_holes)) * 100 if len(trouble_holes) > 0 else 0,
            'attempts': len(trouble_holes),
            'fails': bogey_after_trouble
        }
