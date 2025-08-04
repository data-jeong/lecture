"""
OpenWeatherMap API 클라이언트
"""

from typing import Optional, List
from ..models import Weather, Forecast, Location, Coordinates
from ..utils.config import Config
from .base_client import BaseAPIClient, APIError


class WeatherAPI(BaseAPIClient):
    """OpenWeatherMap API 클라이언트"""
    
    def __init__(self, config: Config):
        super().__init__(config, config.get_openweather_base_url())
        self.api_key = config.openweather_api_key
        self.units = config.default_units
        self.language = config.default_language
    
    def _build_params(self, **kwargs) -> dict:
        """기본 파라미터 구성"""
        params = {
            'appid': self.api_key,
            'units': self.units,
            'lang': self.language,
            **kwargs
        }
        return params
    
    def get_current_weather_by_city(self, city: str, country_code: Optional[str] = None) -> Weather:
        """도시명으로 현재 날씨 조회"""
        query = f"{city},{country_code}" if country_code else city
        params = self._build_params(q=query)
        
        data = self.with_retry(self.get, "weather", params=params)
        
        # Location 객체 생성
        location = Location.from_openweather_response(data)
        
        # Weather 객체 생성
        weather = Weather.from_openweather_response(data, location)
        
        return weather
    
    def get_current_weather_by_coordinates(self, lat: float, lon: float) -> Weather:
        """좌표로 현재 날씨 조회"""
        params = self._build_params(lat=lat, lon=lon)
        
        data = self.with_retry(self.get, "weather", params=params)
        
        # Location 객체 생성
        location = Location.from_openweather_response(data)
        
        # Weather 객체 생성
        weather = Weather.from_openweather_response(data, location)
        
        return weather
    
    def get_forecast_by_city(self, city: str, country_code: Optional[str] = None) -> Forecast:
        """도시명으로 5일 예보 조회"""
        query = f"{city},{country_code}" if country_code else city
        params = self._build_params(q=query)
        
        data = self.with_retry(self.get, "forecast", params=params)
        
        # Location 객체 생성 (첫 번째 아이템에서)
        city_data = data['city']
        location = Location(
            city=city_data['name'],
            country=city_data['country'],
            coordinates=Coordinates(
                latitude=city_data['coord']['lat'],
                longitude=city_data['coord']['lon']
            )
        )
        
        # Forecast 객체 생성
        forecast = Forecast.from_openweather_5day(data, location)
        
        return forecast
    
    def get_forecast_by_coordinates(self, lat: float, lon: float) -> Forecast:
        """좌표로 5일 예보 조회"""
        params = self._build_params(lat=lat, lon=lon)
        
        data = self.with_retry(self.get, "forecast", params=params)
        
        # Location 객체 생성
        city_data = data['city']
        location = Location(
            city=city_data['name'],
            country=city_data['country'],
            coordinates=Coordinates(
                latitude=city_data['coord']['lat'],
                longitude=city_data['coord']['lon']
            )
        )
        
        # Forecast 객체 생성
        forecast = Forecast.from_openweather_5day(data, location)
        
        return forecast
    
    async def get_current_weather_by_city_async(self, city: str, country_code: Optional[str] = None) -> Weather:
        """비동기 - 도시명으로 현재 날씨 조회"""
        query = f"{city},{country_code}" if country_code else city
        params = self._build_params(q=query)
        
        data = await self.with_retry_async(self.get_async, "weather", params=params)
        
        location = Location.from_openweather_response(data)
        weather = Weather.from_openweather_response(data, location)
        
        return weather
    
    async def get_forecast_by_city_async(self, city: str, country_code: Optional[str] = None) -> Forecast:
        """비동기 - 도시명으로 5일 예보 조회"""
        query = f"{city},{country_code}" if country_code else city
        params = self._build_params(q=query)
        
        data = await self.with_retry_async(self.get_async, "forecast", params=params)
        
        city_data = data['city']
        location = Location(
            city=city_data['name'],
            country=city_data['country'],
            coordinates=Coordinates(
                latitude=city_data['coord']['lat'],
                longitude=city_data['coord']['lon']
            )
        )
        
        forecast = Forecast.from_openweather_5day(data, location)
        
        return forecast
    
    def test_connection(self) -> bool:
        """API 연결 테스트"""
        try:
            # 서울 날씨로 간단한 테스트
            self.get_current_weather_by_city("Seoul", "KR")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_rate_limit_info(self) -> dict:
        """Rate limit 정보 (OpenWeatherMap은 헤더로 제공하지 않음)"""
        return {
            'calls_per_minute': 60,  # Free tier: 60 calls/minute
            'calls_per_month': 1_000_000,  # Free tier: 1,000,000 calls/month
            'note': 'OpenWeatherMap does not provide rate limit headers'
        }