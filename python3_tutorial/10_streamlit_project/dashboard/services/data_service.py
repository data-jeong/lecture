"""Data service for managing dashboard data"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import os


class DataService:
    """Service for handling data operations"""
    
    def __init__(self, data_dir: str = "dashboard/data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def load_csv(self, filename: str) -> pd.DataFrame:
        """Load CSV file"""
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            return pd.read_csv(filepath)
        return pd.DataFrame()
    
    def save_csv(self, data: pd.DataFrame, filename: str) -> bool:
        """Save DataFrame to CSV"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            data.to_csv(filepath, index=False)
            return True
        except Exception as e:
            print(f"Error saving CSV: {e}")
            return False
    
    def load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON file"""
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_json(self, data: Dict[str, Any], filename: str) -> bool:
        """Save data to JSON"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving JSON: {e}")
            return False
    
    def generate_sample_data(self, rows: int = 100) -> pd.DataFrame:
        """Generate sample data for testing"""
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=rows),
            periods=rows,
            freq='D'
        )
        
        data = {
            'date': dates,
            'users': np.random.randint(50, 200, rows),
            'sessions': np.random.randint(100, 500, rows),
            'pageviews': np.random.randint(500, 2000, rows),
            'bounce_rate': np.random.uniform(0.2, 0.8, rows),
            'avg_duration': np.random.uniform(60, 300, rows),
            'conversions': np.random.randint(5, 50, rows),
            'revenue': np.random.uniform(1000, 10000, rows)
        }
        
        return pd.DataFrame(data)
    
    def get_summary_stats(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics from DataFrame"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        stats = {}
        for col in numeric_cols:
            stats[col] = {
                'mean': float(data[col].mean()),
                'median': float(data[col].median()),
                'std': float(data[col].std()),
                'min': float(data[col].min()),
                'max': float(data[col].max()),
                'count': int(data[col].count())
            }
        
        return stats
    
    def filter_data(self, data: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to DataFrame"""
        filtered = data.copy()
        
        for column, value in filters.items():
            if column not in filtered.columns:
                continue
            
            if isinstance(value, list):
                filtered = filtered[filtered[column].isin(value)]
            elif isinstance(value, dict):
                if 'min' in value:
                    filtered = filtered[filtered[column] >= value['min']]
                if 'max' in value:
                    filtered = filtered[filtered[column] <= value['max']]
            else:
                filtered = filtered[filtered[column] == value]
        
        return filtered
    
    def aggregate_data(self, data: pd.DataFrame, group_by: str, 
                      agg_func: str = 'mean') -> pd.DataFrame:
        """Aggregate data by specified column"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if agg_func == 'mean':
            return data.groupby(group_by)[numeric_cols].mean().reset_index()
        elif agg_func == 'sum':
            return data.groupby(group_by)[numeric_cols].sum().reset_index()
        elif agg_func == 'count':
            return data.groupby(group_by).size().reset_index(name='count')
        else:
            return data.groupby(group_by)[numeric_cols].agg(agg_func).reset_index()
    
    def get_time_series_data(self, start_date: datetime, end_date: datetime, 
                            freq: str = 'D') -> pd.DataFrame:
        """Generate time series data"""
        dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        
        data = {
            'date': dates,
            'value': np.cumsum(np.random.randn(len(dates))) + 100,
            'volume': np.random.randint(1000, 5000, len(dates))
        }
        
        return pd.DataFrame(data)
    
    def calculate_growth_rate(self, data: pd.DataFrame, value_col: str, 
                             period: int = 1) -> float:
        """Calculate growth rate over specified period"""
        if len(data) < period + 1:
            return 0.0
        
        current = data[value_col].iloc[-1]
        previous = data[value_col].iloc[-(period + 1)]
        
        if previous == 0:
            return 0.0
        
        return ((current - previous) / previous) * 100
    
    def export_to_excel(self, dataframes: Dict[str, pd.DataFrame], 
                       filename: str) -> bool:
        """Export multiple DataFrames to Excel"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for sheet_name, df in dataframes.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return True
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False