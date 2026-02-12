"""
Scoring Performance Engine
Analyzes scoring issues by categorizing performance problems into distinct sections
based on root cause analysis using strokes gained data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class ScoringPerformanceEngine:
    """
    Specialized engine for scoring performance analysis.
    
    Analyzes:
    - Root causes of scoring issues by category
    - Three main sections: Double Bogey+, Bogey, Underperformance
    - Hero cards data aggregation
    - Trend analysis with dual-axis charts
    - Penalty and severe shot metrics
    """
    
    # Root cause categories
    ROOT_CAUSE_CATEGORIES = [
        'Short Putts',    # ≤ 6 feet
        'Mid Range',      # 7-15 feet
        'Lag Putts',      # 16+ feet
        'Driving',        # Drive shots
        'Approach',       # Approach shots
        'Short Game',     # Short Game shots
        'Recovery/Other'  # Recovery or Other shots
    ]
    
    def __init__(self):
        """Initialize the scoring performance engine."""
        pass
    
    def classify_shot_category(self, shot: pd.Series) -> str:
        """
        Classify a shot into a root cause category based on distance and type.
        
        Args:
            shot: A single shot record as pandas Series
            
        Returns:
            Root cause category string
        """
        distance = shot.get('starting_distance', 0)
        if pd.isna(distance):
            distance = 0
        
        shot_type = str(shot.get('shot_category', '')).lower()
        
        # Putting categories by distance
        if 'putt' in shot_type:
            if distance <= 6:
                return 'Short Putts'
            elif distance <= 15:
                return 'Mid Range'
            else:
                return 'Lag Putts'
        
        # Shot type categories
        if 'drive' in shot_type:
            return 'Driving'
        elif 'approach' in shot_type:
            return 'Approach'
        elif 'short game' in shot_type:
            return 'Short Game'
        else:
            return 'Recovery/Other'
    
    def identify_root_cause(self, hole_shots: pd.DataFrame) -> Optional[Dict]:
        """
        Identify the root cause shot for a hole by finding the shot with lowest SG.
        
        Args:
            hole_shots: DataFrame of all shots for a single hole
            
        Returns:
            Dictionary with root cause details, or None if no shots
        """
        if len(hole_shots) == 0:
            return None
        
        # Find the shot with lowest (most negative) SG
        lowest_idx = hole_shots['strokes_gained'].idxmin()
        lowest_shot = hole_shots.loc[lowest_idx]
        
        root_cause = self.classify_shot_category(lowest_shot)
        
        return {
            'hole': int(lowest_shot.get('hole', 0)),
            'round_id': lowest_shot.get('round_id', ''),
            'shot_number': int(lowest_shot.get('shot', 0)),
            'shot_type': str(lowest_shot.get('shot_category', '')),
            'distance': float(lowest_shot.get('starting_distance', 0)),
            'sg_value': float(lowest_shot['strokes_gained']),
            'root_cause': root_cause,
            'ending_location': str(lowest_shot.get('ending_location', '')),
            'penalty': str(lowest_shot.get('penalty', 'No'))
        }
    
    def calculate_hole_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate hole-level metrics from shot-level data.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            DataFrame with hole-level aggregations
        """
        # Group by round and hole
        hole_metrics = df.groupby(['round_id', 'hole']).agg({
            'score': 'max',  # Final score on hole
            'shot': 'count',  # Number of shots
            'strokes_gained': 'sum',  # Total SG on hole
            'penalty': lambda x: (x == 'Yes').sum()  # Penalty count
        }).reset_index()
        
        hole_metrics.columns = ['round_id', 'hole', 'hole_score', 'shots', 'hole_sg', 'penalties']
        
        # Calculate par based on first shot distance
        def get_par_from_distance(distance):
            if pd.isna(distance):
                return 3
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
        
        # Calculate par
        hole_metrics['par'] = hole_metrics['first_shot_distance'].apply(get_par_from_distance)
        
        # Calculate score vs par
        hole_metrics['score_vs_par'] = hole_metrics['hole_score'] - hole_metrics['par']
        
        # Calculate putts per hole
        putts = df[df['starting_location'] == 'Green'].groupby(['round_id', 'hole']).size().reset_index(name='putts')
        hole_metrics = hole_metrics.merge(putts, on=['round_id', 'hole'], how='left')
        hole_metrics['putts'] = hole_metrics['putts'].fillna(0)
        
        return hole_metrics
    
    def detect_three_putt(self, hole_shots: pd.DataFrame) -> bool:
        """
        Detect if a hole had a three-putt.
        
        Args:
            hole_shots: DataFrame of all shots for a single hole
            
        Returns:
            True if three-putt occurred
        """
        putts = hole_shots[hole_shots['starting_location'] == 'Green']
        return len(putts) >= 3
    
    def detect_short_game_miss(self, hole_shots: pd.DataFrame) -> bool:
        """
        Detect if a short game shot missed the green.
        
        Args:
            hole_shots: DataFrame of all shots for a single hole
            
        Returns:
            True if short game shot missed green
        """
        short_game_shots = hole_shots[
            (hole_shots['shot_category'] == 'short_game') | 
            (hole_shots['shot_category'] == 'Short Game')
        ]
        
        if len(short_game_shots) == 0:
            return False
        
        # Check if any short game shot didn't end on green
        missed = short_game_shots[short_game_shots['ending_location'] != 'Green']
        return len(missed) > 0
    
    def analyze_double_bogey_plus(self, hole_df: pd.DataFrame, shot_df: pd.DataFrame) -> Dict:
        """
        Section 1: Analyze holes where score >= +2 over par.
        
        Args:
            hole_df: Hole-level DataFrame
            shot_df: Shot-level DataFrame
            
        Returns:
            Dictionary with analysis results
        """
        # Filter holes with score >= +2 over par
        double_bogey_holes = hole_df[hole_df['score_vs_par'] >= 2]
        
        if len(double_bogey_holes) == 0:
            return {
                'total_holes': 0,
                'root_causes': [],
                'category_counts': {},
                'category_sg': {},
                'penalty_percentage': 0,
                'severe_percentage': 0
            }
        
        root_causes = []
        
        for _, hole in double_bogey_holes.iterrows():
            hole_shots = shot_df[
                (shot_df['round_id'] == hole['round_id']) & 
                (shot_df['hole'] == hole['hole'])
            ]
            
            root_cause = self.identify_root_cause(hole_shots)
            if root_cause:
                root_cause['hole_score'] = int(hole['hole_score'])
                root_cause['score_vs_par'] = int(hole['score_vs_par'])
                root_cause['par'] = int(hole['par'])
                root_cause['putts'] = int(hole.get('putts', 0))
                root_cause['penalties'] = int(hole.get('penalties', 0))
                
                # Check for multiple severe shots (SG <= -0.5)
                severe_shots = hole_shots[hole_shots['strokes_gained'] <= -0.5]
                root_cause['severe_shot_count'] = len(severe_shots)
                root_cause['multiple_severe'] = len(severe_shots) >= 2
                
                root_causes.append(root_cause)
        
        # Aggregate by category
        category_counts = defaultdict(int)
        category_sg = defaultdict(float)
        
        for rc in root_causes:
            cat = rc['root_cause']
            category_counts[cat] += 1
            category_sg[cat] += rc['sg_value']
        
        # Calculate penalty percentage
        holes_with_penalty = sum(1 for rc in root_causes if rc.get('penalties', 0) > 0)
        penalty_percentage = (holes_with_penalty / len(double_bogey_holes) * 100) if len(double_bogey_holes) > 0 else 0
        
        # Calculate severe shot percentage (2+ severe shots)
        holes_multiple_severe = sum(1 for rc in root_causes if rc.get('multiple_severe', False))
        severe_percentage = (holes_multiple_severe / len(double_bogey_holes) * 100) if len(double_bogey_holes) > 0 else 0
        
        return {
            'total_holes': len(double_bogey_holes),
            'root_causes': root_causes,
            'category_counts': dict(category_counts),
            'category_sg': dict(category_sg),
            'penalty_percentage': penalty_percentage,
            'severe_percentage': severe_percentage,
            'multiple_severe_count': holes_multiple_severe
        }
    
    def analyze_bogey(self, hole_df: pd.DataFrame, shot_df: pd.DataFrame) -> Dict:
        """
        Section 2: Analyze holes where score = +1 over par.
        
        Args:
            hole_df: Hole-level DataFrame
            shot_df: Shot-level DataFrame
            
        Returns:
            Dictionary with analysis results
        """
        # Filter holes with score exactly +1 over par
        bogey_holes = hole_df[hole_df['score_vs_par'] == 1]
        
        if len(bogey_holes) == 0:
            return {
                'total_holes': 0,
                'root_causes': [],
                'category_counts': {},
                'category_sg': {},
                'penalty_percentage': 0
            }
        
        root_causes = []
        
        for _, hole in bogey_holes.iterrows():
            hole_shots = shot_df[
                (shot_df['round_id'] == hole['round_id']) & 
                (shot_df['hole'] == hole['hole'])
            ]
            
            root_cause = self.identify_root_cause(hole_shots)
            if root_cause:
                root_cause['hole_score'] = int(hole['hole_score'])
                root_cause['score_vs_par'] = int(hole['score_vs_par'])
                root_cause['par'] = int(hole['par'])
                root_cause['putts'] = int(hole.get('putts', 0))
                root_cause['penalties'] = int(hole.get('penalties', 0))
                
                root_causes.append(root_cause)
        
        # Aggregate by category
        category_counts = defaultdict(int)
        category_sg = defaultdict(float)
        
        for rc in root_causes:
            cat = rc['root_cause']
            category_counts[cat] += 1
            category_sg[cat] += rc['sg_value']
        
        # Calculate penalty percentage
        holes_with_penalty = sum(1 for rc in root_causes if rc.get('penalties', 0) > 0)
        penalty_percentage = (holes_with_penalty / len(bogey_holes) * 100) if len(bogey_holes) > 0 else 0
        
        return {
            'total_holes': len(bogey_holes),
            'root_causes': root_causes,
            'category_counts': dict(category_counts),
            'category_sg': dict(category_sg),
            'penalty_percentage': penalty_percentage
        }
    
    def analyze_underperformance(self, hole_df: pd.DataFrame, shot_df: pd.DataFrame) -> Dict:
        """
        Section 3: Analyze underperformance holes (par or better with scoring issues).
        
        Underperformance defined as:
        - Score is par or better AND
        - Had either a three-putt OR a short game shot that missed the green
        
        Args:
            hole_df: Hole-level DataFrame
            shot_df: Shot-level DataFrame
            
        Returns:
            Dictionary with analysis results
        """
        # Filter holes with score <= par
        good_score_holes = hole_df[hole_df['score_vs_par'] <= 0]
        
        underperformance_holes = []
        
        for _, hole in good_score_holes.iterrows():
            hole_shots = shot_df[
                (shot_df['round_id'] == hole['round_id']) & 
                (shot_df['hole'] == hole['hole'])
            ]
            
            # Check for underperformance conditions
            is_three_putt = self.detect_three_putt(hole_shots)
            is_short_game_miss = self.detect_short_game_miss(hole_shots)
            
            if is_three_putt or is_short_game_miss:
                underperformance_holes.append({
                    **hole.to_dict(),
                    'hole_shots': hole_shots,
                    'three_putt': is_three_putt,
                    'short_game_miss': is_short_game_miss
                })
        
        if len(underperformance_holes) == 0:
            return {
                'total_holes': 0,
                'root_causes': [],
                'category_counts': {},
                'category_sg': {},
                'three_putt_count': 0,
                'short_game_miss_count': 0
            }
        
        root_causes = []
        three_putt_count = 0
        short_game_miss_count = 0
        
        for hole_info in underperformance_holes:
            hole_shots = hole_info.pop('hole_shots')
            
            root_cause = self.identify_root_cause(hole_shots)
            if root_cause:
                root_cause['hole_score'] = int(hole_info.get('hole_score', 0))
                root_cause['score_vs_par'] = int(hole_info.get('score_vs_par', 0))
                root_cause['par'] = int(hole_info.get('par', 0))
                root_cause['putts'] = int(hole_info.get('putts', 0))
                root_cause['three_putt'] = hole_info.get('three_putt', False)
                root_cause['short_game_miss'] = hole_info.get('short_game_miss', False)
                
                if root_cause['three_putt']:
                    three_putt_count += 1
                if root_cause['short_game_miss']:
                    short_game_miss_count += 1
                
                root_causes.append(root_cause)
        
        # Aggregate by category
        category_counts = defaultdict(int)
        category_sg = defaultdict(float)
        
        for rc in root_causes:
            cat = rc['root_cause']
            category_counts[cat] += 1
            category_sg[cat] += rc['sg_value']
        
        return {
            'total_holes': len(underperformance_holes),
            'root_causes': root_causes,
            'category_counts': dict(category_counts),
            'category_sg': dict(category_sg),
            'three_putt_count': three_putt_count,
            'short_game_miss_count': short_game_miss_count
        }
    
    def calculate_hero_cards(self, 
                            double_bogey: Dict, 
                            bogey: Dict, 
                            underperformance: Dict) -> Dict:
        """
        Calculate hero cards data by aggregating all sections.
        
        Args:
            double_bogey: Double Bogey+ analysis results
            bogey: Bogey analysis results
            underperformance: Underperformance analysis results
            
        Returns:
            Dictionary with hero card data for each category
        """
        hero_data = {}
        
        for category in self.ROOT_CAUSE_CATEGORIES:
            # Sum counts from all sections
            db_count = double_bogey.get('category_counts', {}).get(category, 0)
            b_count = bogey.get('category_counts', {}).get(category, 0)
            up_count = underperformance.get('category_counts', {}).get(category, 0)
            
            # Sum SG from all sections
            db_sg = double_bogey.get('category_sg', {}).get(category, 0)
            b_sg = bogey.get('category_sg', {}).get(category, 0)
            up_sg = underperformance.get('category_sg', {}).get(category, 0)
            
            hero_data[category] = {
                'count': db_count + b_count + up_count,
                'total_sg': db_sg + b_sg + up_sg,
                'double_bogey_count': db_count,
                'bogey_count': b_count,
                'underperformance_count': up_count
            }
        
        return hero_data
    
    def calculate_trend_analysis(self,
                                 double_bogey: Dict,
                                 bogey: Dict,
                                 underperformance: Dict) -> Dict:
        """
        Calculate trend data for dual-axis chart.
        
        Args:
            double_bogey: Double Bogey+ analysis results
            bogey: Bogey analysis results
            underperformance: Underperformance analysis results
            
        Returns:
            Dictionary with trend data for charting
        """
        # Get all unique rounds
        rounds_db = set(rc.get('round_id', '') for rc in double_bogey.get('root_causes', []))
        rounds_b = set(rc.get('round_id', '') for rc in bogey.get('root_causes', []))
        rounds_up = set(rc.get('round_id', '') for rc in underperformance.get('root_causes', []))
        
        all_rounds = sorted(rounds_db | rounds_b | rounds_up)
        
        if not all_rounds:
            return {'data': [], 'categories': self.ROOT_CAUSE_CATEGORIES}
        
        trend_data = []
        
        for round_id in all_rounds:
            round_entry = {'round': round_id}
            
            # Get counts by category for this round
            for category in self.ROOT_CAUSE_CATEGORIES:
                round_entry[category] = 0
            
            # Count from each section
            for rc in double_bogey.get('root_causes', []):
                if rc.get('round_id') == round_id:
                    round_entry[rc.get('root_cause', '')] += 1
            
            for rc in bogey.get('root_causes', []):
                if rc.get('round_id') == round_id:
                    round_entry[rc.get('root_cause', '')] += 1
            
            for rc in underperformance.get('root_causes', []):
                if rc.get('round_id') == round_id:
                    round_entry[rc.get('root_cause', '')] += 1
            
            # Calculate total fails for this round
            total_fails = (
                sum(1 for rc in double_bogey.get('root_causes', []) if rc.get('round_id') == round_id) +
                sum(1 for rc in bogey.get('root_causes', []) if rc.get('round_id') == round_id) +
                sum(1 for rc in underperformance.get('root_causes', []) if rc.get('round_id') == round_id)
            )
            round_entry['total_fails'] = total_fails
            
            trend_data.append(round_entry)
        
        return {
            'data': trend_data,
            'categories': self.ROOT_CAUSE_CATEGORIES
        }
    
    def calculate_penalty_metrics(self,
                                 double_bogey: Dict,
                                 bogey: Dict,
                                 shot_df: pd.DataFrame) -> Dict:
        """
        Calculate penalty and severe shot metrics.
        
        Args:
            double_bogey: Double Bogey+ analysis results
            bogey: Bogey analysis results
            shot_df: Shot-level DataFrame for additional analysis
            
        Returns:
            Dictionary with penalty metrics
        """
        # Bogey holes with penalty
        bogey_penalty_pct = bogey.get('penalty_percentage', 0)
        
        # Double Bogey+ holes with penalty
        double_bogey_penalty_pct = double_bogey.get('penalty_percentage', 0)
        
        # Double Bogey holes with 2+ severe shots
        double_bogey_severe_pct = double_bogey.get('severe_percentage', 0)
        
        return {
            'bogey_with_penalty_pct': bogey_penalty_pct,
            'double_bogey_with_penalty_pct': double_bogey_penalty_pct,
            'double_bogey_multiple_severe_pct': double_bogey_severe_pct,
            'bogey_total': bogey.get('total_holes', 0),
            'double_bogey_total': double_bogey.get('total_holes', 0)
        }
    
    def get_root_cause_detail(self,
                             double_bogey: Dict,
                             bogey: Dict,
                             underperformance: Dict) -> pd.DataFrame:
        """
        Get shot-level detail data organized by root cause category.
        
        Args:
            double_bogey: Double Bogey+ analysis results
            bogey: Bogey analysis results
            underperformance: Underperformance analysis results
            
        Returns:
            DataFrame with detailed root cause information
        """
        all_root_causes = []
        
        # Add section type to each record
        for rc in double_bogey.get('root_causes', []):
            rc_copy = rc.copy()
            rc_copy['section'] = 'Double Bogey+'
            all_root_causes.append(rc_copy)
        
        for rc in bogey.get('root_causes', []):
            rc_copy = rc.copy()
            rc_copy['section'] = 'Bogey'
            all_root_causes.append(rc_copy)
        
        for rc in underperformance.get('root_causes', []):
            rc_copy = rc.copy()
            rc_copy['section'] = 'Underperformance'
            all_root_causes.append(rc_copy)
        
        if not all_root_causes:
            return pd.DataFrame()
        
        return pd.DataFrame(all_root_causes)
    
    def calculate_scoring_summary(self,
                                 hole_df: pd.DataFrame,
                                 double_bogey: Dict,
                                 bogey: Dict,
                                 underperformance: Dict) -> Dict:
        """
        Calculate overall scoring summary.
        
        Args:
            hole_df: Hole-level DataFrame
            double_bogey: Double Bogey+ analysis results
            bogey: Bogey analysis results
            underperformance: Underperformance analysis results
            
        Returns:
            Dictionary with scoring summary
        """
        total_holes = len(hole_df)
        
        # Score distribution
        eagles = (hole_df['score_vs_par'] <= -2).sum()
        birdies = (hole_df['score_vs_par'] == -1).sum()
        pars = (hole_df['score_vs_par'] == 0).sum()
        bogeys = (hole_df['score_vs_par'] == 1).sum()
        doubles_or_worse = (hole_df['score_vs_par'] >= 2).sum()
        
        # Calculate scoring average
        scoring_avg = hole_df['hole_score'].mean()
        
        return {
            'total_holes': total_holes,
            'scoring_average': scoring_avg,
            'eagles': eagles,
            'birdies': birdies,
            'pars': pars,
            'bogeys': bogeys,
            'doubles_or_worse': doubles_or_worse,
            'double_bogey_count': double_bogey.get('total_holes', 0),
            'bogey_count': bogey.get('total_holes', 0),
            'underperformance_count': underperformance.get('total_holes', 0),
            'total_fails': (
                double_bogey.get('total_holes', 0) +
                bogey.get('total_holes', 0) +
                underperformance.get('total_holes', 0)
            )
        }
