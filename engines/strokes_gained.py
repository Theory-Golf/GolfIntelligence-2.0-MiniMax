"""
Strokes Gained Engine
Calculates and analyzes Strokes Gained metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class StrokesGainedEngine:
    """
    Specialized engine for Strokes Gained calculations.
    
    Provides:
    - Shot-level SG calculations
    - Category-level SG aggregation
    - SG analysis by various dimensions
    """
    
    def __init__(self, field_mapper):
        """
        Initialize SG engine.
        
        Args:
            field_mapper: FieldMapper instance
        """
        self.field_mapper = field_mapper
    
    def calculate_shot_sg(self, 
                         starting_location: str,
                         starting_distance: float,
                         ending_location: str,
                         ending_distance: float,
                         penalty: bool = False,
                         benchmark_lookup: Dict = None) -> float:
        """
        Calculate SG for a single shot.
        
        Args:
            starting_location: Where shot started
            starting_distance: Distance before shot
            ending_location: Where shot ended
            ending_distance: Distance after shot
            penalty: Whether penalty occurred
            benchmark_lookup: Optional benchmark lookup function
            
        Returns:
            SG value for the shot
        """
        # This is handled by BenchmarkEngine
        # This method provides category-level analysis
        return 0.0
    
    def calculate_sg_by_shot_category(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate total SG by shot category.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary of SG by category
        """
        categories = ['driving', 'approach', 'short_game', 'putting']
        sg_by_category = {}
        
        for cat in categories:
            mask = df['shot_category'] == cat
            sg_by_category[cat] = df.loc[mask, 'strokes_gained'].sum()
        
        return sg_by_category
    
    def calculate_sg_by_distance_bucket(self, 
                                      df: pd.DataFrame,
                                      category: str,
                                      buckets: List[str]) -> Dict[str, float]:
        """
        Calculate SG by distance bucket for a category.
        
        Args:
            df: Shot-level DataFrame
            category: Shot category
            buckets: List of bucket strings
            
        Returns:
            Dictionary of SG by bucket
        """
        bucket_col = f"{category}_bucket"
        
        sg_by_bucket = {}
        for bucket in buckets:
            mask = (df['shot_category'] == category) & (df[bucket_col] == bucket)
            sg_by_bucket[bucket] = df.loc[mask, 'strokes_gained'].sum()
        
        return sg_by_bucket
    
    def calculate_sg_trend(self, 
                          df: pd.DataFrame,
                          bucket_column: str = 'date') -> Dict[str, List[float]]:
        """
        Calculate SG trend over time or rounds.
        
        Args:
            df: DataFrame
            bucket_column: Column to group by
            
        Returns:
            Dictionary of SG values by bucket
        """
        sg_by_bucket = df.groupby(bucket_column)['strokes_gained'].sum()
        
        return {
            'labels': sg_by_bucket.index.tolist(),
            'values': sg_by_bucket.values.tolist()
        }
    
    def calculate_sg_separators(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate SG for key separator metrics.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary of separator SG values
        """
        # These are SG values for specific shot types
        # that often separate good from great players
        
        separators = {}
        
        # Putting 3-6 ft
        mask = (df['shot_category'] == 'putting') & \
               (df['starting_distance'] >= 3) & \
               (df['starting_distance'] <= 6)
        separators['putting_3_6ft'] = df.loc[mask, 'strokes_gained'].sum()
        
        # Approach 100-150 yds
        mask = (df['shot_category'] == 'approach') & \
               (df['starting_distance'] >= 100) & \
               (df['starting_distance'] < 150)
        separators['approach_100_150yd'] = df.loc[mask, 'strokes_gained'].sum()
        
        # Approach 150-200 yds
        mask = (df['shot_category'] == 'approach') & \
               (df['starting_distance'] >= 150) & \
               (df['starting_distance'] < 200)
        separators['approach_150_200yd'] = df.loc[mask, 'strokes_gained'].sum()
        
        # SG on playable drives (fairway or rough, no penalty)
        mask = (df['shot_category'] == 'driving') & \
               (df['ending_location'].isin(['Fairway', 'Rough'])) & \
               (df['penalty'] != 'Yes')
        separators['sg_playable_drives'] = df.loc[mask, 'strokes_gained'].sum()
        
        return separators
