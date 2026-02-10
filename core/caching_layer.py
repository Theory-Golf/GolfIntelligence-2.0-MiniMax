"""
Caching Layer Module
Handles data caching using DuckDB and Parquet for performance optimization
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import streamlit as st
from typing import Optional, Dict, Any
import hashlib
import json


class CachingLayer:
    """
    Manages data caching for improved performance.
    
    Uses:
    - Streamlit's built-in caching decorators for computed results
    - DuckDB for fast querying of large datasets
    - Parquet for efficient columnar storage
    """
    
    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize caching layer.
        
        Args:
            cache_dir: Directory for cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._setup_cache()
    
    def _setup_cache(self):
        """Set up cache storage."""
        # Cache metadata file
        self.meta_file = self.cache_dir / "cache_meta.json"
        
        if not self.meta_file.exists():
            self._save_metadata({})
    
    def _save_metadata(self, metadata: dict):
        """Save cache metadata."""
        with open(self.meta_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _load_metadata(self) -> dict:
        """Load cache metadata."""
        if self.meta_file.exists():
            with open(self.meta_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _generate_cache_key(self, data_hash: str, filters: dict) -> str:
        """Generate unique cache key for data + filter combination."""
        key_data = f"{data_hash}_{json.dumps(filters, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    def _get_data_hash(self, df: pd.DataFrame) -> str:
        """Generate hash of dataframe for change detection."""
        # Use shape, columns, and last few rows for hash
        hash_data = f"{df.shape}_{list(df.columns)}_{df.tail(5).to_dict()}"
        return hashlib.md5(hash_data.encode()).hexdigest()[:16]
    
    # ==================== STREAMLIT CACHING DECORATORS ====================
    
    @staticmethod
    @st.cache_data(ttl=3600)  # 1 hour cache
    def cache_dataframe(_df: pd.DataFrame) -> pd.DataFrame:
        """
        Cache a dataframe with 1 hour TTL.
        
        Args:
            _df: DataFrame to cache (underscore to prevent hashing)
            
        Returns:
            Cached DataFrame
        """
        return _df.copy()
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def cache_metric_computation(func):
        """
        Decorator to cache metric computation results.
        
        Usage:
            @cache_metric_computation
            def compute_tournament_metrics(filters):
                ...
        """
        return func
    
    @staticmethod
    @st.cache_resource
    def cache_benchmark_engine(engine):
        """
        Cache benchmark engine instance.
        
        Args:
            engine: BenchmarkEngine instance
            
        Returns:
            Cached engine instance
        """
        return engine
    
    # ==================== PARQUET OPERATIONS ====================
    
    def save_to_parquet(self, 
                      df: pd.DataFrame, 
                      name: str,
                      overwrite: bool = False) -> str:
        """
        Save DataFrame to Parquet file.
        
        Args:
            df: DataFrame to save
            name: Base name for file
            overwrite: Whether to overwrite existing file
            
        Returns:
            Path to saved file
        """
        filepath = self.cache_dir / f"{name}.parquet"
        
        if filepath.exists() and not overwrite:
            return str(filepath)
        
        df.to_parquet(filepath, index=False)
        
        # Update metadata
        metadata = self._load_metadata()
        metadata[name] = {
            'path': str(filepath),
            'saved_at': datetime.now().isoformat(),
            'rows': len(df),
            'columns': list(df.columns)
        }
        self._save_metadata(metadata)
        
        return str(filepath)
    
    def load_from_parquet(self, name: str) -> Optional[pd.DataFrame]:
        """
        Load DataFrame from Parquet file.
        
        Args:
            name: Base name of file
            
        Returns:
            DataFrame or None if not found
        """
        filepath = self.cache_dir / f"{name}.parquet"
        
        if filepath.exists():
            return pd.read_parquet(filepath)
        
        return None
    
    # ==================== FILTER-BASED CACHING ====================
    
    def get_filtered_data(self,
                         df: pd.DataFrame,
                         filters: Dict[str, Any],
                         cache_key: str = None) -> pd.DataFrame:
        """
        Get filtered data with optional caching.
        
        Args:
            df: Full DataFrame
            filters: Dictionary of filter conditions
            cache_key: Optional cache key
            
        Returns:
            Filtered DataFrame
        """
        if cache_key is None:
            cache_key = self._generate_cache_key(
                self._get_data_hash(df), 
                filters
            )
        
        # Try to load from cache
        cached = self.load_from_parquet(f"filtered_{cache_key}")
        if cached is not None:
            return cached
        
        # Apply filters
        filtered = df.copy()
        
        for column, value in filters.items():
            if column in filtered.columns:
                if isinstance(value, list):
                    filtered = filtered[filtered[column].isin(value)]
                else:
                    filtered = filtered[filtered[column] == value]
        
        # Cache the result
        self.save_to_parquet(filtered, f"filtered_{cache_key}")
        
        return filtered
    
    # ==================== CACHE MANAGEMENT ====================
    
    def clear_cache(self):
        """Clear all cached data."""
        for f in self.cache_dir.glob("*.parquet"):
            f.unlink()
        for f in self.cache_dir.glob("*.duckdb*"):
            f.unlink()
        self._save_metadata({})
    
    def get_cache_status(self) -> Dict:
        """
        Get cache status and statistics.
        
        Returns:
            Dictionary with cache status
        """
        metadata = self._load_metadata()
        
        cache_size = sum(
            f.stat().st_size 
            for f in self.cache_dir.glob("*") 
            if f.is_file()
        )
        
        return {
            'cache_dir': str(self.cache_dir),
            'files_count': len(list(self.cache_dir.glob("*"))),
            'total_size_bytes': cache_size,
            'total_size_mb': cache_size / (1024 * 1024),
            'cached_datasets': list(metadata.keys()),
            'last_updated': datetime.now().isoformat()
        }
    
    def is_cache_valid(self, name: str, max_age_hours: int = 24) -> bool:
        """
        Check if cached data is still valid.
        
        Args:
            name: Name of cached dataset
            max_age_hours: Maximum age in hours
            
        Returns:
            Boolean indicating if cache is valid
        """
        metadata = self._load_metadata()
        
        if name not in metadata:
            return False
        
        saved_at = datetime.fromisoformat(metadata[name]['saved_at'])
        age = datetime.now() - saved_at
        
        return age < timedelta(hours=max_age_hours)
    
    # ==================== PRECOMPUTED METRICS ====================
    
    def save_precomputed_metrics(self,
                               metrics: Dict,
                               name: str,
                               filters: Dict = None):
        """
        Save precomputed metrics to cache.
        
        Args:
            metrics: Dictionary of metrics
            name: Name of metrics
            filters: Filter conditions used
        """
        cache_data = {
            'metrics': metrics,
            'filters': filters or {},
            'computed_at': datetime.now().isoformat()
        }
        
        cache_key = self._generate_cache_key(
            json.dumps(metrics, sort_keys=True),
            filters or {}
        )
        
        filepath = self.cache_dir / f"metrics_{name}_{cache_key}.json"
        
        with open(filepath, 'w') as f:
            json.dump(cache_data, f, indent=2, default=str)
    
    def load_precomputed_metrics(self, 
                               name: str, 
                               filters: Dict = None) -> Optional[Dict]:
        """
        Load precomputed metrics from cache.
        
        Args:
            name: Name of metrics
            filters: Filter conditions
            
        Returns:
            Metrics dictionary or None
        """
        metadata = self._load_metadata()
        
        # Find matching cached metrics
        for f in self.cache_dir.glob(f"metrics_{name}_*.json"):
            try:
                with open(f, 'r') as file:
                    cache_data = json.load(file)
                
                # Check if filters match
                cached_filters = cache_data.get('filters', {})
                
                if cached_filters == (filters or {}):
                    return cache_data['metrics']
                    
            except Exception:
                continue
        
        return None
