"""
Unit tests for the Metric Engine
Tests core metric calculations
"""

import pytest
import pandas as pd
import numpy as np
from core.metric_engine import MetricEngine
from core.field_mapper import FieldMapper


@pytest.fixture
def sample_shot_data():
    """Create sample shot-level data for testing."""
    return pd.DataFrame({
        'round_id': ['R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1'],
        'hole': [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5],
        'shot': [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3],
        'score': [4, 4, 4, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3],
        'strokes_gained': [0.1, 0.2, -0.1, 0.3, 0.1, -0.2, 0.0, 0.2, -0.1, 0.2, 0.1, 0.0, -0.1, 0.3, 0.2, -0.1],
        'shot_category': ['driving', 'approach', 'putting', 'driving', 'approach', 'putting',
                          'driving', 'approach', 'putting', 'driving', 'approach', 'short_game', 'putting',
                          'driving', 'approach', 'putting'],
        'starting_location': ['Tee', 'Fairway', 'Green', 'Tee', 'Rough', 'Green', 'Tee', 'Fairway', 'Green',
                             'Tee', 'Fairway', 'Rough', 'Green', 'Tee', 'Fairway', 'Green'],
        'ending_location': ['Fairway', 'Green', 'Green', 'Rough', 'Green', 'Green', 'Fairway', 'Green', 'Green',
                            'Fairway', 'Green', 'Green', 'Green', 'Fairway', 'Green', 'Green'],
        'starting_distance': [300, 150, 10, 280, 50, 8, 320, 180, 12, 290, 100, 30, 5, 310, 120, 10],
        'ending_distance': [250, 0, 0, 240, 0, 0, 260, 0, 0, 240, 0, 0, 0, 250, 0, 0],
        'penalty': ['No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No'],
        'distance_bucket': ['300+', '100-150', '<25', '250-300', '50-75', '<25', '300+', '150-200', '<25',
                           '250-300', '100-150', '25-50', '<25', '300+', '100-150', '<25']
    })


@pytest.fixture
def field_mapper():
    """Create a FieldMapper instance for testing."""
    return FieldMapper("config/field_mapping.yaml")


@pytest.fixture
def metric_engine(field_mapper):
    """Create a MetricEngine instance for testing."""
    return MetricEngine(field_mapper)


class TestMetricEngine:
    """Test cases for MetricEngine."""
    
    def test_calculate_hole_scores(self, metric_engine, sample_shot_data):
        """Test hole score calculation."""
        hole_stats = metric_engine.calculate_hole_scores(sample_shot_data)
        
        # Check that we have one row per hole
        assert len(hole_stats) == 5  # 5 unique holes in sample data
        
        # Check column names
        assert 'round_id' in hole_stats.columns
        assert 'hole' in hole_stats.columns
        assert 'hole_score' in hole_stats.columns
        assert 'shots_count' in hole_stats.columns
        assert 'hole_sg' in hole_stats.columns
        
        # Check hole scores
        hole1_score = hole_stats[hole_stats['hole'] == 1]['hole_score'].values[0]
        assert hole1_score == 4  # Score was 4 on hole 1
    
    def test_calculate_sg_by_category(self, metric_engine, sample_shot_data):
        """Test SG calculation by shot category."""
        sg_by_category = metric_engine.calculate_sg_by_category(sample_shot_data)
        
        # Check that all categories are present
        expected_categories = ['driving', 'approach', 'short_game', 'putting']
        for category in expected_categories:
            assert category in sg_by_category
        
        # Check that SG totals are numeric
        for category, sg in sg_by_category.items():
            assert isinstance(sg, (int, float))
    
    def test_calculate_sg_per_round(self, metric_engine, sample_shot_data):
        """Test SG per round calculation."""
        sg_metrics = metric_engine.calculate_sg_per_round(sample_shot_data)
        
        # Check required keys
        assert 'total_sg' in sg_metrics
        assert 'sg_per_round' in sg_metrics
        assert 'num_rounds' in sg_metrics
        
        # Check values
        assert sg_metrics['num_rounds'] == 1  # All shots are from round R1
        assert isinstance(sg_metrics['total_sg'], (int, float))
        assert isinstance(sg_metrics['sg_per_round'], (int, float))
    
    def test_calculate_driving_metrics(self, metric_engine, sample_shot_data):
        """Test driving-specific metrics calculation."""
        driving_metrics = metric_engine.calculate_driving_metrics(sample_shot_data)
        
        # Check required keys
        assert 'total_drives' in driving_metrics
        assert 'fairway_percentage' in driving_metrics
        assert 'sg_total' in driving_metrics
        
        # Check values
        assert driving_metrics['total_drives'] > 0
        assert 0 <= driving_metrics['fairway_percentage'] <= 100
    
    def test_calculate_approach_metrics(self, metric_engine, sample_shot_data):
        """Test approach-specific metrics calculation."""
        approach_metrics = metric_engine.calculate_approach_metrics(sample_shot_data)
        
        # Check required keys
        assert 'total_approaches' in approach_metrics
        assert 'gir_rate' in approach_metrics
        assert 'sg_total' in approach_metrics
        
        # Check values
        assert approach_metrics['total_approaches'] > 0
        assert 0 <= approach_metrics['gir_rate'] <= 100
    
    def test_calculate_short_game_metrics(self, metric_engine, sample_shot_data):
        """Test short game metrics calculation."""
        short_game_metrics = metric_engine.calculate_short_game_metrics(sample_shot_data)
        
        # Check required keys
        assert 'total_short_game' in short_game_metrics
        assert 'up_and_down_rate' in short_game_metrics
        assert 'sg_total' in short_game_metrics
    
    def test_calculate_putting_metrics(self, metric_engine, sample_shot_data):
        """Test putting metrics calculation."""
        putting_metrics = metric_engine.calculate_putting_metrics(sample_shot_data)
        
        # Check required keys
        assert 'total_putts' in putting_metrics
        assert 'one_putt_rate' in putting_metrics
        assert 'three_putt_rate' in putting_metrics
    
    def test_calculate_scoring_metrics(self, metric_engine, sample_shot_data):
        """Test scoring metrics calculation."""
        scoring_metrics = metric_engine.calculate_scoring_metrics(sample_shot_data)
        
        # Check required keys
        assert 'scoring_average' in scoring_metrics
        assert 'total_holes' in scoring_metrics
        assert 'birdies' in scoring_metrics
        assert 'pars' in scoring_metrics
        
        # Check that scores sum to total holes
        holes = scoring_metrics['total_holes']
        assert scoring_metrics['birdies'] + scoring_metrics['pars'] + scoring_metrics['bogeys'] + scoring_metrics['doubles_or_worse'] == holes
    
    def test_calculate_all_metrics(self, metric_engine, sample_shot_data):
        """Test aggregate metrics calculation."""
        all_metrics = metric_engine.calculate_all_metrics(sample_shot_data)
        
        # Check that all metric categories are present
        expected_categories = ['scoring', 'sg_total', 'sg_by_category', 'driving', 'approach', 'short_game', 'putting', 'holes']
        for category in expected_categories:
            assert category in all_metrics


class TestEdgeCases:
    """Test edge cases for MetricEngine."""
    
    def test_empty_dataframe(self, metric_engine):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame(columns=['round_id', 'hole', 'shot', 'score', 'strokes_gained', 'shot_category'])
        
        # Should not raise an error
        hole_stats = metric_engine.calculate_hole_scores(empty_df)
        assert len(hole_stats) == 0
        
        sg_by_category = metric_engine.calculate_sg_by_category(empty_df)
        assert all(v == 0 for v in sg_by_category.values())
    
    def test_single_shot(self, metric_engine):
        """Test handling of single shot."""
        single_shot = pd.DataFrame({
            'round_id': ['R1'],
            'hole': [1],
            'shot': [1],
            'score': [4],
            'strokes_gained': [0.5],
            'shot_category': ['driving'],
            'starting_location': ['Tee'],
            'ending_location': ['Fairway'],
            'starting_distance': [300],
            'ending_distance': [250],
            'penalty': ['No']
        })
        
        metrics = metric_engine.calculate_driving_metrics(single_shot)
        assert metrics['total_drives'] == 1
        assert isinstance(metrics['sg_total'], (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
