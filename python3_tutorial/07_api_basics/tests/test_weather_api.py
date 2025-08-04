import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from weather_client.api.weather_api import WeatherAPI
from weather_client.services.weather_service import WeatherService
from weather_client.services.cache_service import CacheService
from weather_client.models.weather import Weather, WeatherData
from weather_client.models.location import Location
from weather_client.utils.validators import validate_city_name, validate_coordinates


class TestWeatherAPI:
    @pytest.fixture
    def api(self):
        return WeatherAPI("test_api_key")
        
    def test_init(self, api):
        assert api.api_key == "test_api_key"
        assert api.base_url == "https://api.openweathermap.org/data/2.5"
        
    @patch('requests.get')
    def test_get_current_weather(self, mock_get, api):
        mock_response = Mock()
        mock_response.json.return_value = {
            'name': 'Seoul',
            'main': {'temp': 20, 'feels_like': 18, 'humidity': 60, 'pressure': 1013},
            'weather': [{'description': 'clear sky', 'icon': '01d'}],
            'wind': {'speed': 3.5, 'deg': 180},
            'clouds': {'all': 10},
            'coord': {'lat': 37.5665, 'lon': 126.9780},
            'sys': {'country': 'KR', 'sunrise': 1234567890, 'sunset': 1234567900},
            'dt': 1234567895,
            'visibility': 10000
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = api.get_current_weather('Seoul')
        
        assert result['name'] == 'Seoul'
        assert result['main']['temp'] == 20
        mock_get.assert_called_once()
        
    @patch('requests.get')
    def test_get_forecast(self, mock_get, api):
        mock_response = Mock()
        mock_response.json.return_value = {
            'city': {
                'name': 'Seoul',
                'country': 'KR',
                'coord': {'lat': 37.5665, 'lon': 126.9780}
            },
            'list': []
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = api.get_forecast('Seoul')
        
        assert result['city']['name'] == 'Seoul'
        mock_get.assert_called_once()


class TestWeatherService:
    @pytest.fixture
    def service(self):
        with patch('weather_client.services.weather_service.Config'):
            return WeatherService("test_api_key")
            
    @patch('weather_client.services.weather_service.WeatherAPI')
    def test_get_current_weather(self, mock_api_class, service):
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        
        mock_api.get_current_weather.return_value = {
            'name': 'Seoul',
            'main': {'temp': 20, 'feels_like': 18, 'humidity': 60, 'pressure': 1013},
            'weather': [{'description': 'clear sky', 'icon': '01d'}],
            'wind': {'speed': 3.5, 'deg': 180},
            'clouds': {'all': 10},
            'coord': {'lat': 37.5665, 'lon': 126.9780},
            'sys': {'country': 'KR', 'sunrise': 1234567890, 'sunset': 1234567900},
            'dt': 1234567895,
            'visibility': 10000
        }
        
        service.api = mock_api
        result = service.get_current_weather('Seoul')
        
        assert isinstance(result, Weather)
        assert result.location.name == 'Seoul'
        assert result.current.temperature == 20
        
    def test_cache_operations(self, service):
        service._update_cache('test_key', 'test_value')
        
        service.config.cache_enabled = True
        assert service._is_cache_valid('test_key')
        
        service.clear_cache()
        assert not service._is_cache_valid('test_key')


class TestCacheService:
    @pytest.fixture
    def cache(self, tmp_path):
        return CacheService(cache_dir=str(tmp_path / "test_cache"))
        
    def test_set_and_get(self, cache):
        cache.set('test_key', {'data': 'test_value'})
        
        result = cache.get('test_key')
        assert result == {'data': 'test_value'}
        
    def test_get_nonexistent(self, cache):
        result = cache.get('nonexistent_key')
        assert result is None
        
    def test_delete(self, cache):
        cache.set('test_key', 'test_value')
        cache.delete('test_key')
        
        result = cache.get('test_key')
        assert result is None
        
    def test_clear(self, cache):
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        
        cache.clear()
        
        assert cache.get('key1') is None
        assert cache.get('key2') is None
        
    def test_cache_stats(self, cache):
        cache.set('test_key', 'test_value')
        
        stats = cache.get_cache_stats()
        assert stats['memory_entries'] >= 1
        assert stats['total_entries'] >= 1


class TestValidators:
    def test_validate_city_name_valid(self):
        validate_city_name("Seoul")
        validate_city_name("New York")
        validate_city_name("São Paulo")
        
    def test_validate_city_name_invalid(self):
        with pytest.raises(ValueError):
            validate_city_name("")
        with pytest.raises(ValueError):
            validate_city_name("a")
        with pytest.raises(ValueError):
            validate_city_name("a" * 101)
            
    def test_validate_coordinates_valid(self):
        validate_coordinates(37.5665, 126.9780)
        validate_coordinates(-90, 180)
        validate_coordinates(90, -180)
        
    def test_validate_coordinates_invalid(self):
        with pytest.raises(ValueError):
            validate_coordinates(91, 0)
        with pytest.raises(ValueError):
            validate_coordinates(-91, 0)
        with pytest.raises(ValueError):
            validate_coordinates(0, 181)
        with pytest.raises(ValueError):
            validate_coordinates(0, -181)


class TestWeatherModels:
    def test_weather_data_creation(self):
        data = WeatherData(
            temperature=20.5,
            feels_like=18.3,
            humidity=65,
            pressure=1013,
            wind_speed=3.5,
            wind_direction=180,
            description="clear sky",
            icon="01d",
            clouds=10,
            visibility=10,
            timestamp=datetime.now()
        )
        
        assert data.temperature == 20.5
        assert data.humidity == 65
        assert data.description == "clear sky"
        
    def test_location_creation(self):
        location = Location(
            name="Seoul",
            country="KR",
            latitude=37.5665,
            longitude=126.9780,
            timezone=32400
        )
        
        assert location.name == "Seoul"
        assert location.country == "KR"
        assert location.latitude == 37.5665
        
    def test_weather_creation(self):
        location = Location(
            name="Seoul",
            country="KR",
            latitude=37.5665,
            longitude=126.9780,
            timezone=32400
        )
        
        weather_data = WeatherData(
            temperature=20.5,
            feels_like=18.3,
            humidity=65,
            pressure=1013,
            wind_speed=3.5,
            wind_direction=180,
            description="clear sky",
            icon="01d",
            clouds=10,
            visibility=10,
            timestamp=datetime.now()
        )
        
        weather = Weather(
            location=location,
            current=weather_data,
            sunrise=datetime.now(),
            sunset=datetime.now()
        )
        
        assert weather.location.name == "Seoul"
        assert weather.current.temperature == 20.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])