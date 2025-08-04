from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from functools import lru_cache

from ..api.weather_api import WeatherAPI
from ..models.weather import Weather, WeatherData
from ..models.forecast import Forecast, ForecastData
from ..models.location import Location
from ..utils.config import Config
from ..utils.validators import validate_city_name, validate_coordinates

logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self, api_key: Optional[str] = None):
        self.config = Config()
        self.api = WeatherAPI(api_key or self.config.api_key)
        self._cache: Dict[str, Any] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        
    def get_current_weather(self, city: str) -> Weather:
        validate_city_name(city)
        
        cache_key = f"current_{city}"
        if self._is_cache_valid(cache_key):
            logger.info(f"Returning cached weather for {city}")
            return self._cache[cache_key]
            
        try:
            data = self.api.get_current_weather(city)
            weather = self._parse_current_weather(data)
            self._update_cache(cache_key, weather)
            return weather
        except Exception as e:
            logger.error(f"Failed to get weather for {city}: {e}")
            raise
            
    def get_forecast(self, city: str, days: int = 5) -> Forecast:
        validate_city_name(city)
        
        cache_key = f"forecast_{city}_{days}"
        if self._is_cache_valid(cache_key):
            logger.info(f"Returning cached forecast for {city}")
            return self._cache[cache_key]
            
        try:
            data = self.api.get_forecast(city, days)
            forecast = self._parse_forecast(data)
            self._update_cache(cache_key, forecast)
            return forecast
        except Exception as e:
            logger.error(f"Failed to get forecast for {city}: {e}")
            raise
            
    def get_weather_by_coordinates(self, lat: float, lon: float) -> Weather:
        validate_coordinates(lat, lon)
        
        cache_key = f"coord_{lat}_{lon}"
        if self._is_cache_valid(cache_key):
            logger.info(f"Returning cached weather for coordinates {lat}, {lon}")
            return self._cache[cache_key]
            
        try:
            data = self.api.get_weather_by_coordinates(lat, lon)
            weather = self._parse_current_weather(data)
            self._update_cache(cache_key, weather)
            return weather
        except Exception as e:
            logger.error(f"Failed to get weather for coordinates {lat}, {lon}: {e}")
            raise
            
    def get_hourly_forecast(self, city: str, hours: int = 24) -> List[WeatherData]:
        validate_city_name(city)
        
        cache_key = f"hourly_{city}_{hours}"
        if self._is_cache_valid(cache_key):
            logger.info(f"Returning cached hourly forecast for {city}")
            return self._cache[cache_key]
            
        try:
            data = self.api.get_hourly_forecast(city)
            hourly_data = self._parse_hourly_forecast(data, hours)
            self._update_cache(cache_key, hourly_data)
            return hourly_data
        except Exception as e:
            logger.error(f"Failed to get hourly forecast for {city}: {e}")
            raise
            
    def search_cities(self, query: str, limit: int = 5) -> List[Location]:
        try:
            data = self.api.search_cities(query, limit)
            return self._parse_locations(data)
        except Exception as e:
            logger.error(f"Failed to search cities with query '{query}': {e}")
            raise
            
    def get_air_quality(self, lat: float, lon: float) -> Dict[str, Any]:
        validate_coordinates(lat, lon)
        
        cache_key = f"air_{lat}_{lon}"
        if self._is_cache_valid(cache_key):
            logger.info(f"Returning cached air quality for {lat}, {lon}")
            return self._cache[cache_key]
            
        try:
            data = self.api.get_air_quality(lat, lon)
            air_quality = self._parse_air_quality(data)
            self._update_cache(cache_key, air_quality)
            return air_quality
        except Exception as e:
            logger.error(f"Failed to get air quality for {lat}, {lon}: {e}")
            raise
            
    def get_uv_index(self, lat: float, lon: float) -> float:
        validate_coordinates(lat, lon)
        
        try:
            data = self.api.get_uv_index(lat, lon)
            return data.get('value', 0.0)
        except Exception as e:
            logger.error(f"Failed to get UV index for {lat}, {lon}: {e}")
            raise
            
    def _parse_current_weather(self, data: dict) -> Weather:
        weather_data = WeatherData(
            temperature=data['main']['temp'],
            feels_like=data['main']['feels_like'],
            humidity=data['main']['humidity'],
            pressure=data['main']['pressure'],
            wind_speed=data['wind']['speed'],
            wind_direction=data['wind'].get('deg', 0),
            description=data['weather'][0]['description'],
            icon=data['weather'][0]['icon'],
            clouds=data['clouds']['all'],
            visibility=data.get('visibility', 10000) / 1000,
            timestamp=datetime.fromtimestamp(data['dt'])
        )
        
        location = Location(
            name=data['name'],
            country=data['sys']['country'],
            latitude=data['coord']['lat'],
            longitude=data['coord']['lon'],
            timezone=data.get('timezone', 0)
        )
        
        return Weather(
            location=location,
            current=weather_data,
            sunrise=datetime.fromtimestamp(data['sys']['sunrise']),
            sunset=datetime.fromtimestamp(data['sys']['sunset'])
        )
        
    def _parse_forecast(self, data: dict) -> Forecast:
        location = Location(
            name=data['city']['name'],
            country=data['city']['country'],
            latitude=data['city']['coord']['lat'],
            longitude=data['city']['coord']['lon'],
            timezone=data['city'].get('timezone', 0)
        )
        
        daily_forecasts = []
        grouped_by_day = {}
        
        for item in data['list']:
            date = datetime.fromtimestamp(item['dt']).date()
            if date not in grouped_by_day:
                grouped_by_day[date] = []
            grouped_by_day[date].append(item)
            
        for date, items in grouped_by_day.items():
            temps = [item['main']['temp'] for item in items]
            forecast_data = ForecastData(
                date=date,
                temperature_min=min(temps),
                temperature_max=max(temps),
                temperature_avg=sum(temps) / len(temps),
                humidity=sum(item['main']['humidity'] for item in items) / len(items),
                pressure=sum(item['main']['pressure'] for item in items) / len(items),
                wind_speed=sum(item['wind']['speed'] for item in items) / len(items),
                description=items[len(items)//2]['weather'][0]['description'],
                icon=items[len(items)//2]['weather'][0]['icon'],
                precipitation_probability=max(item.get('pop', 0) for item in items) * 100,
                rain_volume=sum(item.get('rain', {}).get('3h', 0) for item in items),
                snow_volume=sum(item.get('snow', {}).get('3h', 0) for item in items)
            )
            daily_forecasts.append(forecast_data)
            
        return Forecast(
            location=location,
            daily_forecasts=daily_forecasts[:5]
        )
        
    def _parse_hourly_forecast(self, data: dict, hours: int) -> List[WeatherData]:
        hourly_data = []
        
        for item in data['list'][:hours // 3]:
            weather_data = WeatherData(
                temperature=item['main']['temp'],
                feels_like=item['main']['feels_like'],
                humidity=item['main']['humidity'],
                pressure=item['main']['pressure'],
                wind_speed=item['wind']['speed'],
                wind_direction=item['wind'].get('deg', 0),
                description=item['weather'][0]['description'],
                icon=item['weather'][0]['icon'],
                clouds=item['clouds']['all'],
                visibility=item.get('visibility', 10000) / 1000,
                timestamp=datetime.fromtimestamp(item['dt'])
            )
            hourly_data.append(weather_data)
            
        return hourly_data
        
    def _parse_locations(self, data: List[dict]) -> List[Location]:
        locations = []
        for item in data:
            location = Location(
                name=item['name'],
                country=item['country'],
                latitude=item['lat'],
                longitude=item['lon'],
                state=item.get('state', ''),
                timezone=0
            )
            locations.append(location)
        return locations
        
    def _parse_air_quality(self, data: dict) -> Dict[str, Any]:
        if 'list' in data and data['list']:
            aqi_data = data['list'][0]
            return {
                'aqi': aqi_data['main']['aqi'],
                'co': aqi_data['components'].get('co', 0),
                'no': aqi_data['components'].get('no', 0),
                'no2': aqi_data['components'].get('no2', 0),
                'o3': aqi_data['components'].get('o3', 0),
                'so2': aqi_data['components'].get('so2', 0),
                'pm2_5': aqi_data['components'].get('pm2_5', 0),
                'pm10': aqi_data['components'].get('pm10', 0),
                'nh3': aqi_data['components'].get('nh3', 0)
            }
        return {}
        
    def _is_cache_valid(self, key: str) -> bool:
        if not self.config.cache_enabled:
            return False
            
        if key not in self._cache or key not in self._cache_expiry:
            return False
            
        return datetime.now() < self._cache_expiry[key]
        
    def _update_cache(self, key: str, value: Any) -> None:
        if self.config.cache_enabled:
            self._cache[key] = value
            self._cache_expiry[key] = datetime.now() + timedelta(
                minutes=self.config.cache_expiry_minutes
            )
            
    def clear_cache(self) -> None:
        self._cache.clear()
        self._cache_expiry.clear()
        logger.info("Weather service cache cleared")