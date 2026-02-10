"""
Benchmark Engine Module
Handles Strokes Gained benchmark lookups and SG calculation
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
import streamlit as st


class BenchmarkEngine:
    """
    Handles benchmark loading and Strokes Gained calculations.
    
    Supports:
    - Multiple benchmark lookup tables
    - Distance bucketing
    - Location-based lookups
    - SG recalculation from raw shot data
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize benchmark engine.
        
        Args:
            config: Project configuration dictionary
        """
        self.config = config or {}
        self.benchmarks = {}
        self._load_benchmarks()
    
    def _load_benchmarks(self):
        """Load all benchmark lookup tables."""
        benchmarks_config = self.config.get('benchmarks', {})
        
        for key, cfg in benchmarks_config.items():
            filepath = Path(f"data/benchmarks/{cfg['filename']}")
            if filepath.exists():
                self.benchmarks[key] = self._load_benchmark_csv(filepath)
                st.cache_resource.clear()
            else:
                st.warning(f"Benchmark file not found: {filepath}")
    
    def _load_benchmark_csv(self, filepath: Path) -> Dict[Tuple[str, str], float]:
        """
        Load benchmark CSV and create lookup dictionary.
        
        Args:
            filepath: Path to benchmark CSV file
            
        Returns:
            Dictionary mapping (location, distance_bucket) -> expected_strokes
        """
        try:
            df = pd.read_csv(filepath)
            
            # Create lookup dictionary
            lookup = {}
            
            # Distance column is the first column
            distance_col = df.columns[0]
            lie_columns = df.columns[1:]
            
            for _, row in df.iterrows():
                distance = row[distance_col]
                
                for lie in lie_columns:
                    try:
                        expected_strokes = float(row[lie])
                        if not np.isnan(expected_strokes):
                            bucket = self._distance_to_bucket(distance)
                            lookup[(lie.lower(), bucket)] = expected_strokes
                    except (ValueError, TypeError):
                        continue
            
            return lookup
            
        except Exception as e:
            st.error(f"Error loading benchmark {filepath}: {e}")
            return {}
    
    def _distance_to_bucket(self, distance: float) -> str:
        """
        Convert distance to bucket string for lookup.
        
        Args:
            distance: Distance value
            
        Returns:
            Distance bucket string
        """
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
    
    def _get_lookup_key(self, location: str, distance: float) -> Tuple[str, str]:
        """
        Get standardized lookup key.
        
        Args:
            location: Location string
            distance: Distance value
            
        Returns:
            Tuple of (normalized_location, distance_bucket)
        """
        # Normalize location
        location_map = {
            'tee': 'tee',
            'fairway': 'fairway',
            'rough': 'rough',
            'sand': 'sand',
            'recovery': 'recovery',
            'green': 'putt',
            'putt': 'putt'
        }
        
        normalized_location = location_map.get(
            str(location).lower().strip(), 
            'putt'
        )
        
        bucket = self._distance_to_bucket(distance)
        
        return (normalized_location, bucket)
    
    def lookup(self, benchmark_key: str, location: str, distance: float) -> float:
        """
        Look up expected strokes for a given state.
        
        Args:
            benchmark_key: Benchmark identifier (a, b, c)
            location: Shot location (tee, fairway, rough, sand, recovery, green)
            distance: Distance to hole
            
        Returns:
            Expected strokes to hole out
        """
        if benchmark_key not in self.benchmarks:
            # Return default value
            return 2.0
        
        lookup_key = self._get_lookup_key(location, distance)
        
        # Try exact match first
        if lookup_key in self.benchmarks[benchmark_key]:
            return self.benchmarks[benchmark_key][lookup_key]
        
        # Try finding closest available distance
        return self._find_closest_value(benchmark_key, lookup_key)
    
    def _find_closest_value(self, benchmark_key: str, lookup_key: Tuple[str, str]) -> float:
        """
        Find closest available value when exact match not found.
        
        Args:
            benchmark_key: Benchmark identifier
            lookup_key: Tuple of (location, distance_bucket)
            
        Returns:
            Closest expected strokes value
        """
        location = lookup_key[0]
        
        # Find all entries for this location
        matching_keys = [
            (loc, dist) for (loc, dist) in self.benchmarks[benchmark_key].keys()
            if loc == location
        ]
        
        if not matching_keys:
            return 2.0  # Default fallback
        
        # Return average of all values for this location
        values = [
            self.benchmarks[benchmark_key][k] for k in matching_keys
        ]
        return float(np.mean(values))
    
    def compute_sg(self, 
                  benchmark_key: str,
                  starting_location: str,
                  starting_distance: float,
                  ending_location: str,
                  ending_distance: float,
                  penalty: bool = False) -> float:
        """
        Calculate Strokes Gained for a single shot.
        
        Formula:
        SG = Expected_Strokes(start) - Expected_Strokes(end) - strokes_consumed
        
        Args:
            benchmark_key: Benchmark to use
            starting_location: Where the shot started
            starting_distance: Distance before shot
            ending_location: Where the shot ended
            ending_distance: Distance after shot
            penalty: Whether penalty stroke was incurred
            
        Returns:
            Strokes Gained value
        """
        # Calculate expected strokes from start
        expected_start = self.lookup(
            benchmark_key, starting_location, starting_distance
        )
        
        # Calculate expected strokes from end
        expected_end = self.lookup(
            benchmark_key, ending_location, ending_distance
        )
        
        # Calculate strokes consumed (2 for penalty, 1 for normal)
        strokes_consumed = 2 if penalty else 1
        
        # SG formula
        sg = expected_start - expected_end - strokes_consumed
        
        return sg
    
    def compute_sg_for_shot(self, benchmark_key: str, shot_data: dict) -> float:
        """
        Calculate SG for a shot from shot data dictionary.
        
        Args:
            benchmark_key: Benchmark to use
            shot_data: Dictionary with shot information
            
        Returns:
            Strokes Gained value
        """
        return self.compute_sg(
            benchmark_key,
            shot_data.get('starting_location', 'tee'),
            shot_data.get('starting_distance', 300),
            shot_data.get('ending_location', 'fairway'),
            shot_data.get('ending_distance', 250),
            shot_data.get('penalty', 'No') == 'Yes'
        )
    
    def recompute_all_sg(self, 
                        df: pd.DataFrame, 
                        benchmark_key: str,
                        field_mapper) -> pd.DataFrame:
        """
        Recompute SG for entire DataFrame using selected benchmark.
        
        Args:
            df: DataFrame with shot data
            benchmark_key: Benchmark to use
            field_mapper: FieldMapper instance
            
        Returns:
            DataFrame with recomputed SG values
        """
        df = df.copy()
        
        sg_values = []
        for idx, row in df.iterrows():
            sg = self.compute_sg(
                benchmark_key,
                row.get('starting_location', 'tee'),
                row.get('starting_distance', 300),
                row.get('ending_location', 'fairway'),
                row.get('ending_distance', 250),
                row.get('penalty', 'No') == 'Yes'
            )
            sg_values.append(sg)
        
        df['strokes_gained'] = sg_values
        df['benchmark_used'] = benchmark_key
        
        return df
    
    def get_benchmark_info(self, benchmark_key: str) -> dict:
        """
        Get information about a benchmark.
        
        Args:
            benchmark_key: Benchmark identifier
            
        Returns:
            Dictionary with benchmark information
        """
        benchmarks_config = self.config.get('benchmarks', {})
        
        if benchmark_key in benchmarks_config:
            return benchmarks_config[benchmark_key]
        
        return {
            'display_name': 'Unknown',
            'description': 'Unknown benchmark'
        }
    
    def list_benchmarks(self) -> list:
        """List all available benchmarks."""
        return list(self.benchmarks.keys())
    
    def get_available_benchmarks(self) -> Dict[str, str]:
        """
        Get dictionary of available benchmarks for UI display.
        
        Returns:
            Dictionary mapping key -> display_name
        """
        benchmarks_config = self.config.get('benchmarks', {})
        return {
            key: cfg.get('display_name', key)
            for key, cfg in benchmarks_config.items()
            if key in self.benchmarks
        }
