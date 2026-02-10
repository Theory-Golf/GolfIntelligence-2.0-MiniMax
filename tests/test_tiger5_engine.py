"""
Unit tests for the Tiger 5 Engine
Tests Tiger 5 analysis and Grit Score calculations
"""

import pytest
import pandas as pd
import numpy as np
from engines.tiger5 import Tiger5Engine


@pytest.fixture
def sample_hole_data():
    """Create sample hole-level data for testing."""
    return pd.DataFrame({
        'round_id': ['R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1', 'R1'],
        'hole': [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5],
        'hole_score': [4, 4, 4, 3, 3, 3, 5, 5, 5, 6, 6, 6, 6, 3, 3],
        'shots': [3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 3, 3],
        'hole_sg': [0.2, 0.2, 0.2, 0.4, 0.4, 0.4, -0.5, -0.5, -0.5, -0.8, -0.8, -0.8, -0.8, 0.4, 0.4],
        'penalties': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0],
        'score_vs_par': [1, 1, 1, 0, 0, 0, 2, 2, 2, 3, 3, 3, 3, 0, 0],
        'putts': [1, 1, 1, 2, 2, 2, 1, 1, 1, 3, 3, 3, 3, 2, 2]
    })


@pytest.fixture
def tiger5_engine():
    """Create a Tiger5Engine instance for testing."""
    return Tiger5Engine()


class TestTiger5Engine:
    """Test cases for Tiger5Engine."""
    
    def test_calculate_tiger5_fails(self, tiger5_engine, sample_hole_data):
        """Test Tiger 5 fail calculation."""
        results = tiger5_engine.calculate_tiger5_fails(sample_hole_data)
        
        # Check required keys
        assert 'total_holes' in results
        assert 'categories' in results
        assert 'grit_score' in results
        assert 'total_fails' in results
        assert 'total_attempts' in results
        
        # Check values
        assert results['total_holes'] == len(sample_hole_data)
        assert isinstance(results['grit_score'], float)
        assert 0 <= results['grit_score'] <= 100
    
    def test_grit_score_calculation(self, tiger5_engine):
        """Test Grit Score calculation."""
        # Perfect score
        perfect_results = {'total_attempts': 100, 'total_fails': 0}
        grit = tiger5_engine.calculate_grit_score(perfect_results)
        assert grit == 100.0
        
        # All fails
        all_fail_results = {'total_attempts': 100, 'total_fails': 100}
        grit = tiger5_engine.calculate_grit_score(all_fail_results)
        assert grit == 0.0
        
        # Mixed
        mixed_results = {'total_attempts': 100, 'total_fails': 20}
        grit = tiger5_engine.calculate_grit_score(mixed_results)
        assert grit == 80.0
    
    def test_grit_score_interpretation(self, tiger5_engine):
        """Test Grit Score interpretation."""
        # Excellent
        interp = tiger5_engine.get_grit_interpretation(90)
        assert interp['level'] == 'Excellent'
        assert interp['color'] == 'green'
        
        # Good
        interp = tiger5_engine.get_grit_interpretation(80)
        assert interp['level'] == 'Good'
        assert interp['color'] == 'blue'
        
        # Needs Work
        interp = tiger5_engine.get_grit_interpretation(70)
        assert interp['level'] == 'Needs Work'
        assert interp['color'] == 'orange'
        
        # Critical
        interp = tiger5_engine.get_grit_interpretation(60)
        assert interp['level'] == 'Critical'
        assert interp['color'] == 'red'
    
    def test_calculate_tiger5_trend(self, tiger5_engine, sample_hole_data):
        """Test Tiger 5 trend calculation."""
        round_ids = ['R1']
        trends = tiger5_engine.calculate_tiger5_trend(sample_hole_data, round_ids)
        
        # Check that we have results for each round
        assert len(trends) == len(round_ids)
        
        # Check that each trend has required keys
        for round_id, trend in trends.items():
            assert 'total_fails' in trend
            assert 'grit_score' in trend
            assert 'categories' in trend
    
    def test_get_tiger5_scenarios(self, tiger5_engine, sample_hole_data):
        """Test Tiger 5 fail scenario extraction."""
        scenarios = tiger5_engine.get_tiger5_scenarios(sample_hole_data)
        
        # Should return DataFrame
        assert isinstance(scenarios, pd.DataFrame)
        
        # Check column names
        expected_cols = ['round_id', 'hole', 'score', 'score_vs_par', 'putts', 'fails']
        for col in expected_cols:
            assert col in scenarios.columns
    
    def test_default_config(self, tiger5_engine):
        """Test default configuration."""
        config = tiger5_engine.config
        
        # Check that categories are defined
        assert 'categories' in config
        assert len(config['categories']) > 0
        
        # Check category structure
        for category in config['categories']:
            assert 'name' in category
            assert 'fail_condition' in category


class TestEdgeCases:
    """Test edge cases for Tiger5Engine."""
    
    def test_no_fails(self, tiger5_engine):
        """Test handling of data with no Tiger 5 fails."""
        clean_holes = pd.DataFrame({
            'round_id': ['R1', 'R1', 'R1'],
            'hole': [1, 2, 3],
            'hole_score': [3, 4, 3],
            'shots': [3, 4, 3],
            'hole_sg': [0.5, 0.3, 0.4],
            'penalties': [0, 0, 0],
            'score_vs_par': [0, 0, 0],
            'putts': [2, 2, 2]
        })
        
        results = tiger5_engine.calculate_tiger5_fails(clean_holes)
        
        # Should have Grit Score of 100
        assert results['grit_score'] == 100.0
        assert results['total_fails'] == 0
    
    def test_all_fails(self, tiger5_engine):
        """Test handling of data with all Tiger 5 fails."""
        fail_holes = pd.DataFrame({
            'round_id': ['R1', 'R1', 'R1'],
            'hole': [1, 2, 3],
            'hole_score': [6, 6, 6],
            'shots': [4, 4, 4],
            'hole_sg': [-1.5, -1.5, -1.5],
            'penalties': [0, 0, 0],
            'score_vs_par': [3, 3, 3],
            'putts': [1, 1, 1]
        })
        
        results = tiger5_engine.calculate_tiger5_fails(fail_holes)
        
        # Should have Grit Score of 0
        assert results['grit_score'] == 0.0
    
    def test_empty_dataframe(self, tiger5_engine):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame(columns=['round_id', 'hole', 'hole_score', 'shots', 'hole_sg', 'penalties', 'score_vs_par', 'putts'])
        
        results = tiger5_engine.calculate_tiger5_fails(empty_df)
        
        # Should return valid structure with 0 values
        assert results['total_holes'] == 0
        assert results['total_fails'] == 0
        assert results['total_attempts'] == 0
    
    def test_calculate_root_causes(self, tiger5_engine, sample_hole_data):
        """Test root cause analysis."""
        # Add shot data for root cause analysis
        shot_data = pd.DataFrame({
            'round_id': ['R1'] * 15,
            'hole': [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5],
            'shot': [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 4, 1, 2],
            'shot_category': ['driving', 'approach', 'putting'] * 5,
            'starting_location': ['Tee', 'Fairway', 'Green'] * 5,
            'ending_location': ['Fairway', 'Green', 'Green'] * 5,
            'penalty': ['No'] * 15,
            'strokes_gained': [0.1, 0.2, -0.1] * 5
        })
        
        causes = tiger5_engine.calculate_root_causes(sample_hole_data, shot_data)
        
        # Should return dictionary with driving and putting analysis
        assert 'driving' in causes
        assert 'putting' in causes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
