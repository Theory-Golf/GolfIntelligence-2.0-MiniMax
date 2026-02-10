"""
Metric Engine Module
Core calculations for golf metrics and statistics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class MetricEngine:
    """
    Core metric calculations for golf analytics.
    
    Calculates:
    - Strokes Gained by category
    - Hole-level statistics
    - Tiger 5 metrics
    - Pillar-specific metrics (Driving, Approach, Short Game, Putting)
    """
    
    def __init__(self, field_mapper):
        """
        Initialize metric engine.
        
        Args:
            field_mapper: FieldMapper instance for field name translation
        """
        self.field_mapper = field_mapper
    
    # ==================== HOLE-LEVEL CALCULATIONS ====================
    
    def calculate_hole_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate hole-level statistics.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            DataFrame with hole-level aggregations
        """
        hole_stats = df.groupby(['round_id', 'hole']).agg({
            'score': 'max',  # Final score on hole
            'shot': 'count',  # Number of shots
            'strokes_gained': 'sum',  # Total SG on hole
            'penalty': lambda x: (x == 'Yes').sum()  # Penalty count
        }).reset_index()
        
        hole_stats.columns = ['round_id', 'hole', 'hole_score', 'shots_count', 'hole_sg', 'penalties']
        
        # Calculate score vs par (assuming par = shots - 2 for simplicity, 
        # should be customized based on actual course par)
        hole_stats['score_vs_par'] = hole_stats['hole_score'] - 3  # Default par 3, customize as needed
        
        return hole_stats
    
    def calculate_putts_per_hole(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate putts per hole.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            DataFrame with putt counts
        """
        putts = df.groupby(['round_id', 'hole']).agg({
            'shot': lambda x: (df.loc[x.index, 'starting_location'] == 'Green').sum()
        }).reset_index()
        
        putts.columns = ['round_id', 'hole', 'putts']
        
        return putts
    
    # ==================== STROKES GAINED CALCULATIONS ====================
    
    def calculate_sg_by_category(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate total Strokes Gained by shot category.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with SG by category
        """
        sg_by_category = {}
        
        for category in ['driving', 'approach', 'short_game', 'putting']:
            mask = df['shot_category'] == category
            sg_by_category[category] = df.loc[mask, 'strokes_gained'].sum()
        
        return sg_by_category
    
    def calculate_sg_per_round(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate SG metrics per round.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with per-round SG metrics
        """
        rounds = df['round_id'].nunique()
        total_sg = df['strokes_gained'].sum()
        
        return {
            'total_sg': total_sg,
            'sg_per_round': total_sg / rounds if rounds > 0 else 0,
            'num_rounds': rounds
        }
    
    def calculate_sg_by_distance_bucket(self, 
                                       df: pd.DataFrame, 
                                       category: str,
                                       buckets: List[str]) -> Dict[str, float]:
        """
        Calculate SG by distance bucket for a category.
        
        Args:
            df: Shot-level DataFrame
            category: Shot category (driving, approach, short_game, putting)
            buckets: List of distance bucket strings
            
        Returns:
            Dictionary mapping bucket -> SG total
        """
        sg_by_bucket = {}
        
        for bucket in buckets:
            mask = (df['shot_category'] == category) & (df['distance_bucket'] == bucket)
            sg_by_bucket[bucket] = df.loc[mask, 'strokes_gained'].sum()
        
        return sg_by_bucket
    
    # ==================== DRIVING METRICS ====================
    
    def calculate_driving_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate driving-specific metrics.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with driving metrics
        """
        drives = df[df['shot_category'] == 'driving']
        
        if len(drives) == 0:
            return {}
        
        total_drives = len(drives)
        
        # Fairway hit rate (Fairway + Green endings)
        fairway_hits = drives[drives['ending_location'].isin(['Fairway', 'Rough'])].shape[0]
        fairway_percentage = (fairway_hits / total_drives) * 100
        
        # Playable drives (Fairway or Rough, no penalty)
        playable = drives[(drives['ending_location'].isin(['Fairway', 'Rough'])) & 
                         (drives['penalty'] != 'Yes')]
        sg_playable = playable['strokes_gained'].sum()
        
        # OB/Re-tee detection (holes with 2+ tee shots)
        ob_retee = drives.groupby('hole').size()
        ob_count = (ob_retee >= 2).sum()
        
        # SG on all drives
        sg_total = drives['strokes_gained'].sum()
        
        return {
            'total_drives': total_drives,
            'fairway_percentage': fairway_percentage,
            'fairway_hits': fairway_hits,
            'sg_total': sg_total,
            'sg_per_drive': sg_total / total_drives,
            'sg_playable': sg_playable,
            'ob_retee_count': ob_count,
            'ob_retee_rate': (ob_count / total_drives) * 100
        }
    
    # ==================== APPROACH METRICS ====================
    
    def calculate_approach_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate approach-specific metrics.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with approach metrics
        """
        approaches = df[df['shot_category'] == 'approach']
        
        if len(approaches) == 0:
            return {}
        
        total_approaches = len(approaches)
        
        # Green hit rate
        green_hits = approaches[approaches['ending_location'] == 'Green'].shape[0]
        gir_rate = (green_hits / total_approaches) * 100
        
        # SG total
        sg_total = approaches['strokes_gained'].sum()
        
        # Proximity (average ending distance)
        on_green = approaches[approaches['ending_location'] == 'Green']
        proximity = on_green['ending_distance'].mean() if len(on_green) > 0 else 0
        
        return {
            'total_approaches': total_approaches,
            'gir_rate': gir_rate,
            'green_hits': green_hits,
            'sg_total': sg_total,
            'sg_per_approach': sg_total / total_approaches,
            'avg_proximity': proximity
        }
    
    # ==================== SHORT GAME METRICS ====================
    
    def calculate_short_game_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate short game metrics.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with short game metrics
        """
        short_game = df[df['shot_category'] == 'short_game']
        
        if len(short_game) == 0:
            return {}
        
        total_short_game = len(short_game)
        
        # Up-and-down rate (short game shot that ends on green + 1 putt or holed)
        up_and_downs = short_game[
            (short_game['ending_location'] == 'Green') & 
            (short_game['strokes_gained'] >= 0)
        ].shape[0]
        
        # SG total
        sg_total = short_game['strokes_gained'].sum()
        
        return {
            'total_short_game': total_short_game,
            'up_and_down_rate': (up_and_downs / total_short_game) * 100,
            'sg_total': sg_total,
            'sg_per_shot': sg_total / total_short_game
        }
    
    # ==================== PUTTING METRICS ====================
    
    def calculate_putting_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate putting metrics.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with putting metrics
        """
        putts = df[df['shot_category'] == 'putting']
        
        if len(putts) == 0:
            return {}
        
        total_putts = len(putts)
        
        # SG total
        sg_total = putts['strokes_gained'].sum()
        
        # Make percentage by distance
        makes = putts[putts['ending_distance'] == 0]
        
        # 1-putt rate
        hole_scores = df.groupby('hole')['score'].max()
        one_putts = (hole_scores == 2).sum()  # Score of 2 means 1 putt
        total_holes = len(hole_scores)
        one_putt_rate = (one_putts / total_holes) * 100 if total_holes > 0 else 0
        
        # 3-putt avoidance
        three_putts = (hole_scores >= 4).sum()  # Score of 4+ means 3+ putts
        three_putt_rate = (three_putts / total_holes) * 100 if total_holes > 0 else 0
        
        return {
            'total_putts': total_putts,
            'sg_total': sg_total,
            'sg_per_putt': sg_total / total_putts,
            'one_putt_rate': one_putt_rate,
            'three_putt_rate': three_putt_rate,
            'putts_per_hole': total_putts / total_holes
        }
    
    # ==================== SCORING METRICS ====================
    
    def calculate_scoring_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate overall scoring metrics.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with scoring metrics
        """
        hole_scores = df.groupby('hole')['score'].max()
        
        total_holes = len(hole_scores)
        
        # Score distribution
        eagles = (hole_scores <= 1).sum()  # Score of 1 or less (eagle)
        birdies = (hole_scores == 2).sum()  # Score of 2 (birdie)
        pars = (hole_scores == 3).sum()     # Score of 3 (par)
        bogeys = (hole_scores == 4).sum()   # Score of 4 (bogey)
        doubles = (hole_scores >= 5).sum()  # Score of 5+ (double or worse)
        
        scoring_avg = hole_scores.mean()
        
        return {
            'scoring_average': scoring_avg,
            'total_holes': total_holes,
            'eagles': eagles,
            'birdies': birdies,
            'pars': pars,
            'bogeys': bogeys,
            'doubles_or_worse': doubles,
            'eagle_rate': (eagles / total_holes) * 100,
            'birdie_rate': (birdies / total_holes) * 100,
            'par_rate': (pars / total_holes) * 100,
            'bogey_rate': (bogeys / total_holes) * 100,
            'double_rate': (doubles / total_holes) * 100
        }
    
    # ==================== AGGREGATE METHOD ====================
    
    def calculate_all_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate all metrics for a DataFrame.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with all calculated metrics
        """
        return {
            'scoring': self.calculate_scoring_metrics(df),
            'sg_total': self.calculate_sg_per_round(df),
            'sg_by_category': self.calculate_sg_by_category(df),
            'driving': self.calculate_driving_metrics(df),
            'approach': self.calculate_approach_metrics(df),
            'short_game': self.calculate_short_game_metrics(df),
            'putting': self.calculate_putting_metrics(df),
            'holes': self.calculate_hole_scores(df)
        }
