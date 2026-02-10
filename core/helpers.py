"""
Helpers Module
Utility functions for golf analytics calculations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class Helpers:
    """
    Utility functions for golf analytics.
    
    Provides:
    - Distance bucketing
    - Score classification
    - Data formatting
    - Statistical helpers
    """
    
    # ==================== DISTANCE BUCKETING ====================
    
    @staticmethod
    def bucket_distance(distance: float, category: str = 'general') -> str:
        """
        Convert distance to bucket string.
        
        Args:
            distance: Distance value
            category: Type of shot (general, driving, approach, short_game, putting)
            
        Returns:
            Bucket string
        """
        if category == 'driving':
            if distance < 200:
                return "<200"
            elif distance < 250:
                return "200-250"
            elif distance < 300:
                return "250-300"
            else:
                return "300+"
        
        elif category == 'approach':
            if distance < 50:
                return "<50"
            elif distance < 100:
                return "50-100"
            elif distance < 150:
                return "100-150"
            elif distance < 200:
                return "150-200"
            else:
                return "200+"
        
        elif category == 'short_game':
            if distance < 10:
                return "<10"
            elif distance < 20:
                return "10-20"
            elif distance < 30:
                return "20-30"
            elif distance < 40:
                return "30-40"
            else:
                return "40-50"
        
        elif category == 'putting':
            if distance <= 3:
                return "0-3"
            elif distance <= 6:
                return "4-6"
            elif distance <= 10:
                return "7-10"
            elif distance <= 20:
                return "10-20"
            elif distance <= 30:
                return "20-30"
            else:
                return "30+"
        
        else:  # general
            if distance < 50:
                return "<50"
            elif distance < 100:
                return "50-100"
            elif distance < 150:
                return "100-150"
            elif distance < 200:
                return "150-200"
            elif distance < 250:
                return "200-250"
            elif distance < 300:
                return "250-300"
            else:
                return "300+"
    
    @staticmethod
    def bucket_for_sg_lookup(distance: float) -> int:
        """
        Get integer bucket for SG lookup table.
        
        Args:
            distance: Distance value
            
        Returns:
            Integer bucket (0-600)
        """
        if distance < 0:
            return 0
        elif distance > 600:
            return 600
        return int(distance)
    
    # ==================== SCORE CLASSIFICATION ====================
    
    @staticmethod
    def classify_score(score_vs_par: int) -> str:
        """
        Classify hole score relative to par.
        
        Args:
            score_vs_par: Score minus par
            
        Returns:
            Score classification
        """
        if score_vs_par <= -2:
            return "Eagle"
        elif score_vs_par == -1:
            return "Birdie"
        elif score_vs_par == 0:
            return "Par"
        elif score_vs_par == 1:
            return "Bogey"
        else:
            return "Double+"
    
    @staticmethod
    def score_name(score: int, par: int = 4) -> str:
        """
        Get descriptive name for a score.
        
        Args:
            score: Raw score number
            par: Par for the hole
            
        Returns:
            Score name (Eagle, Birdie, Par, Bogey, Double, etc.)
        """
        score_vs_par = score - par
        
        return Helpers.classify_score(score_vs_par)
    
    # ==================== ROUND CLASSIFICATION ====================
    
    @staticmethod
    def classify_round_score(score: int) -> str:
        """
        Classify overall round score.
        
        Args:
            score: Total score for round
            
        Returns:
            Classification
        """
        if score < 70:
            return "Under Par"
        elif score <= 73:
            return "Even to +3"
        else:
            return "+4 or Worse"
    
    # ==================== FORMATTING ====================
    
    @staticmethod
    def format_number(num: float, decimals: int = 2) -> str:
        """
        Format number with appropriate precision.
        
        Args:
            num: Number to format
            decimals: Decimal places
            
        Returns:
            Formatted string
        """
        if abs(num) < 0.01 and num != 0:
            return f"{num:.3f}"
        return f"{num:.{decimals}f}"
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """
        Format as percentage.
        
        Args:
            value: Value (0-100)
            decimals: Decimal places
            
        Returns:
            Formatted percentage string
        """
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_strokes_gained(sg: float) -> Tuple[str, str]:
        """
        Format strokes gained with sign and color.
        
        Args:
            sg: Strokes gained value
            
        Returns:
            Tuple of (formatted_string, color)
        """
        sign = "+" if sg >= 0 else ""
        formatted = f"{sign}{sg:.2f}"
        
        if sg > 0.1:
            return formatted, "green"
        elif sg < -0.1:
            return formatted, "red"
        else:
            return formatted, "gray"
    
    # ==================== DATE/TIME HELPERS ====================
    
    @staticmethod
    def get_date_range(df: pd.DataFrame) -> Tuple[datetime, datetime]:
        """
        Get min and max dates from DataFrame.
        
        Args:
            df: DataFrame with date column
            
        Returns:
            Tuple of (min_date, max_date)
        """
        dates = pd.to_datetime(df['date'])
        return dates.min(), dates.max()
    
    @staticmethod
    def filter_by_date(df: pd.DataFrame,
                      start_date: datetime,
                      end_date: datetime) -> pd.DataFrame:
        """
        Filter DataFrame by date range.
        
        Args:
            df: DataFrame with date column
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            Filtered DataFrame
        """
        dates = pd.to_datetime(df['date'])
        mask = (dates >= start_date) & (dates <= end_date)
        return df[mask]
    
    @staticmethod
    def get_recent_rounds(df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
        """
        Get most recent N rounds.
        
        Args:
            df: DataFrame with date column
            n: Number of recent rounds
            
        Returns:
            DataFrame with most recent rounds
        """
        sorted_df = df.sort_values('date', ascending=False)
        recent_round_ids = sorted_df['round_id'].unique()[:n]
        return df[df['round_id'].isin(recent_round_ids)]
    
    # ==================== STATISTICAL HELPERS ====================
    
    @staticmethod
    def safe_divide(a: float, b: float, default: float = 0.0) -> float:
        """
        Safely divide two numbers.
        
        Args:
            a: Numerator
            b: Denominator
            default: Value to return if b is zero
            
        Returns:
            a / b or default
        """
        return a / b if b != 0 else default
    
    @staticmethod
    def rolling_average(values: List[float], window: int = 3) -> List[float]:
        """
        Calculate rolling average.
        
        Args:
            values: List of values
            window: Window size
            
        Returns:
            List of rolling averages
        """
        if len(values) < window:
            return values
        
        results = []
        for i in range(len(values)):
            start = max(0, i - window + 1)
            window_vals = values[start:i + 1]
            results.append(sum(window_vals) / len(window_vals))
        
        return results
    
    @staticmethod
    def percentile_rank(value: float, reference: List[float]) -> float:
        """
        Calculate percentile rank of a value.
        
        Args:
            value: Value to rank
            reference: Reference distribution
            
        Returns:
            Percentile rank (0-100)
        """
        if len(reference) == 0:
            return 50.0
        
        below = sum(1 for v in reference if v < value)
        return (below / len(reference)) * 100
    
    # ==================== DATA TRANSFORMATION ====================
    
    @staticmethod
    def add_distance_buckets(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add distance bucket columns to DataFrame.
        
        Args:
            df: DataFrame with distance columns
            
        Returns:
            DataFrame with added bucket columns
        """
        df = df.copy()
        
        # General bucket
        df['distance_bucket'] = df['starting_distance'].apply(
            lambda x: Helpers.bucket_distance(x, 'general')
        )
        
        # Category-specific buckets
        df['driving_bucket'] = df['starting_distance'].apply(
            lambda x: Helpers.bucket_distance(x, 'driving')
        )
        
        df['approach_bucket'] = df['starting_distance'].apply(
            lambda x: Helpers.bucket_distance(x, 'approach')
        )
        
        df['short_game_bucket'] = df['starting_distance'].apply(
            lambda x: Helpers.bucket_distance(x, 'short_game')
        )
        
        df['putting_bucket'] = df['starting_distance'].apply(
            lambda x: Helpers.bucket_distance(x, 'putting')
        )
        
        return df
    
    @staticmethod
    def add_shot_categories(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add shot category column to DataFrame.
        
        Args:
            df: DataFrame with shot data
            
        Returns:
            DataFrame with shot_category column
        """
        df = df.copy()
        
        def categorize_shot(row):
            shot = row.get('shot', 0)
            starting_location = str(row.get('starting_location', '')).lower()
            starting_distance = row.get('starting_distance', 100)
            
            # Drive = Shot 1 from Tee
            if shot == 1 and starting_location == 'tee':
                return 'driving'
            
            # Putting = On green
            if starting_location == 'green':
                return 'putting'
            
            # Short game = <= 25 yards, not from tee
            if starting_distance <= 25 and starting_location != 'tee':
                return 'short_game'
            
            # Approach = Everything else
            return 'approach'
        
        df['shot_category'] = df.apply(categorize_shot, axis=1)
        
        return df
    
    # ==================== LOCATION HELPERS ====================
    
    @staticmethod
    def is_fairway(ending_location: str) -> bool:
        """Check if shot ended in fairway."""
        return str(ending_location).lower() == 'fairway'
    
    @staticmethod
    def is_green(ending_location: str) -> bool:
        """Check if shot ended on green."""
        return str(ending_location).lower() == 'green'
    
    @staticmethod
    def is_sand(ending_location: str) -> bool:
        """Check if shot ended in sand."""
        return str(ending_location).lower() == 'sand'
    
    @staticmethod
    def is_penalty(penalty: str) -> bool:
        """Check if shot had penalty."""
        return str(penalty).lower() == 'yes'
