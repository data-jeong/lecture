"""
Data model modules
"""

from .location import Location
from .weather import Weather, WeatherData
from .forecast import Forecast, ForecastData

__all__ = [
    "Location",
    "Weather",
    "WeatherData",
    "Forecast",
    "ForecastData",
]