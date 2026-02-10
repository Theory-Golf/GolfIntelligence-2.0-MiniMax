"""
Small Sample Analytics Module
Handles uncertainty quantification and confidence estimation for limited data
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from scipy import stats


class SmallSampleAnalytics:
    """
    Provides uncertainty quantification for small sample sizes.
    
    Key methods:
    - Bootstrap confidence intervals
    - Stability indicators
    - Consistency metrics
    - Confidence labeling
    """
    
    def __init__(self, 
                 bootstrap_samples: int = 100,
                 confidence_level: float = 0.95):
        """
        Initialize small sample analytics.
        
        Args:
            bootstrap_samples: Number of bootstrap resamples
            confidence_level: Confidence level for CIs (default 95%)
        """
        self.bootstrap_samples = bootstrap_samples
        self.confidence_level = confidence_level
    
    # ==================== BOOTSTRAP CONFIDENCE INTERVALS ====================
    
    def bootstrap_ci(self, 
                    data: np.ndarray, 
                    metric_name: str = None) -> Dict:
        """
        Calculate bootstrap confidence interval for a metric.
        
        Args:
            data: Array of metric values
            metric_name: Name of metric for reporting
            
        Returns:
            Dictionary with CI bounds and stability metrics
        """
        if len(data) < 2:
            return {
                'mean': np.mean(data) if len(data) > 0 else 0,
                'lower_bound': np.mean(data) if len(data) > 0 else 0,
                'upper_bound': np.mean(data) if len(data) > 0 else 0,
                'ci_width': 0,
                'stability': 'LOW',
                'n': len(data)
            }
        
        # Calculate original statistics
        original_mean = np.mean(data)
        original_std = np.std(data, ddof=1) if len(data) > 1 else 0
        
        # Bootstrap resampling
        np.random.seed(42)  # For reproducibility
        bootstrap_means = []
        
        for _ in range(self.bootstrap_samples):
            sample = np.random.choice(data, size=len(data), replace=True)
            bootstrap_means.append(np.mean(sample))
        
        bootstrap_means = np.array(bootstrap_means)
        
        # Calculate confidence interval
        alpha = 1 - self.confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        lower_bound = np.percentile(bootstrap_means, lower_percentile)
        upper_bound = np.percentile(bootstrap_means, upper_percentile)
        ci_width = upper_bound - lower_bound
        
        # Determine stability based on CI width and sample size
        stability = self._calculate_stability(len(data), ci_width)
        
        return {
            'mean': original_mean,
            'std': original_std,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'ci_width': ci_width,
            'stability': stability,
            'n': len(data),
            'bootstrap_means': bootstrap_means
        }
    
    def _calculate_stability(self, n: int, ci_width: float) -> str:
        """
        Categorize stability based on sample size and CI width.
        
        Args:
            n: Sample size
            ci_width: Width of confidence interval
            
        Returns:
            Stability category: HIGH, MEDIUM, or LOW
        """
        # Thresholds for stability
        high_threshold_n = 15
        medium_threshold_n = 10
        
        tight_ci_width = 0.5
        moderate_ci_width = 1.0
        
        if n >= high_threshold_n and ci_width <= tight_ci_width:
            return 'HIGH'
        elif n >= medium_threshold_n or ci_width <= moderate_ci_width:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    # ==================== CONSISTENCY METRICS ====================
    
    def calculate_consistency_metrics(self, data: np.ndarray) -> Dict:
        """
        Calculate various consistency/dispersion metrics.
        
        Args:
            data: Array of values
            
        Returns:
            Dictionary with consistency metrics
        """
        if len(data) < 2:
            return {
                'mean': np.mean(data) if len(data) > 0 else 0,
                'median': np.median(data) if len(data) > 0 else 0,
                'std': 0,
                'iqr': 0,
                'range': 0,
                'cv': 0,
                'n': len(data)
            }
        
        mean_val = np.mean(data)
        std_val = np.std(data, ddof=1)
        q1, q3 = np.percentile(data, [25, 75])
        
        return {
            'mean': mean_val,
            'median': np.median(data),
            'std': std_val,
            'iqr': q3 - q1,
            'range': np.max(data) - np.min(data),
            'cv': (std_val / mean_val * 100) if mean_val != 0 else 0,
            'n': len(data)
        }
    
    def calculate_trimmed_mean(self, 
                             data: np.ndarray, 
                             proportion: float = 0.2) -> float:
        """
        Calculate trimmed mean (less sensitive to outliers).
        
        Args:
            data: Array of values
            proportion: Proportion to trim from each end
            
        Returns:
            Trimmed mean value
        """
        if len(data) < 3:
            return np.mean(data)
        
        return stats.trim_mean(data, proportion)
    
    # ==================== CONFIDENCE LABELING ====================
    
    def confidence_label(self, 
                       n: int, 
                       effect_size: float,
                       n_threshold: int = 10,
                       effect_threshold: float = 0.3) -> str:
        """
        Assign confidence label based on sample size and effect magnitude.
        
        Args:
            n: Sample size
            effect_size: Magnitude of effect (e.g., delta, difference)
            n_threshold: Minimum n for high confidence
            effect_threshold: Minimum effect size for meaningful difference
            
        Returns:
            Confidence label: HIGH, MEDIUM, or LOW
        """
        abs_effect = abs(effect_size)
        
        if n >= n_threshold * 1.5 and abs_effect >= effect_threshold * 2:
            return 'HIGH'
        elif n >= n_threshold or abs_effect >= effect_threshold:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    # ==================== COMPARISON FRAMEWORK ====================
    
    def compare_periods(self, 
                       current_data: np.ndarray,
                       baseline_data: np.ndarray,
                       metric_name: str = None) -> Dict:
        """
        Compare current period vs baseline with uncertainty.
        
        Args:
            current_data: Data for current period (e.g., tournament)
            baseline_data: Data for baseline (e.g., season)
            metric_name: Name of metric
            
        Returns:
            Comparison dictionary with deltas and confidence
        """
        current_stats = self.bootstrap_ci(current_data, metric_name)
        baseline_stats = self.bootstrap_ci(baseline_data, metric_name)
        
        delta = current_stats['mean'] - baseline_stats['mean']
        
        # Calculate effect size (Cohen's d approximation)
        pooled_std = np.sqrt(
            (current_stats['std']**2 + baseline_stats['std']**2) / 2
        )
        effect_size = delta / pooled_std if pooled_std > 0 else 0
        
        return {
            'current': current_stats,
            'baseline': baseline_stats,
            'delta': delta,
            'effect_size': effect_size,
            'confidence': self.confidence_label(
                min(current_stats['n'], baseline_stats['n']),
                delta
            ),
            'interpretation': self._interpret_delta(delta, effect_size)
        }
    
    def _interpret_delta(self, delta: float, effect_size: float) -> str:
        """
        Interpret the meaning of a delta value.
        
        Args:
            delta: Change in metric
            effect_size: Standardized effect size
            
        Returns:
            String interpretation
        """
        abs_delta = abs(delta)
        abs_effect = abs(effect_size)
        
        if abs_effect >= 0.8:  # Large effect
            magnitude = "substantial"
        elif abs_effect >= 0.5:  # Medium effect
            magnitude = "moderate"
        elif abs_effect >= 0.2:  # Small effect
            magnitude = "small"
        else:
            return "No meaningful change"
        
        direction = "improvement" if delta > 0 else "decline"
        
        return f"{magnitude.capitalize()} {direction}"
    
    # ==================== STABILITY INDICATORS ====================
    
    def get_stability_badge(self, 
                           stability: str,
                           n: int = None) -> Dict:
        """
        Get display properties for stability badge.
        
        Args:
            stability: Stability category (HIGH, MEDIUM, LOW)
            n: Optional sample size
            
        Returns:
            Dictionary with badge properties
        """
        badges = {
            'HIGH': {
                'color': 'green',
                'icon': '✅',
                'label': 'High Confidence'
            },
            'MEDIUM': {
                'color': 'orange',
                'icon': '⚠️',
                'label': 'Moderate Confidence'
            },
            'LOW': {
                'color': 'red',
                'icon': '❌',
                'label': 'Low Confidence'
            }
        }
        
        result = badges.get(stability, badges['LOW'])
        
        if n is not None:
            result['tooltip'] = f"Based on {n} observations"
        
        return result
    
    # ==================== SAMPLE SIZE UTILITIES ====================
    
    def sample_size_category(self, n: int) -> str:
        """
        Categorize sample size for reporting.
        
        Args:
            n: Sample size
            
        Returns:
            Category label
        """
        if n >= 20:
            return "Good"
        elif n >= 10:
            return "Adequate"
        elif n >= 5:
            return "Limited"
        else:
            return "Very Limited"
    
    def is_reliable(self, n: int, ci_width: float = None) -> bool:
        """
        Check if data is sufficient for reliable conclusions.
        
        Args:
            n: Sample size
            ci_width: Optional CI width threshold
            
        Returns:
            Boolean indicating reliability
        """
        if n < 5:
            return False
        
        if ci_width is not None:
            stability = self._calculate_stability(n, ci_width)
            return stability != 'LOW'
        
        return n >= 10
