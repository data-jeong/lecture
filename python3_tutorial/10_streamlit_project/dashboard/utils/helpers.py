"""Helper utilities for the dashboard"""

from typing import Any, List, Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def format_number(value: float, decimals: int = 0) -> str:
    """Format number with thousands separator"""
    if pd.isna(value):
        return "N/A"
    
    if decimals == 0:
        return f"{int(value):,}"
    else:
        return f"{value:,.{decimals}f}"


def format_currency(value: float, currency: str = "USD", decimals: int = 2) -> str:
    """Format value as currency"""
    if pd.isna(value):
        return "N/A"
    
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "KRW": "₩"
    }
    
    symbol = symbols.get(currency, currency)
    formatted = format_number(value, decimals)
    
    if currency in ["USD", "GBP", "EUR"]:
        return f"{symbol}{formatted}"
    else:
        return f"{formatted}{symbol}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format value as percentage"""
    if pd.isna(value):
        return "N/A"
    
    return f"{value:.{decimals}f}%"


def format_bytes(size: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def get_color_scheme(theme: str = "default") -> Dict[str, str]:
    """Get color scheme for charts"""
    schemes = {
        "default": {
            "primary": "#1f77b4",
            "secondary": "#ff7f0e",
            "success": "#2ca02c",
            "danger": "#d62728",
            "warning": "#ff9800",
            "info": "#17a2b8",
            "light": "#f8f9fa",
            "dark": "#343a40"
        },
        "dark": {
            "primary": "#4CAF50",
            "secondary": "#FFC107",
            "success": "#8BC34A",
            "danger": "#F44336",
            "warning": "#FF9800",
            "info": "#00BCD4",
            "light": "#212121",
            "dark": "#FAFAFA"
        },
        "pastel": {
            "primary": "#FFB6C1",
            "secondary": "#FFE4B5",
            "success": "#98FB98",
            "danger": "#FFA07A",
            "warning": "#F0E68C",
            "info": "#B0E0E6",
            "light": "#FFFAFA",
            "dark": "#696969"
        }
    }
    
    return schemes.get(theme, schemes["default"])


def calculate_trend(data: List[float]) -> str:
    """Calculate trend direction"""
    if len(data) < 2:
        return "stable"
    
    recent = data[-5:] if len(data) >= 5 else data
    if recent[-1] > recent[0]:
        return "up"
    elif recent[-1] < recent[0]:
        return "down"
    else:
        return "stable"


def get_date_range(period: str) -> tuple:
    """Get date range based on period"""
    end_date = datetime.now()
    
    periods = {
        "today": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": timedelta(days=30),
        "quarter": timedelta(days=90),
        "year": timedelta(days=365)
    }
    
    delta = periods.get(period, timedelta(days=30))
    start_date = end_date - delta
    
    return start_date, end_date


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime"""
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def generate_mock_data(data_type: str, rows: int = 100) -> pd.DataFrame:
    """Generate mock data for testing"""
    np.random.seed(42)
    
    if data_type == "sales":
        dates = pd.date_range(start="2024-01-01", periods=rows, freq="D")
        return pd.DataFrame({
            "date": dates,
            "sales": np.random.randint(1000, 5000, rows),
            "orders": np.random.randint(50, 200, rows),
            "customers": np.random.randint(30, 150, rows),
            "revenue": np.random.uniform(5000, 20000, rows)
        })
    
    elif data_type == "users":
        return pd.DataFrame({
            "user_id": range(1, rows + 1),
            "username": [f"user_{i}" for i in range(1, rows + 1)],
            "email": [f"user_{i}@example.com" for i in range(1, rows + 1)],
            "signup_date": pd.date_range(start="2023-01-01", periods=rows, freq="D"),
            "last_active": pd.date_range(start="2024-01-01", periods=rows, freq="H"),
            "status": np.random.choice(["active", "inactive", "pending"], rows)
        })
    
    elif data_type == "metrics":
        timestamps = pd.date_range(start="2024-01-01", periods=rows, freq="H")
        return pd.DataFrame({
            "timestamp": timestamps,
            "cpu_usage": np.random.uniform(20, 80, rows),
            "memory_usage": np.random.uniform(30, 70, rows),
            "disk_usage": np.random.uniform(40, 60, rows),
            "network_in": np.random.uniform(100, 1000, rows),
            "network_out": np.random.uniform(100, 1000, rows)
        })
    
    else:
        return pd.DataFrame({
            "id": range(1, rows + 1),
            "value": np.random.randn(rows)
        })


def sanitize_html(text: str) -> str:
    """Sanitize HTML content"""
    import html
    return html.escape(text)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix