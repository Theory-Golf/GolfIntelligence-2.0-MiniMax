"""
Data Ingestion Module
Handles loading golf data from various sources (CSV, Google Sheets, etc.)
"""

import pandas as pd
import yaml
from pathlib import Path
from datetime import datetime
import streamlit as st


class DataIngestion:
    """
    Handles data loading and preprocessing for golf analytics.
    
    Supports:
    - CSV files
    - Google Sheets (future)
    - Parquet files (cached)
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize data ingestion with configuration.
        
        Args:
            config_path: Path to field mapping YAML file
        """
        self.config_path = config_path or "config/field_mapping.yaml"
        self.field_map = self._load_field_mapping()
        self.data = None
        
    def _load_field_mapping(self) -> dict:
        """Load field mapping configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Return default mapping if file not found
            return self._get_default_mapping()
    
    def _get_default_mapping(self) -> dict:
        """Return default field mapping based on user's data structure."""
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
            }
        }
    
    def load_csv(self, filepath: str) -> pd.DataFrame:
        """
        Load golf data from CSV file.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            DataFrame with standardized column names
        """
        try:
            df = pd.read_csv(filepath)
            df = self._standardize_columns(df)
            df = self._preprocess_data(df)
            self.data = df
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            raise
    
    def load_google_sheet(self, spreadsheet_id: str, sheet_name: str = None):
        """
        Load data from Google Sheets.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            sheet_name: Name of sheet tab (optional, loads first sheet if not provided)
            
        Returns:
            DataFrame with standardized column names
        """
        try:
            # Construct the Google Sheets URL
            if sheet_name:
                url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
            else:
                url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv"
            
            # Load the data directly as CSV
            df = pd.read_csv(url)
            
            # Standardize and preprocess
            df = self._standardize_columns(df)
            df = self._preprocess_data(df)
            
            self.data = df
            return df
            
        except Exception as e:
            st.error(f"Error loading Google Sheet: {e}")
            raise
    
    def get_sheet_names(self, spreadsheet_id: str):
        """
        Get list of sheet names from a Google Sheets spreadsheet.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            
        Returns:
            List of sheet names
        """
        try:
            # Use gsheetsdb or similar approach
            # For now, return common defaults
            return ["Sheet1", "Data", "Shot Data"]
        except Exception:
            return ["Sheet1"]
    
    def load_sample_data(self) -> pd.DataFrame:
        """Load sample data for testing."""
        sample_path = Path("data/sample_data.csv")
        if sample_path.exists():
            return self.load_csv(sample_path)
        else:
            # Create sample data from user's provided data
            return self._create_sample_data()
    
    def _create_sample_data(self) -> pd.DataFrame:
        """Create sample data based on user's provided data structure."""
        data = """Player,Round ID,Date,Course,Weather Difficulty,Course Difficulty,Tournament,Benchmark,Shot,Hole,Score,Starting Distance,Starting Location,Ending Distance,Ending Location,Penalty,Starting SG,Ending SG,Strokes Gained
Adam,R1769787317558,2026-01-30,Gaston,Cold,Standard,Practice,Scratch Golfer,1,1,1,500,Tee,230,Fairway,No,4.71,3.59,0.12
Adam,R1769787317558,2026-01-30,Gaston,Cold,Standard,Practice,Scratch Golfer,2,1,2,230,Fairway,50,Fairway,No,3.59,2.7,-0.11
Adam,R1769787317558,2026-01-30,Gaston,Cold,Standard,Practice,Scratch Golfer,3,1,3,50,Fairway,8,Green,No,2.7,1.5,0.2
Adam,R1769787317558,2026-01-30,Gaston,Cold,Standard,Practice,Scratch Golfer,4,1,4,8,Green,0,Green,No,1.5,0,0.5
Adam,R1769787317558,2026-01-30,Gaston,Cold,Standard,Practice,Scratch Golfer,1,2,5,180,Tee,35,Green,No,3.16,2.04,0.12
Adam,R1769787317558,2026-01-30,Gaston,Cold,Standard,Practice,Scratch Golfer,2,2,6,35,Green,2,Green,No,2.04,1.04,0
Adam,R1769787317558,2026-01-30,Gaston,Cold,Standard,Practice,Scratch Golfer,3,2,7,2,Green,0,Green,No,1,0,0
Adam,R1769787317558,2026-01-30,Gaston,Cold,Standard,Practice,Scratch Golfer,1,3,9,440,Tee,145,Rough,Yes,4.33,3.33,-1
Adam,R1769787317558,2026-01-30,Gaston,Cold,Standard,Practice,Scratch Golfer,2,3,10,145,Rough,23,Rough,No,3.33,2.64,-0.31
Adam,R1769787317558,2026-01-30,Gaston,Cold,Standard,Practice,Scratch Golfer,3,3,11,23,Rough,4,Green,No,2.64,1.14,0.5
Adam,R1769787317558,2026-01-30,Gaston,Cold,Standard,Practice,Scratch Golfer,4,3,12,4,Green,0,Green,No,1.02,0,0.02
Adam,R1769787317558,2026-01-30,Gaston,Cold,Standard,Practice,Scratch Golfer,1,4,13,330,Tee,150,Fairway,No,4.03,3.08,-0.05
Adam,R1769787317558,2026-01-30,Gaston,Cold,Standard,Practice,Scratch Golfer,2,4,14,150,Fairway,43,Green,No,3.08,2.1,-0.02
Adam,R1769787317558,2026-01-30,Gaston,Cold,Standard,Practice,Scratch Golfer,3,4,15,43,Green,3,Green,No,2.1,1.05,0.05"""
        
        from io import StringIO
        df = pd.read_csv(StringIO(data))
        return self._standardize_columns(df)
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names to internal format.
        
        Args:
            df: Raw DataFrame with user's column names
            
        Returns:
            DataFrame with standardized column names
        """
        field_map = self.field_map.get('shot_level', {})
        rename_map = {v: k for k, v in field_map.items()}
        
        # Rename columns that exist in the dataframe
        rename_map = {k: v for k, v in rename_map.items() if k in df.columns}
        df = df.rename(columns=rename_map)
        
        return df
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess loaded data.
        
        Args:
            df: DataFrame with standardized columns
            
        Returns:
            Preprocessed DataFrame
        """
        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Ensure numeric columns
        numeric_cols = ['shot', 'hole', 'score', 'starting_distance', 'ending_distance',
                       'starting_sg', 'ending_sg', 'strokes_gained']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Standardize location values
        if 'starting_location' in df.columns:
            df['starting_location'] = df['starting_location'].str.strip()
        if 'ending_location' in df.columns:
            df['ending_location'] = df['ending_location'].str.strip()
        
        # Standardize penalty values
        if 'penalty' in df.columns:
            df['penalty'] = df['penalty'].str.strip().str.capitalize()
        
        return df
    
    def get_unique_values(self, column: str) -> list:
        """Get unique values from a column."""
        if self.data is None:
            return []
        if column not in self.data.columns:
            return []
        return sorted(self.data[column].dropna().unique().tolist())
    
    def get_players(self) -> list:
        """Get list of unique players."""
        return self.get_unique_values('player')
    
    def get_courses(self) -> list:
        """Get list of unique courses."""
        return self.get_unique_values('course')
    
    def get_tournaments(self) -> list:
        """Get list of unique tournaments."""
        return self.get_unique_values('tournament')
