"""
Overview Engine
Aggregates all metrics for overall performance view
"""

import pandas as pd
import numpy as np
from typing import Dict


class OverviewEngine:
    """
    Aggregates metrics from all other engines for overall view.
    
    Provides:
    - Total SG
    - SG by pillar
    - Scoring summary
    - Key separators
    """
    
    def __init__(self, 
                 driving_engine,
                 approach_engine,
                 short_game_engine,
                 putting_engine):
        """
        Initialize overview engine with pillar engines.
        
        Args:
            driving_engine: DrivingEngine instance
            approach_engine: ApproachEngine instance
            short_game_engine: ShortGameEngine instance
            putting_engine: PuttingEngine instance
        """
        self.driving = driving_engine
        self.approach = approach_engine
        self.short_game = short_game_engine
        self.putting = putting_engine
    
    def get_overall_summary(self, df: pd.DataFrame) -> Dict:
        """
        Get complete overall performance summary.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with complete overview
        """
        # Get pillar metrics
        driving = self.driving.analyze_driving(df)
        approach = self.approach.analyze_approach(df)
        short_game = self.short_game.analyze_short_game(df)
        putting = self.putting.analyze_putting(df)
        
        # Calculate totals
        num_rounds = df['round_id'].nunique()
        total_shots = len(df)
        total_sg = df['strokes_gained'].sum()
        
        # Scoring summary
        hole_scores = df.groupby('hole')['score'].max()
        scoring_avg = hole_scores.mean()
        
        return {
            'rounds': {
                'count': num_rounds,
                'total_shots': total_shots
            },
            'strokes_gained': {
                'total': total_sg,
                'per_round': total_sg / num_rounds if num_rounds > 0 else 0
            },
            'scoring': {
                'average': scoring_avg,
                'total_holes': len(hole_scores)
            },
            'pillars': {
                'driving': driving,
                'approach': approach,
                'short_game': short_game,
                'putting': putting
            },
            'tee_to_green': {
                'sg': (driving.get('sg_total', 0) + 
                      approach.get('sg_total', 0) + 
                      short_game.get('sg_total', 0))
            }
        }
    
    def calculate_sg_total(self, df: pd.DataFrame) -> Dict:
        """
        Calculate total SG metrics.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with SG totals
        """
        total_sg = df['strokes_gained'].sum()
        num_rounds = df['round_id'].nunique()
        
        return {
            'total_sg': total_sg,
            'sg_per_round': total_sg / num_rounds if num_rounds > 0 else 0,
            'num_rounds': num_rounds
        }
    
    def get_sg_separators(self, df: pd.DataFrame) -> Dict:
        """
        Calculate key SG separator metrics.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary of separator values
        """
        separators = {}
        
        # Putting 3-6 ft
        mask = (df['shot_category'] == 'putting') & \
               (df['starting_distance'] >= 3) & (df['starting_distance'] <= 6)
        separators['putting_3_6ft'] = df.loc[mask, 'strokes_gained'].sum()
        
        # Approach 100-150 yds
        mask = (df['shot_category'] == 'approach') & \
               (df['starting_distance'] >= 100) & (df['starting_distance'] < 150)
        separators['approach_100_150yd'] = df.loc[mask, 'strokes_gained'].sum()
        
        # Approach 150-200 yds
        mask = (df['shot_category'] == 'approach') & \
               (df['starting_distance'] >= 150) & (df['starting_distance'] < 200)
        separators['approach_150_200yd'] = df.loc[mask, 'strokes_gained'].sum()
        
        # Rough approach <150 yds
        mask = (df['shot_category'] == 'approach') & \
               (df['starting_location'] == 'Rough') & \
               (df['starting_distance'] < 150)
        separators['approach_rough_under150'] = df.loc[mask, 'strokes_gained'].sum()
        
        # Playable drives
        mask = (df['shot_category'] == 'driving') & \
               (df['ending_location'].isin(['Fairway', 'Rough'])) & \
               (df['penalty'] != 'Yes')
        separators['sg_playable_drives'] = df.loc[mask, 'strokes_gained'].sum()
        
        return separators
    
    def calculate_hole_outcomes(self, df: pd.DataFrame) -> Dict:
        """
        Calculate hole outcome distribution.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with outcome counts and percentages
        """
        hole_scores = df.groupby('hole')['score'].max()
        
        eagles = (hole_scores <= 1).sum()
        birdies = (hole_scores == 2).sum()
        pars = (hole_scores == 3).sum()
        bogeys = (hole_scores == 4).sum()
        doubles = (hole_scores >= 5).sum()
        total = len(hole_scores)
        
        return {
            'total_holes': total,
            'eagles': {'count': eagles, 'pct': eagles / total * 100},
            'birdies': {'count': birdies, 'pct': birdies / total * 100},
            'pars': {'count': pars, 'pct': pars / total * 100},
            'bogeys': {'count': bogeys, 'pct': bogeys / total * 100},
            'doubles_plus': {'count': doubles, 'pct': doubles / total * 100}
        }
