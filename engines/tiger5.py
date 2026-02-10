"""
Tiger 5 Engine
Analyzes Tiger 5 fails and Grit Score
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class Tiger5Engine:
    """
    Specialized engine for Tiger 5 analysis.
    
    Calculates:
    - Tiger 5 fail counts by category
    - Grit Score
    - Fail trends
    - Root cause analysis
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize Tiger 5 engine.
        
        Args:
            config: Tiger 5 category definitions
        """
        self.config = config or self._default_config()
    
    def _default_config(self) -> dict:
        """Return default Tiger 5 configuration."""
        return {
            'categories': [
                {
                    'name': '3 Putts',
                    'attempts_field': 'putts',
                    'fail_condition': lambda df: df.get('putts', 0) >= 3
                },
                {
                    'name': 'Double Bogey',
                    'attempts_field': 'all',
                    'fail_condition': lambda df: df.get('score_vs_par', 0) >= 2
                },
                {
                    'name': 'Par 5 Bogey',
                    'attempts_field': 'par5',
                    'fail_condition': lambda df: (df.get('par', 3) == 5) & (df.get('hole_score', 0) >= 6)
                },
                {
                    'name': 'Missed Green',
                    'attempts_field': 'short_game',
                    'fail_condition': lambda df: df.get('missed_green', False) == True
                },
                {
                    'name': '125yd Bogey',
                    'attempts_field': 'scoring_shot',
                    'fail_condition': lambda df: (df.get('scoring_shot_sg', 0) < 0) & (df.get('hole_score', 0) > df.get('par', 3))
                }
            ]
        }
    
    def calculate_hole_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate hole-level metrics for Tiger 5 analysis.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            DataFrame with hole-level metrics
        """
        hole_metrics = df.groupby(['round_id', 'hole']).agg({
            'score': 'max',
            'shot': 'count',
            'strokes_gained': 'sum',
            'penalty': lambda x: (x == 'Yes').sum()
        }).reset_index()
        
        hole_metrics.columns = ['round_id', 'hole', 'hole_score', 'shots', 'hole_sg', 'penalties']
        
        # Calculate putts
        putts = df[df['starting_location'] == 'Green'].groupby(['round_id', 'hole']).size().reset_index(name='putts')
        hole_metrics = hole_metrics.merge(putts, on=['round_id', 'hole'], how='left')
        hole_metrics['putts'] = hole_metrics['putts'].fillna(0)
        
        # Calculate par based on first shot distance (tee shot)
        # Par 3: 0-240 yards
        # Par 4: 240-490 yards
        # Par 5: 490-600 yards
        def get_par_from_distance(distance):
            if pd.isna(distance):
                return 3  # Default to par 3 if no distance
            if distance < 240:
                return 3
            elif distance < 490:
                return 4
            else:
                return 5
        
        # Get first shot distance for each hole
        first_shots = df[df['shot'] == 1][['round_id', 'hole', 'starting_distance']].copy()
        first_shots.columns = ['round_id', 'hole', 'first_shot_distance']
        hole_metrics = hole_metrics.merge(first_shots, on=['round_id', 'hole'], how='left')
        
        # Calculate par from first shot distance
        hole_metrics['par'] = hole_metrics['first_shot_distance'].apply(get_par_from_distance)
        
        # Calculate score vs par
        hole_metrics['score_vs_par'] = hole_metrics['hole_score'] - hole_metrics['par']
        
        return hole_metrics
    
    def calculate_tiger5_fails(self, hole_df: pd.DataFrame) -> Dict:
        """
        Calculate Tiger 5 fails by category.
        
        Args:
            hole_df: Hole-level DataFrame
            
        Returns:
            Dictionary with fail counts and rates
        """
        # Handle empty or invalid input
        if hole_df is None or len(hole_df) == 0:
            return {
                'total_holes': 0,
                'categories': {},
                'grit_score': 100.0,
                'total_fails': 0,
                'total_attempts': 0
            }
        
        results = {
            'total_holes': len(hole_df),
            'categories': {},
            'grit_score': 0.0,
            'total_fails': 0,
            'total_attempts': 0
        }
        
        total_fails = 0
        total_attempts = 0
        
        for category in self.config['categories']:
            cat_name = category['name']
            attempts_col = category.get('attempts_field', 'all')
            
            # Calculate attempts
            if attempts_col == 'all':
                attempts = len(hole_df)
            elif attempts_col == 'par5':
                # Par 5 holes based on first shot distance
                par5_mask = hole_df.get('par', 3) == 5
                attempts = par5_mask.sum() if hasattr(par5_mask, 'sum') else len(hole_df[hole_df.get('par', 3) == 5])
            else:
                attempts = len(hole_df)
            
            # Calculate fails
            try:
                fail_mask = category['fail_condition'](hole_df)
                fails = int(fail_mask.sum()) if hasattr(fail_mask, 'sum') else int(fail_mask)
            except (KeyError, AttributeError, TypeError) as e:
                fails = 0
            
            fail_rate = (fails / attempts * 100) if attempts > 0 else 0
            
            results['categories'][cat_name] = {
                'attempts': attempts,
                'fails': fails,
                'fail_rate': fail_rate
            }
            
            total_fails += fails
            total_attempts += attempts
        
        results['total_fails'] = total_fails
        results['total_attempts'] = total_attempts
        
        # Calculate Grit Score
        if total_attempts > 0:
            results['grit_score'] = ((total_attempts - total_fails) / total_attempts) * 100
        
        return results
    
    def calculate_tiger5_trend(self, 
                              hole_df: pd.DataFrame,
                              round_ids: List[str]) -> Dict[str, Dict]:
        """
        Calculate Tiger 5 trend across rounds.
        
        Args:
            hole_df: Hole-level DataFrame
            round_ids: List of round IDs in order
            
        Returns:
            Dictionary of metrics by round
        """
        trends = {}
        
        for round_id in round_ids:
            round_holes = hole_df[hole_df['round_id'] == round_id]
            results = self.calculate_tiger5_fails(round_holes)
            trends[round_id] = results
        
        return trends
    
    def calculate_root_causes(self, 
                            hole_df: pd.DataFrame,
                            shot_df: pd.DataFrame) -> Dict:
        """
        Analyze root causes of Tiger 5 fails.
        
        Args:
            hole_df: Hole-level DataFrame with fails
            shot_df: Shot-level DataFrame
            
        Returns:
            Dictionary of root cause analysis
        """
        causes = {}
        
        # Get holes with Tiger 5 fails
        fail_holes = hole_df[hole_df['score_vs_par'] >= 2]['hole'].unique()
        
        if len(fail_holes) == 0:
            return {'message': 'No Tiger 5 fails found'}
        
        # Analyze patterns
        fail_shots = shot_df[shot_df['hole'].isin(fail_holes)]
        
        # Driving correlation
        driving_shots = fail_shots[fail_shots['shot_category'] == 'driving']
        fairway_miss_rate = (driving_shots['ending_location'] == 'Rough').mean() if len(driving_shots) > 0 else 0
        
        # Penalty correlation
        penalty_rate = (fail_shots['penalty'] == 'Yes').mean()
        
        # 3-putt analysis
        fail_hole_data = hole_df[hole_df['score_vs_par'] >= 2]
        three_putt_rate = (fail_hole_data['putts'] >= 3).mean() if len(fail_hole_data) > 0 else 0
        
        causes = {
            'driving': {
                'fairway_miss_rate': fairway_miss_rate,
                'penalty_rate': penalty_rate,
                'evidence': f"{fairway_miss_rate*100:.1f}% fairway misses on fail holes"
            },
            'putting': {
                'three_putt_rate': three_putt_rate,
                'evidence': f"{three_putt_rate*100:.1f}% of fail holes had 3+ putts"
            }
        }
        
        return causes
    
    def get_tiger5_scenarios(self, hole_df: pd.DataFrame) -> pd.DataFrame:
        """
        Get detailed breakdown of Tiger 5 fail scenarios.
        
        Args:
            hole_df: Hole-level DataFrame
            
        Returns:
            DataFrame with fail scenarios
        """
        scenarios = []
        
        for _, row in hole_df.iterrows():
            scenario = {
                'round_id': row['round_id'],
                'hole': row['hole'],
                'score': row['hole_score'],
                'score_vs_par': row['score_vs_par'],
                'putts': row.get('putts', 0),
                'fails': []
            }
            
            # Check each fail type
            if row.get('putts', 0) >= 3:
                scenario['fails'].append('3 Putts')
            if row.get('score_vs_par', 0) >= 2:
                scenario['fails'].append('Double Bogey')
            # Par 5 holes: check if hole has par of 5 (based on first shot distance)
            if row.get('par', 3) == 5 and row.get('hole_score', 0) >= 6:
                scenario['fails'].append('Par 5 Bogey')
            
            if scenario['fails']:
                scenarios.append(scenario)
        
        return pd.DataFrame(scenarios)
    
    def calculate_grit_score(self, results: Dict) -> float:
        """
        Calculate Grit Score.
        
        Args:
            results: Tiger 5 calculation results
            
        Returns:
            Grit Score (0-100)
        """
        total_attempts = results.get('total_attempts', 0)
        total_fails = results.get('total_fails', 0)
        
        if total_attempts == 0:
            return 100.0  # No attempts = perfect score
        
        return ((total_attempts - total_fails) / total_attempts) * 100
    
    def get_grit_interpretation(self, grit_score: float) -> Dict:
        """
        Get interpretation of Grit Score.
        
        Args:
            grit_score: Calculated Grit Score
            
        Returns:
            Dictionary with interpretation
        """
        if grit_score >= 85:
            return {
                'level': 'Excellent',
                'color': 'green',
                'message': 'Outstanding avoidance of blowup holes'
            }
        elif grit_score >= 75:
            return {
                'level': 'Good',
                'color': 'blue',
                'message': 'Solid performance with occasional struggles'
            }
        elif grit_score >= 65:
            return {
                'level': 'Needs Work',
                'color': 'orange',
                'message': 'Regular blowup holes hurting scoring'
            }
        else:
            return {
                'level': 'Critical',
                'color': 'red',
                'message': 'Frequent blowup holes - major improvement needed'
            }
