"""
Coach Corner Engine
Mental metrics and coaching insights
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class CoachCornerEngine:
    """
    Provides mental metrics and coaching insights.
    
    Calculates:
    - Bounce back rate
    - Drop off rate
    - Gas pedal rate
    - Bogey train rate
    - Pressure performance
    - Strengths/weaknesses identification
    """
    
    def __init__(self):
        """Initialize coach corner engine."""
        pass
    
    # ==================== MENTAL METRICS ====================
    
    def calculate_bounce_back_rate(self, df: pd.DataFrame) -> Dict:
        """
        Calculate bounce back rate (par or better after bogey or worse).
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with bounce back metrics
        """
        # Get hole scores
        hole_scores = df.groupby(['round_id', 'hole'])['score'].max().reset_index()
        hole_scores = hole_scores.sort_values(['round_id', 'hole'])
        
        # Identify bogey or worse holes
        hole_scores['bogey_plus'] = hole_scores['score'] > 3  # Assuming par 3
        
        # Check next hole
        hole_scores['next_bogey_plus'] = hole_scores.groupby('round_id')['bogey_plus'].shift(-1)
        
        # Calculate bounce backs
        opportunities = hole_scores[hole_scores['bogey_plus']].shape[0]
        successes = hole_scores[
            (hole_scores['bogey_plus']) & (hole_scores['next_bogey_plus'] == False)
        ].shape[0]
        
        return {
            'opportunities': opportunities,
            'successes': successes,
            'bounce_back_rate': (successes / opportunities * 100) if opportunities > 0 else 0
        }
    
    def calculate_gas_pedal_rate(self, df: pd.DataFrame) -> Dict:
        """
        Calculate gas pedal rate (birdie or better after birdie).
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with gas pedal metrics
        """
        hole_scores = df.groupby(['round_id', 'hole'])['score'].max().reset_index()
        hole_scores = hole_scores.sort_values(['round_id', 'hole'])
        
        # Identify birdie or better holes
        hole_scores['birdie_plus'] = hole_scores['score'] <= 2
        
        # Check next hole
        hole_scores['next_birdie_plus'] = hole_scores.groupby('round_id')['birdie_plus'].shift(-1)
        
        # Calculate gas pedals
        opportunities = hole_scores[hole_scores['birdie_plus']].shape[0]
        successes = hole_scores[
            (hole_scores['birdie_plus']) & (hole_scores['next_birdie_plus'] == True)
        ].shape[0]
        
        return {
            'opportunities': opportunities,
            'successes': successes,
            'gas_pedal_rate': (successes / opportunities * 100) if opportunities > 0 else 0
        }
    
    def calculate_bogey_train_rate(self, df: pd.DataFrame) -> Dict:
        """
        Calculate bogey train rate (consecutive bogey+ holes).
        
        Args:
            df: Shot-level DataFrame
            
        Returns:
            Dictionary with bogey train metrics
        """
        hole_scores = df.groupby(['round_id', 'hole'])['score'].max().reset_index()
        
        # Identify bogey+ holes
        hole_scores['bogey_plus'] = hole_scores['score'] > 3
        
        # Count consecutive bogey+ sequences
        round_ids = hole_scores['round_id'].unique()
        
        train_count = 0
        bogey_plus_holes = hole_scores[hole_scores['bogey_plus']].shape[0]
        
        for rid in round_ids:
            round_holes = hole_scores[hole_scores['round_id'] == rid]
            
            # Count consecutive bogey+ within this round
            consecutive = 0
            for _, row in round_holes.iterrows():
                if row['bogey_plus']:
                    consecutive += 1
                    if consecutive >= 2:
                        train_count += 1
                else:
                    consecutive = 0
        
        return {
            'bogey_plus_holes': bogey_plus_holes,
            'trains': train_count,
            'bogey_train_rate': (train_count / bogey_plus_holes * 100) if bogey_plus_holes > 0 else 0
        }
    
    # ==================== STRENGTHS & WEAKNESSES ====================
    
    def identify_strengths_weaknesses(self, 
                                   current_metrics: Dict,
                                   baseline_metrics: Dict) -> Dict:
        """
        Identify strengths and weaknesses based on deltas.
        
        Args:
            current_metrics: Current period metrics
            baseline_metrics: Baseline period metrics
            
        Returns:
            Dictionary with strengths and weaknesses
        """
        strengths = []
        weaknesses = []
        
        for metric, current_value in current_metrics.items():
            if metric in baseline_metrics:
                delta = current_value - baseline_metrics[metric]
                
                # Define thresholds for meaningful difference
                if delta > 0.1:  # Positive change
                    strengths.append({
                        'metric': metric,
                        'delta': delta,
                        'current': current_value,
                        'baseline': baseline_metrics[metric]
                    })
                elif delta < -0.1:  # Negative change
                    weaknesses.append({
                        'metric': metric,
                        'delta': delta,
                        'current': current_value,
                        'baseline': baseline_metrics[metric]
                    })
        
        # Sort by magnitude
        strengths.sort(key=lambda x: x['delta'], reverse=True)
        weaknesses.sort(key=lambda x: x['delta'])
        
        return {
            'strengths': strengths[:5],  # Top 5 strengths
            'weaknesses': weaknesses[:5]  # Top 5 weaknesses
        }
    
    def rank_strengths_weaknesses(self, 
                               current_metrics: Dict,
                               baseline_metrics: Dict) -> Dict:
        """
        Rank strengths and weaknesses with confidence levels.
        
        Args:
            current_metrics: Current period metrics
            baseline_metrics: Baseline period metrics
            
        Returns:
            Ranked list with confidence labels
        """
        ranked = self.identify_strengths_weaknesses(current_metrics, baseline_metrics)
        
        # Add confidence labels
        for category in ['strengths', 'weaknesses']:
            for item in ranked[category]:
                item['confidence'] = self._confidence_label(item)
        
        return ranked
    
    def _confidence_label(self, item: Dict) -> str:
        """
        Generate confidence label for a metric.
        
        Args:
            item: Metric item with delta
            
        Returns:
            Confidence label: HIGH, MEDIUM, or LOW
        """
        magnitude = abs(item['delta'])
        
        if magnitude >= 0.5:
            return 'HIGH'
        elif magnitude >= 0.2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    # ==================== PERFORMANCE DRIVERS ====================
    
    def identify_performance_drivers(self,
                                   round_data: Dict,
                                   metric: str = 'score') -> Dict:
        """
        Identify what drives performance changes.
        
        Args:
            round_data: Dictionary of round_id -> metrics
            metric: Metric to analyze
            
        Returns:
            Dictionary with driver analysis
        """
        if len(round_data) < 2:
            return {'message': 'Need at least 2 rounds for analysis'}
        
        # Sort rounds by the metric
        sorted_rounds = sorted(round_data.items(), key=lambda x: x[1].get(metric, 0))
        
        best_rounds = sorted_rounds[-3:]  # Best 3
        worst_rounds = sorted_rounds[:3]  # Worst 3
        
        # Compare best vs worst
        differences = {}
        for key in ['driving', 'approach', 'short_game', 'putting']:
            best_avg = np.mean([r[1].get(f'{key}_sg', 0) for r in best_rounds])
            worst_avg = np.mean([r[1].get(f'{key}_sg', 0) for r in worst_rounds])
            differences[key] = best_avg - worst_avg
        
        # Rank by difference
        ranked = sorted(differences.items(), key=lambda x: abs(x[1]), reverse=True)
        
        return {
            'best_rounds': [r[0] for r in best_rounds],
            'worst_rounds': [r[0] for r in worst_rounds],
            'driver_differences': dict(ranked),
            'primary_driver': ranked[0][0] if ranked else None,
            'impact': ranked[0][1] if ranked else 0
        }
    
    # ==================== RECOMMENDATIONS ====================
    
    def generate_recommendations(self, 
                              analysis: Dict,
                              priorities: List[str] = None) -> List[Dict]:
        """
        Generate actionable recommendations.
        
        Args:
            analysis: Analysis results from various engines
            priorities: Priority areas
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Based on weaknesses
        if 'weaknesses' in analysis:
            for weakness in analysis['weaknesses'][:3]:
                recommendations.append({
                    'type': 'IMPROVE',
                    'area': weakness['metric'],
                    'action': f"Focus practice on {weakness['metric']}",
                    'evidence': f"Current: {weakness['current']:.2f}, Baseline: {weakness['baseline']:.2f}",
                    'confidence': weakness.get('confidence', 'MEDIUM')
                })
        
        # Based on primary driver
        if 'primary_driver' in analysis and analysis['primary_driver']:
            recommendations.append({
                'type': 'PRIORITY',
                'area': analysis['primary_driver'],
                'action': f"{analysis['primary_driver']} is your primary performance driver",
                'evidence': f"Impact: {analysis['impact']:.2f} strokes per round difference",
                'confidence': 'HIGH'
            })
        
        return recommendations[:5]  # Top 5 recommendations
