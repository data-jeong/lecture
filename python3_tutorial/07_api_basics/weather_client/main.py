#!/usr/bin/env python3
import argparse
import sys
import os
from datetime import datetime
from typing import Optional
import logging
from pathlib import Path

from dotenv import load_dotenv

from .services.weather_service import WeatherService
from .services.cache_service import CacheService
from .services.notification import NotificationService
from .visualization.charts import WeatherCharts
from .visualization.maps import WeatherMap
from .utils.formatters import format_weather, format_forecast, format_hourly
from .utils.config import Config

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeatherClient:
    def __init__(self):
        self.config = Config()
        self.weather_service = WeatherService()
        self.cache_service = CacheService()
        self.notification_service = NotificationService(
            smtp_user=os.getenv('SMTP_USER'),
            smtp_password=os.getenv('SMTP_PASSWORD')
        )
        self.charts = WeatherCharts()
        
    def get_current_weather(self, city: str, visualize: bool = False,
                           save_map: bool = False) -> None:
        try:
            weather = self.weather_service.get_current_weather(city)
            
            print(format_weather(weather))
            
            if visualize:
                self.charts.plot_weather_overview(weather.current)
                
            if save_map:
                weather_map = WeatherMap(
                    center=(weather.location.latitude, weather.location.longitude)
                )
                weather_map.create_map()
                weather_map.add_weather_marker(weather)
                weather_map.save_map(f"{city}_weather_map.html")
                
        except Exception as e:
            logger.error(f"Failed to get weather for {city}: {e}")
            print(f"Error: {e}")
            
    def get_forecast(self, city: str, days: int = 5, visualize: bool = False) -> None:
        try:
            forecast = self.weather_service.get_forecast(city, days)
            
            print(format_forecast(forecast))
            
            if visualize:
                self.charts.plot_forecast_comparison(
                    forecast.daily_forecasts,
                    title=f"{city} {days}-Day Forecast"
                )
                
        except Exception as e:
            logger.error(f"Failed to get forecast for {city}: {e}")
            print(f"Error: {e}")
            
    def get_hourly_forecast(self, city: str, hours: int = 24,
                          visualize: bool = False) -> None:
        try:
            hourly_data = self.weather_service.get_hourly_forecast(city, hours)
            
            print(format_hourly(hourly_data, city))
            
            if visualize:
                self.charts.plot_temperature_trend(
                    hourly_data,
                    title=f"{city} {hours}-Hour Temperature Trend"
                )
                self.charts.plot_hourly_comparison(
                    hourly_data,
                    metrics=['temperature', 'humidity', 'wind_speed']
                )
                
        except Exception as e:
            logger.error(f"Failed to get hourly forecast for {city}: {e}")
            print(f"Error: {e}")
            
    def compare_cities(self, cities: list, visualize: bool = False) -> None:
        weather_list = []
        
        for city in cities:
            try:
                weather = self.weather_service.get_current_weather(city)
                weather_list.append(weather)
                print(f"\n{city}:")
                print("-" * 40)
                print(format_weather(weather))
            except Exception as e:
                print(f"Failed to get weather for {city}: {e}")
                
        if visualize and weather_list:
            weather_map = WeatherMap()
            weather_map.create_comparison_map(weather_list)
            weather_map.save_map("cities_comparison_map.html")
            
    def search_city(self, query: str, limit: int = 5) -> None:
        try:
            locations = self.weather_service.search_cities(query, limit)
            
            if not locations:
                print(f"No cities found for '{query}'")
                return
                
            print(f"\nSearch results for '{query}':")
            print("-" * 50)
            
            for i, loc in enumerate(locations, 1):
                print(f"{i}. {loc.name}, {loc.state or ''} {loc.country}")
                print(f"   Coordinates: ({loc.latitude:.4f}, {loc.longitude:.4f})")
                
        except Exception as e:
            logger.error(f"Failed to search cities: {e}")
            print(f"Error: {e}")
            
    def get_air_quality(self, city: str) -> None:
        try:
            weather = self.weather_service.get_current_weather(city)
            air_quality = self.weather_service.get_air_quality(
                weather.location.latitude,
                weather.location.longitude
            )
            
            print(f"\nAir Quality for {city}:")
            print("-" * 40)
            
            aqi = air_quality.get('aqi', 0)
            aqi_text = ['', 'Good', 'Fair', 'Moderate', 'Poor', 'Very Poor'][aqi]
            
            print(f"Air Quality Index: {aqi} ({aqi_text})")
            print(f"CO: {air_quality.get('co', 0):.1f} μg/m³")
            print(f"NO₂: {air_quality.get('no2', 0):.1f} μg/m³")
            print(f"O₃: {air_quality.get('o3', 0):.1f} μg/m³")
            print(f"SO₂: {air_quality.get('so2', 0):.1f} μg/m³")
            print(f"PM2.5: {air_quality.get('pm2_5', 0):.1f} μg/m³")
            print(f"PM10: {air_quality.get('pm10', 0):.1f} μg/m³")
            
        except Exception as e:
            logger.error(f"Failed to get air quality: {e}")
            print(f"Error: {e}")
            
    def setup_alert(self, email: str, city: str, condition: str,
                   threshold: Optional[float] = None) -> None:
        alert_id = f"{email}_{city}_{condition}_{datetime.now().timestamp()}"
        
        self.notification_service.add_alert(
            alert_id=alert_id,
            email=email,
            city=city,
            condition=condition,
            threshold=threshold
        )
        
        print(f"Alert set up successfully!")
        print(f"Alert ID: {alert_id}")
        print(f"You will receive notifications when {condition} threshold is met.")
        
    def clear_cache(self) -> None:
        self.cache_service.clear()
        self.weather_service.clear_cache()
        print("Cache cleared successfully!")
        
    def show_cache_stats(self) -> None:
        stats = self.cache_service.get_cache_stats()
        
        print("\nCache Statistics:")
        print("-" * 40)
        print(f"Memory entries: {stats['memory_entries']}")
        print(f"File entries: {stats['file_entries']}")
        print(f"Total entries: {stats['total_entries']}")
        print(f"Cache directory: {stats['cache_dir']}")
        print(f"Total size: {stats['total_size_mb']:.2f} MB")


def main():
    parser = argparse.ArgumentParser(description='Weather API Client')
    
    parser.add_argument('--city', '-c', type=str, help='City name')
    parser.add_argument('--forecast', '-f', action='store_true',
                       help='Get 5-day forecast')
    parser.add_argument('--hourly', '-h', type=int, metavar='HOURS',
                       help='Get hourly forecast for specified hours')
    parser.add_argument('--visualize', '-v', action='store_true',
                       help='Visualize weather data')
    parser.add_argument('--map', '-m', action='store_true',
                       help='Save weather map')
    parser.add_argument('--compare', nargs='+', metavar='CITY',
                       help='Compare weather between cities')
    parser.add_argument('--search', '-s', type=str,
                       help='Search for cities')
    parser.add_argument('--air-quality', '-a', action='store_true',
                       help='Get air quality data')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Clear cache')
    parser.add_argument('--cache-stats', action='store_true',
                       help='Show cache statistics')
    
    args = parser.parse_args()
    
    client = WeatherClient()
    
    if args.clear_cache:
        client.clear_cache()
    elif args.cache_stats:
        client.show_cache_stats()
    elif args.search:
        client.search_city(args.search)
    elif args.compare:
        client.compare_cities(args.compare, visualize=args.visualize)
    elif args.city:
        if args.forecast:
            client.get_forecast(args.city, visualize=args.visualize)
        elif args.hourly:
            client.get_hourly_forecast(args.city, args.hourly,
                                      visualize=args.visualize)
        elif args.air_quality:
            client.get_air_quality(args.city)
        else:
            client.get_current_weather(args.city, visualize=args.visualize,
                                     save_map=args.map)
    else:
        parser.print_help()
        

if __name__ == '__main__':
    main()