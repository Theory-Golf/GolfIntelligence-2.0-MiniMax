"""
Hole Summary Engine
Aggregates shot-level data into hole-level metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class HoleSummary:
    """Data class for hole-level summary."""
    round_id: str
    hole: int
    hole_score: int
    shots: int
    strokes_gained: float
    putts: int
    penalties: int
    score_vs_par: int
    par: int
    gir: bool
    fairway_hit: Optional[bool]
    up_and_down: bool
    sand_save: bool


class HoleSummaryEngine:
    """
    Engine for aggregating shot-level data into hole-level metrics.
    
    Provides:
    - Hole score calculation
    - GIR/FIR detection
    - Up-and-down detection
    - Sand save detection
    - Detailed hole statistics
    """
    
    def __init__(self, par_by_hole: Dict[int, int] = None):
        """
        Initialize hole summary engine.
        
        Args:
            par_by_hole: Dictionary mapping hole number to par (1-18)
        """
        self.par_by_hole = par_by_hole or {
            1: 4, 2: 5, 3: 3, 4: 4, 5: 4,
            6: 5, 7: 3, 8: 4, 9: 4,
            10: 4, 11: 5, 12: 3, 13: 4, 14: 4,
            15: 5, 16: 3, 17: 4, 18: 4
        }
    
    def calculate_hole_summaries(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate hole-level summaries from shot-level data.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            DataFrame with hole-level summaries
        """
        summaries = []
        
        for (round_id, hole), hole_data in df.groupby(['round_id', 'hole']):
            summary = self._calculate_single_hole(round_id, hole, hole_data)
            summaries.append(summary)
        
        return pd.DataFrame(summaries)
    
    def _calculate_single_hole(self, 
                               round_id: str, 
                               hole: int, 
                               hole_data: pd.DataFrame) -> Dict:
        """
        Calculate summary for a single hole.
        
        Args:
            round_id: Round identifier
            hole: Hole number
            hole_data: Shot data for this hole
            
        Returns:
            Dictionary with hole summary
        """
        # Basic metrics
        hole_score = hole_data['score'].max()
        shots = len(hole_data)
        strokes_gained = hole_data['strokes_gained'].sum()
        penalties = (hole_data['penalty'] == 'Yes').sum()
        par = self.par_by_hole.get(hole, 4)
        score_vs_par = hole_score - par
        
        # Putts
        putts = hole_data[hole_data['starting_location'] == 'Green'].shape[0]
        
        # Green in Regulation
        # GIR: hitting green in regulation (par-2 for par-4, etc.)
        gir_threshold = par - 2
        gir = False
        
        # Check if any shot ended on green within expected strokes
        green_shots = hole_data[hole_data['ending_location'] == 'Green']
        if len(green_shots) > 0:
            first_gir_shot = green_shots['shot'].min()
            if first_gir_shot <= gir_threshold:
                gir = True
        
        # Fairway in Regulation (for par-4 and par-5 holes)
        fir = None
        if par >= 4:
            # FIR: first shot ends on fairway
            first_shot = hole_data[hole_data['shot'] == 1]
            if len(first_shot) > 0:
                fir = first_shot['ending_location'].iloc[0] == 'Fairway'
        
        # Up-and-down (getting up and down to save par or better)
        up_and_down = False
        if not gir:
            # Check if got up and down to save par or better
            approach_shot = hole_data[
                (hole_data['shot_category'] == 'short_game') & 
                (hole_data['shot'] == hole_data['shot'].min())
            ]
            if len(approach_shot) > 0:
                approach_ended_green = approach_shot['ending_location'].iloc[0] == 'Green'
                if approach_ended_green and putts <= 2:
                    up_and_down = True
        
        # Sand save
        sand_save = False
        sand_shots = hole_data[hole_data['starting_location'] == 'Sand']
        if len(sand_shots) > 0:
            # First sand shot
            first_sand = sand_shots[sand_shots['shot'] == sand_shots['shot'].min()]
            if len(first_sand) > 0:
                sand_ended_green = first_sand['ending_location'].iloc[0] == 'Green'
                if sand_ended_green and putts <= 2:
                    sand_save = True
        
        return {
            'round_id': round_id,
            'hole': hole,
            'par': par,
            'hole_score': hole_score,
            'score_vs_par': score_vs_par,
            'shots': shots,
            'strokes_gained': strokes_gained,
            'putts': putts,
            'penalties': penalties,
            'gir': gir,
            'fir': fir,
            'up_and_down': up_and_down,
            'sand_save': sand_save,
            'putts_per_gir': shots - putts if gir else None
        }
    
    def calculate_season_hole_stats(self, hole_summaries: pd.DataFrame) -> Dict:
        """
        Calculate season-level hole statistics.
        
        Args:
            hole_summaries: DataFrame from calculate_hole_summaries
            
        Returns:
            Dictionary with season statistics
        """
        if len(hole_summaries) == 0:
            return {}
        
        total_holes = len(hole_summaries)
        
        # Score distribution
        eagles = (hole_summaries['hole_score'] <= 1).sum()
        birdies = (hole_summaries['hole_score'] == 2).sum()
        pars = (hole_summaries['hole_score'] == 3).sum()
        bogeys = (hole_summaries['hole_score'] == 4).sum()
        doubles = (hole_summaries['hole_score'] == 5).sum()
        worse = (hole_summaries['hole_score'] >= 6).sum()
        
        # GIR and FIR rates
        gir_count = hole_summaries['gir'].sum()
        fir_count = hole_summaries['fir'].sum()
        fir_opportunities = hole_summaries['fir'].notna().sum()
        
        up_and_downs = hole_summaries['up_and_down'].sum()
        sand_saves = hole_summaries['sand_save'].sum()
        
        return {
            'total_holes': total_holes,
            'scoring': {
                'average': hole_summaries['hole_score'].mean(),
                'eagles': eagles,
                'birdies': birdies,
                'pars': pars,
                'bogeys': bogeys,
                'doubles': doubles,
                'worse': worse,
                'eagle_rate': eagles / total_holes * 100,
                'birdie_rate': birdies / total_holes * 100,
                'par_rate': pars / total_holes * 100,
                'bogey_rate': bogeys / total_holes * 100,
                'double_plus_rate': (doubles + worse) / total_holes * 100
            },
            'gir': {
                'count': gir_count,
                'rate': gir_count / total_holes * 100
            },
            'fir': {
                'count': fir_count,
                'rate': fir_count / fir_opportunities * 100 if fir_opportunities > 0 else 0
            },
            'short_game': {
                'up_and_downs': up_and_downs,
                'up_and_down_rate': 0  # Only calculated on missed GIR
            },
            'sand': {
                'saves': sand_saves,
                'sand_save_rate': 0  # Only calculated on sand shots
            },
            'putting': {
                'total_putts': hole_summaries['putts'].sum(),
                'putts_per_hole': hole_summaries['putts'].mean(),
                'three_putts': (hole_summaries['putts'] >= 3).sum(),
                'three_putt_rate': (hole_summaries['putts'] >= 3).sum() / total_holes * 100
            }
        }
    
    def calculate_hole_by_hole_performance(self, 
                                           hole_summaries: pd.DataFrame,
                                           hole: int) -> Dict:
        """
        Calculate performance on a specific hole.
        
        Args:
            hole_summaries: DataFrame from calculate_hole_summaries
            hole: Hole number (1-18)
            
        Returns:
            Dictionary with hole-specific performance
        """
        hole_data = hole_summaries[hole_summaries['hole'] == hole]
        
        if len(hole_data) == 0:
            return {}
        
        par = self.par_by_hole.get(hole, 4)
        
        return {
            'hole': hole,
            'par': par,
            'rounds_played': len(hole_data),
            'scoring': {
                'average': hole_data['hole_score'].mean(),
                'total': hole_data['hole_score'].sum(),
                'vs_par': (hole_data['hole_score'] - par).sum()
            },
            'eagles': (hole_data['hole_score'] <= 1).sum(),
            'birdies': (hole_data['hole_score'] == 2).sum(),
            'pars': (hole_data['hole_score'] == 3).sum(),
            'bogeys': (hole_data['hole_score'] == 4).sum(),
            'doubles_plus': (hole_data['hole_score'] >= 5).sum(),
            'gir_rate': hole_data['gir'].mean() * 100,
            'strokes_gained_avg': hole_data['strokes_gained'].mean()
        }
    
    def get_hole_map_data(self, hole_summaries: pd.DataFrame) -> pd.DataFrame:
        """
        Get data for hole map visualization.
        
        Args:
            hole_summaries: DataFrame from calculate_hole_summaries
            
        Returns:
            DataFrame suitable for hole map visualization
        """
        return hole_summaries.groupby('hole').agg({
            'hole_score': ['mean', 'std'],
            'strokes_gained': 'sum',
            'score_vs_par': ['sum', 'mean'],
            'gir': 'mean',
            'putts': 'mean'
        }).reset_index()
    
    def identify_hardest_holes(self, 
                               hole_summaries: pd.DataFrame,
                               n: int = 5) -> pd.DataFrame:
        """
        Identify the n hardest holes by score vs par.
        
        Args:
            hole_summaries: DataFrame from calculate_hole_summaries
            n: Number of holes to return
            
        Returns:
            DataFrame with hardest holes
        """
        hardest = hole_summaries.groupby('hole').agg({
            'score_vs_par': 'mean',
            'strokes_gained': 'mean',
            'hole_score': 'mean'
        }).reset_index()
        
        hardest.columns = ['hole', 'avg_vs_par', 'avg_sg', 'avg_score']
        hardest = hardest.sort_values('avg_vs_par', ascending=False)
        
        # Add par
        hardest['par'] = hardest['hole'].map(self.par_by_hole)
        
        return hardest.head(n)
    
    def identify_easiest_holes(self, 
                              hole_summaries: pd.DataFrame,
                              n: int = 5) -> pd.DataFrame:
        """
        Identify the n easiest holes by score vs par.
        
        Args:
            hole_summaries: DataFrame from calculate_hole_summaries
            n: Number of holes to return
            
        Returns:
            DataFrame with easiest holes
        """
        easiest = hole_summaries.groupby('hole').agg({
            'score_vs_par': 'mean',
            'strokes_gained': 'mean',
            'hole_score': 'mean'
        }).reset_index()
        
        easiest.columns = ['hole', 'avg_vs_par', 'avg_sg', 'avg_score']
        easiest = easiest.sort_values('avg_vs_par', ascending=True)
        
        # Add par
        easiest['par'] = easiest['hole'].map(self.par_by_hole)
        
        return easiest.head(n)
