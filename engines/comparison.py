"""
Comparison Engine
Compares performance across different dimensions
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from core.small_sample_analytics import SmallSampleAnalytics


@dataclass
class ComparisonResult:
    """Data class for comparison results."""
    metric: str
    current: float
    baseline: float
    delta: float
    delta_pct: float
    confidence: str
    sample_size: int
    significance: bool
    interpretation: str


class ComparisonEngine:
    """
    Engine for comparing performance across different dimensions.
    
    Provides:
    - Tournament vs Season comparison
    - Round-to-round comparison
    - Player vs Benchmark comparison
    - Trend analysis
    """
    
    def __init__(self, benchmark_data: Dict = None):
        """
        Initialize comparison engine.
        
        Args:
            benchmark_data: Dictionary of benchmark metrics
        """
        self.benchmark_data = benchmark_data or {}
        self.small_sample = SmallSampleAnalytics()
    
    def compare_tournament_season(self,
                                tournament_df: pd.DataFrame,
                                season_df: pd.DataFrame) -> Dict[str, ComparisonResult]:
        """
        Compare tournament performance vs season average.
        
        Args:
            tournament_df: Tournament (recent 3 rounds) DataFrame
            season_df: Season (all rounds) DataFrame
            
        Returns:
            Dictionary of ComparisonResult objects
        """
        comparisons = {}
        
        # Scoring average
        tournament_score = tournament_df.groupby('hole')['score'].max().mean()
        season_score = season_df.groupby('hole')['score'].max().mean()
        
        comparisons['scoring_average'] = ComparisonResult(
            metric='Scoring Average',
            current=tournament_score,
            baseline=season_score,
            delta=tournament_score - season_score,
            delta_pct=((tournament_score - season_score) / season_score * 100) if season_score != 0 else 0,
            confidence=self._get_confidence(tournament_df, season_df),
            sample_size=tournament_df['round_id'].nunique(),
            significance=abs(tournament_score - season_score) > 0.5,
            interpretation=self._interpret_score_diff(tournament_score - season_score)
        )
        
        # Total SG
        tournament_sg = tournament_df['strokes_gained'].sum()
        tournament_rounds = tournament_df['round_id'].nunique()
        season_sg = season_df['strokes_gained'].sum()
        season_rounds = season_df['round_id'].nunique()
        
        comparisons['sg_total'] = ComparisonResult(
            metric='Strokes Gained Total',
            current=tournament_sg / tournament_rounds if tournament_rounds > 0 else 0,
            baseline=season_sg / season_rounds if season_rounds > 0 else 0,
            delta=tournament_sg / tournament_rounds - season_sg / season_rounds,
            delta_pct=0,
            confidence=self._get_confidence(tournament_df, season_df),
            sample_size=tournament_rounds,
            significance=abs(tournament_sg / tournament_rounds - season_sg / season_rounds) > 0.5,
            interpretation=self._interpret_sg_diff(tournament_sg / tournament_rounds - season_sg / season_rounds)
        )
        
        # Fairway percentage
        tournament_fw = self._calculate_fairway_pct(tournament_df)
        season_fw = self._calculate_fairway_pct(season_df)
        
        comparisons['fairway_pct'] = ComparisonResult(
            metric='Fairway Percentage',
            current=tournament_fw,
            baseline=season_fw,
            delta=tournament_fw - season_fw,
            delta_pct=((tournament_fw - season_fw) / season_fw * 100) if season_fw != 0 else 0,
            confidence=self._get_confidence(tournament_df, season_df),
            sample_size=tournament_df['round_id'].nunique(),
            significance=abs(tournament_fw - season_fw) > 3,
            interpretation=self._interpret_pct_diff(tournament_fw - season_fw, 'fairway')
        )
        
        # GIR percentage
        tournament_gir = self._calculate_gir_pct(tournament_df)
        season_gir = self._calculate_gir_pct(season_df)
        
        comparisons['gir_pct'] = ComparisonResult(
            metric='GIR Percentage',
            current=tournament_gir,
            baseline=season_gir,
            delta=tournament_gir - season_gir,
            delta_pct=((tournament_gir - season_gir) / season_gir * 100) if season_gir != 0 else 0,
            confidence=self._get_confidence(tournament_df, season_df),
            sample_size=tournament_df['round_id'].nunique(),
            significance=abs(tournament_gir - season_gir) > 3,
            interpretation=self._interpret_pct_diff(tournament_gir - season_gir, 'gir')
        )
        
        # Putting average
        tournament_putts = self._calculate_putts_per_hole(tournament_df)
        season_putts = self._calculate_putts_per_hole(season_df)
        
        comparisons['putts_per_hole'] = ComparisonResult(
            metric='Putts Per Hole',
            current=tournament_putts,
            baseline=season_putts,
            delta=tournament_putts - season_putts,
            delta_pct=((tournament_putts - season_putts) / season_putts * 100) if season_putts != 0 else 0,
            confidence=self._get_confidence(tournament_df, season_df),
            sample_size=tournament_df['round_id'].nunique(),
            significance=abs(tournament_putts - season_putts) > 0.2,
            interpretation=self._interpret_putts_diff(tournament_putts - season_putts)
        )
        
        return comparisons
    
    def compare_against_benchmark(self,
                                 df: pd.DataFrame,
                                 benchmark_key: str = 'pga_tour') -> Dict[str, ComparisonResult]:
        """
        Compare performance against a benchmark.
        
        Args:
            df: Current performance DataFrame
            benchmark_key: Key for benchmark comparison
            
        Returns:
            Dictionary of ComparisonResult objects
        """
        comparisons = {}
        
        # Get benchmark data
        benchmark = self.benchmark_data.get(benchmark_key, {})
        
        # Calculate current metrics
        current_sg = df['strokes_gained'].sum() / df['round_id'].nunique() if df['round_id'].nunique() > 0 else 0
        benchmark_sg = benchmark.get('sg_per_round', 0)
        
        comparisons['sg_vs_benchmark'] = ComparisonResult(
            metric='SG vs Benchmark',
            current=current_sg,
            baseline=benchmark_sg,
            delta=current_sg - benchmark_sg,
            delta_pct=0,
            confidence='HIGH',
            sample_size=df['round_id'].nunique(),
            significance=abs(current_sg - benchmark_sg) > 0.5,
            interpretation=self._interpret_sg_diff(current_sg - benchmark_sg)
        )
        
        return comparisons
    
    def compare_best_worst_rounds(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Identify best and worst rounds.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Tuple of (best_rounds_df, worst_rounds_df)
        """
        round_stats = df.groupby('round_id').agg({
            'strokes_gained': 'sum',
            'score': lambda x: x.groupby(level='hole').max().mean()
        }).reset_index()
        
        round_stats.columns = ['round_id', 'total_sg', 'scoring_avg']
        
        # Sort by SG
        sorted_rounds = round_stats.sort_values('total_sg', ascending=False)
        
        best_rounds = sorted_rounds.head(3)
        worst_rounds = sorted_rounds.tail(3)
        
        return best_rounds, worst_rounds
    
    def compare_by_course(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compare performance across different courses.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            DataFrame with course comparisons
        """
        if 'course' not in df.columns:
            return pd.DataFrame()
        
        course_stats = df.groupby('course').agg({
            'strokes_gained': ['sum', 'mean'],
            'score': lambda x: x.groupby(level='hole').max().mean(),
            'round_id': 'nunique'
        }).reset_index()
        
        course_stats.columns = ['course', 'total_sg', 'sg_per_round', 'scoring_avg', 'rounds']
        
        return course_stats
    
    def compare_by_conditions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compare performance across different conditions.
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            DataFrame with condition comparisons
        """
        if 'weather_difficulty' not in df.columns:
            return pd.DataFrame()
        
        condition_stats = df.groupby('weather_difficulty').agg({
            'strokes_gained': ['sum', 'mean'],
            'score': lambda x: x.groupby(level='hole').max().mean()
        }).reset_index()
        
        condition_stats.columns = ['condition', 'total_sg', 'sg_per_round', 'scoring_avg']
        
        return condition_stats
    
    def trend_analysis(self, 
                      df: pd.DataFrame,
                      metric: str = 'strokes_gained',
                      periods: int = 5) -> Dict:
        """
        Analyze trends in a metric.
        
        Args:
            df: Shot-level DataFrame
            metric: Metric to analyze ('strokes_gained', 'score', etc.)
            periods: Number of periods to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        if metric == 'strokes_gained':
            period_data = df.groupby('round_id')['strokes_gained'].sum().reset_index()
        elif metric == 'score':
            period_data = df.groupby('round_id').apply(
                lambda x: x.groupby('hole')['score'].max().mean()
            ).reset_index()
            period_data.columns = ['round_id', metric]
        else:
            period_data = df.groupby('round_id')[metric].mean().reset_index()
        
        if len(period_data) < 2:
            return {'trend': 'insufficient_data'}
        
        # Calculate trend
        x = np.arange(len(period_data))
        y = period_data[metric].values
        
        # Simple linear regression
        if len(x) >= 2:
            slope = np.polyfit(x, y, 1)[0]
            
            if slope > 0.05:
                trend = 'improving'
            elif slope < -0.05:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        # Calculate consistency (coefficient of variation)
        cv = period_data[metric].std() / period_data[metric].mean() if period_data[metric].mean() != 0 else 0
        
        return {
            'trend': trend,
            'slope': slope if 'slope' in dir() else 0,
            'latest': y[-1] if len(y) > 0 else 0,
            'average': y.mean(),
            'consistency': cv,
            'data': period_data.to_dict('records')
        }
    
    def _get_confidence(self, current_df: pd.DataFrame, baseline_df: pd.DataFrame) -> str:
        """Determine confidence level based on sample size."""
        n_current = current_df['round_id'].nunique()
        n_baseline = baseline_df['round_id'].nunique()
        
        if n_current >= 10 and n_baseline >= 20:
            return 'HIGH'
        elif n_current >= 5 and n_baseline >= 10:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_fairway_pct(self, df: pd.DataFrame) -> float:
        """Calculate fairway hit percentage."""
        drives = df[df['shot_category'] == 'driving']
        if len(drives) == 0:
            return 0
        fairway_hits = drives[drives['ending_location'] == 'Fairway'].shape[0]
        return (fairway_hits / len(drives)) * 100
    
    def _calculate_gir_pct(self, df: pd.DataFrame) -> float:
        """Calculate GIR percentage."""
        approaches = df[df['shot_category'] == 'approach']
        if len(approaches) == 0:
            return 0
        green_hits = approaches[approaches['ending_location'] == 'Green'].shape[0]
        return (green_hits / len(approaches)) * 100
    
    def _calculate_putts_per_hole(self, df: pd.DataFrame) -> float:
        """Calculate putts per hole."""
        putts = df[df['starting_location'] == 'Green'].shape[0]
        holes = df['hole'].nunique()
        return putts / holes if holes > 0 else 0
    
    def _interpret_score_diff(self, diff: float) -> str:
        """Interpret scoring difference."""
        if diff < -0.5:
            return 'Significantly better than baseline'
        elif diff < 0:
            return 'Slightly better than baseline'
        elif diff == 0:
            return 'Same as baseline'
        elif diff <= 0.5:
            return 'Slightly worse than baseline'
        else:
            return 'Significantly worse than baseline'
    
    def _interpret_sg_diff(self, diff: float) -> str:
        """Interpret SG difference."""
        if diff > 0.5:
            return 'Significantly above baseline'
        elif diff > 0:
            return 'Slightly above baseline'
        elif diff == 0:
            return 'Same as baseline'
        elif diff >= -0.5:
            return 'Slightly below baseline'
        else:
            return 'Significantly below baseline'
    
    def _interpret_pct_diff(self, diff: float, metric_type: str) -> str:
        """Interpret percentage point difference."""
        if metric_type == 'fairway':
            threshold = 3
        else:
            threshold = 3
        
        if diff > threshold:
            return f'Significantly higher {metric_type} rate'
        elif diff > 0:
            return f'Slightly higher {metric_type} rate'
        elif diff == 0:
            return f'Same {metric_type} rate'
        elif diff >= -threshold:
            return f'Slightly lower {metric_type} rate'
        else:
            return f'Significantly lower {metric_type} rate'
    
    def _interpret_putts_diff(self, diff: float) -> str:
        """Interpret putts per hole difference."""
        if diff < -0.2:
            return 'Better than baseline (fewer putts)'
        elif diff < 0:
            return 'Slightly better than baseline'
        elif diff == 0:
            return 'Same as baseline'
        elif diff <= 0.2:
            return 'Slightly worse than baseline'
        else:
            return 'Worse than baseline (more putts)'
