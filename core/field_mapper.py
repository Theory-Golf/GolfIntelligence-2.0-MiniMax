"""
Field Mapper Module
Handles mapping between user field names and internal standard field names
"""

import yaml
from pathlib import Path
from typing import Dict, Optional, Any


class FieldMapper:
    """
    Config-driven field mapping system.
    
    Maps user's field names to internal standard names and vice versa.
    Allows easy customization of field names without changing core code.
    """
    
    def __init__(self, config_path: str = "config/field_mapping.yaml"):
        """
        Initialize field mapper with configuration.
        
        Args:
            config_path: Path to field mapping YAML file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """Load field mapping configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """Return default configuration."""
        return {
            'shot_level': {
                'player': 'Player',
                'round_id': 'Round ID',
                'date': 'Date',
                'course': 'Course',
                'shot': 'Shot',
                'hole': 'Hole',
                'score': 'Score',
                'starting_distance': 'Starting Distance',
                'starting_location': 'Starting Location',
                'ending_distance': 'Ending Distance',
                'ending_location': 'Ending Location',
                'penalty': 'Penalty',
                'starting_sg': 'Starting SG',
                'ending_sg': 'Ending SG',
                'strokes_gained': 'Strokes Gained'
            },
            'locations': {
                'tee': ['Tee'],
                'fairway': ['Fairway'],
                'rough': ['Rough'],
                'sand': ['Sand'],
                'recovery': ['Recovery'],
                'green': ['Green', 'Putt']
            }
        }
    
    def to_internal(self, df_columns: list) -> Dict[str, str]:
        """
        Create mapping from user's column names to internal standard names.
        
        Args:
            df_columns: List of column names from DataFrame
            
        Returns:
            Dictionary mapping user_name -> internal_name
        """
        mapping = {}
        for section in ['shot_level', 'round_level']:
            if section in self.config:
                for internal_name, user_name in self.config[section].items():
                    if user_name in df_columns:
                        mapping[user_name] = internal_name
        return mapping
    
    def to_user(self, internal_name: str) -> str:
        """
        Convert internal field name to user's field name.
        
        Args:
            internal_name: Internal standard field name
            
        Returns:
            User's field name
        """
        for section in ['shot_level', 'round_level']:
            if section in self.config:
                if internal_name in self.config[section]:
                    return self.config[section][internal_name]
        return internal_name
    
    def get_user_name(self, internal_name: str, default: str = None) -> str:
        """
        Get user's field name for an internal field.
        
        Args:
            internal_name: Internal field name
            default: Default value if not found
            
        Returns:
            User's field name or default
        """
        for section in ['shot_level', 'round_level']:
            if section in self.config:
                if internal_name in self.config[section]:
                    return self.config[section][internal_name]
        return default or internal_name
    
    def get_internal_name(self, user_name: str, default: str = None) -> str:
        """
        Get internal field name from user's field name.
        
        Args:
            user_name: User's field name
            default: Default value if not found
            
        Returns:
            Internal field name or default
        """
        for section in ['shot_level', 'round_level']:
            if section in self.config:
                for internal, user in self.config[section].items():
                    if user == user_name:
                        return internal
        return default or user_name
    
    def get_location_type(self, location_value: str) -> str:
        """
        Normalize location value to standard type.
        
        Args:
            location_value: Raw location value from data
            
        Returns:
            Standardized location type (tee, fairway, rough, sand, recovery, green)
        """
        if not location_value:
            return 'unknown'
        
        location_value = str(location_value).strip().lower()
        
        locations = self.config.get('locations', {})
        for loc_type, aliases in locations.items():
            if location_value in [a.lower() for a in aliases]:
                return loc_type
        
        # Try to match partial names
        for loc_type, aliases in locations.items():
            for alias in aliases:
                if alias.lower() in location_value or location_value in alias.lower():
                    return loc_type
        
        return 'unknown'
    
    def is_drive(self, shot_data: dict) -> bool:
        """
        Determine if a shot is a drive (tee shot on par 4 or 5).
        
        Args:
            shot_data: Shot data dictionary
            
        Returns:
            True if shot is a drive
        """
        shot = shot_data.get('shot', 0)
        starting_location = self.get_location_type(shot_data.get('starting_location', ''))
        
        # Drive = Shot 1 from Tee on par 4 or par 5
        return (shot == 1 and 
                starting_location == 'tee')
    
    def is_approach(self, shot_data: dict) -> bool:
        """
        Determine if a shot is an approach shot (>25 yards to green).
        
        Args:
            shot_data: Shot data dictionary
            
        Returns:
            True if shot is an approach
        """
        shot = shot_data.get('shot', 0)
        starting_distance = shot_data.get('starting_distance', 0)
        starting_location = self.get_location_type(shot_data.get('starting_location', ''))
        
        # Approach = Not from tee, >25 yards
        return (shot > 1 and 
                starting_location != 'tee' and 
                starting_distance > 25)
    
    def is_short_game(self, shot_data: dict) -> bool:
        """
        Determine if a shot is a short game shot (≤25 yards).
        
        Args:
            shot_data: Shot data dictionary
            
        Returns:
            True if shot is short game
        """
        starting_distance = shot_data.get('starting_distance', 100)
        starting_location = self.get_location_type(shot_data.get('starting_location', ''))
        
        # Short game = ≤25 yards, not from tee, not putting
        return (starting_distance <= 25 and 
                starting_location != 'tee')
    
    def is_putting(self, shot_data: dict) -> bool:
        """
        Determine if a shot is a putt.
        
        Args:
            shot_data: Shot data dictionary
            
        Returns:
            True if shot is a putt
        """
        starting_location = self.get_location_type(shot_data.get('starting_location', ''))
        return starting_location == 'green'
    
    def get_shot_category(self, shot_data: dict) -> str:
        """
        Get the category of a shot.
        
        Args:
            shot_data: Shot data dictionary
            
        Returns:
            Shot category: drive, approach, short_game, putting, or other
        """
        if self.is_drive(shot_data):
            return 'driving'
        elif self.is_putting(shot_data):
            return 'putting'
        elif self.is_short_game(shot_data):
            return 'short_game'
        elif self.is_approach(shot_data):
            return 'approach'
        else:
            return 'other'
