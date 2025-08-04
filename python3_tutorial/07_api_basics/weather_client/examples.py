#!/usr/bin/env python3
"""
Weather API Client 사용 예제
"""

import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from weather_client.services.weather_service import WeatherService
from weather_client.services.cache_service import CacheService
from weather_client.services.notification import NotificationService
from weather_client.visualization.charts import WeatherCharts
from weather_client.visualization.maps import WeatherMap
from weather_client.utils.formatters import format_weather, format_forecast


def example_basic_weather():
    """기본 날씨 조회 예제"""
    print("\n" + "="*50)
    print("1. 기본 날씨 조회")
    print("="*50)
    
    service = WeatherService()
    
    cities = ["Seoul", "Tokyo", "New York"]
    for city in cities:
        try:
            weather = service.get_current_weather(city)
            print(f"\n{city} 현재 날씨:")
            print(f"  온도: {weather.current.temperature:.1f}°C")
            print(f"  체감온도: {weather.current.feels_like:.1f}°C")
            print(f"  날씨: {weather.current.description}")
            print(f"  습도: {weather.current.humidity}%")
            print(f"  풍속: {weather.current.wind_speed} m/s")
        except Exception as e:
            print(f"  Error: {e}")


def example_forecast():
    """일기예보 조회 예제"""
    print("\n" + "="*50)
    print("2. 5일 일기예보")
    print("="*50)
    
    service = WeatherService()
    
    try:
        forecast = service.get_forecast("Seoul", days=5)
        print(f"\nSeoul 5일 예보:")
        
        for day_forecast in forecast.daily_forecasts:
            print(f"\n{day_forecast.date.strftime('%Y-%m-%d')}:")
            print(f"  최저/최고: {day_forecast.temperature_min:.1f}°C / {day_forecast.temperature_max:.1f}°C")
            print(f"  평균: {day_forecast.temperature_avg:.1f}°C")
            print(f"  날씨: {day_forecast.description}")
            print(f"  강수확률: {day_forecast.precipitation_probability:.0f}%")
    except Exception as e:
        print(f"Error: {e}")


def example_hourly_forecast():
    """시간별 예보 예제"""
    print("\n" + "="*50)
    print("3. 시간별 예보")
    print("="*50)
    
    service = WeatherService()
    
    try:
        hourly = service.get_hourly_forecast("Seoul", hours=12)
        print(f"\nSeoul 12시간 예보:")
        
        for data in hourly[:4]:
            print(f"\n{data.timestamp.strftime('%H:%M')}:")
            print(f"  온도: {data.temperature:.1f}°C")
            print(f"  습도: {data.humidity}%")
            print(f"  날씨: {data.description}")
    except Exception as e:
        print(f"Error: {e}")


def example_coordinates():
    """좌표로 날씨 조회 예제"""
    print("\n" + "="*50)
    print("4. 좌표로 날씨 조회")
    print("="*50)
    
    service = WeatherService()
    
    locations = [
        ("서울", 37.5665, 126.9780),
        ("제주", 33.4996, 126.5312),
        ("부산", 35.1796, 129.0756)
    ]
    
    for name, lat, lon in locations:
        try:
            weather = service.get_weather_by_coordinates(lat, lon)
            print(f"\n{name} ({lat:.4f}, {lon:.4f}):")
            print(f"  온도: {weather.current.temperature:.1f}°C")
            print(f"  날씨: {weather.current.description}")
        except Exception as e:
            print(f"  Error: {e}")


def example_city_search():
    """도시 검색 예제"""
    print("\n" + "="*50)
    print("5. 도시 검색")
    print("="*50)
    
    service = WeatherService()
    
    queries = ["Paris", "London", "Seoul"]
    
    for query in queries:
        try:
            locations = service.search_cities(query, limit=3)
            print(f"\n'{query}' 검색 결과:")
            
            for loc in locations:
                print(f"  - {loc.name}, {loc.country} ({loc.latitude:.4f}, {loc.longitude:.4f})")
        except Exception as e:
            print(f"  Error: {e}")


def example_air_quality():
    """대기질 조회 예제"""
    print("\n" + "="*50)
    print("6. 대기질 정보")
    print("="*50)
    
    service = WeatherService()
    
    try:
        weather = service.get_current_weather("Seoul")
        air_quality = service.get_air_quality(
            weather.location.latitude,
            weather.location.longitude
        )
        
        print(f"\nSeoul 대기질:")
        aqi = air_quality.get('aqi', 0)
        aqi_text = ['', 'Good', 'Fair', 'Moderate', 'Poor', 'Very Poor'][aqi]
        
        print(f"  AQI: {aqi} ({aqi_text})")
        print(f"  PM2.5: {air_quality.get('pm2_5', 0):.1f} μg/m³")
        print(f"  PM10: {air_quality.get('pm10', 0):.1f} μg/m³")
        print(f"  O₃: {air_quality.get('o3', 0):.1f} μg/m³")
    except Exception as e:
        print(f"Error: {e}")


def example_cache():
    """캐시 사용 예제"""
    print("\n" + "="*50)
    print("7. 캐시 사용")
    print("="*50)
    
    cache = CacheService(expiry_minutes=5)
    
    cache.set("test_key", {"data": "test_value"})
    
    cached_data = cache.get("test_key")
    if cached_data:
        print(f"캐시된 데이터: {cached_data}")
    
    stats = cache.get_cache_stats()
    print(f"\n캐시 통계:")
    print(f"  메모리 엔트리: {stats['memory_entries']}")
    print(f"  파일 엔트리: {stats['file_entries']}")
    print(f"  전체 크기: {stats['total_size_mb']:.2f} MB")
    
    cleaned = cache.cleanup_expired()
    print(f"  만료된 엔트리 {cleaned}개 정리됨")


def example_visualization():
    """시각화 예제"""
    print("\n" + "="*50)
    print("8. 데이터 시각화")
    print("="*50)
    
    service = WeatherService()
    charts = WeatherCharts()
    
    try:
        hourly_data = service.get_hourly_forecast("Seoul", hours=24)
        
        print("온도 트렌드 차트 생성 중...")
        
        print("차트 저장 중...")
        charts.plot_temperature_trend(hourly_data, title="Seoul 24-Hour Temperature")
        charts.save_chart("seoul_temperature.png")
        
        print("차트가 'seoul_temperature.png'로 저장되었습니다.")
    except Exception as e:
        print(f"Error: {e}")


def example_map():
    """지도 생성 예제"""
    print("\n" + "="*50)
    print("9. 날씨 지도")
    print("="*50)
    
    service = WeatherService()
    
    try:
        cities = ["Seoul", "Busan", "Daegu", "Incheon"]
        weather_list = []
        
        for city in cities:
            try:
                weather = service.get_current_weather(city)
                weather_list.append(weather)
            except:
                pass
                
        if weather_list:
            weather_map = WeatherMap()
            weather_map.create_comparison_map(weather_list)
            weather_map.save_map("korea_weather_map.html")
            print("지도가 'korea_weather_map.html'로 저장되었습니다.")
    except Exception as e:
        print(f"Error: {e}")


def example_notifications():
    """알림 설정 예제"""
    print("\n" + "="*50)
    print("10. 날씨 알림 설정")
    print("="*50)
    
    notification = NotificationService()
    
    notification.add_alert(
        alert_id="temp_alert_1",
        email="user@example.com",
        city="Seoul",
        condition="temperature_above",
        threshold=30
    )
    
    notification.add_alert(
        alert_id="rain_alert_1",
        email="user@example.com",
        city="Seoul",
        condition="rain",
        threshold=None
    )
    
    print("알림 설정 완료:")
    print("  - 서울 온도 30°C 이상 알림")
    print("  - 서울 비 예보 알림")
    
    user_alerts = notification.get_user_alerts("user@example.com")
    print(f"\n사용자 알림 설정: {len(user_alerts)}개")


def main():
    """모든 예제 실행"""
    print("\n" + "="*60)
    print(" Weather API Client 예제 모음")
    print("="*60)
    
    examples = [
        ("기본 날씨 조회", example_basic_weather),
        ("일기예보", example_forecast),
        ("시간별 예보", example_hourly_forecast),
        ("좌표로 조회", example_coordinates),
        ("도시 검색", example_city_search),
        ("대기질 정보", example_air_quality),
        ("캐시 사용", example_cache),
        ("알림 설정", example_notifications),
    ]
    
    print("\n실행할 예제를 선택하세요:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print("  0. 모든 예제 실행")
    print("  q. 종료")
    
    while True:
        choice = input("\n선택: ").strip()
        
        if choice == 'q':
            break
        elif choice == '0':
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"Error in {name}: {e}")
            break
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(examples):
                    examples[idx][1]()
                else:
                    print("잘못된 선택입니다.")
            except (ValueError, IndexError):
                print("잘못된 입력입니다.")


if __name__ == "__main__":
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        print("경고: OPENWEATHER_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("일부 예제가 작동하지 않을 수 있습니다.")
        print("\n.env 파일을 생성하고 API 키를 설정하세요:")
        print("  OPENWEATHER_API_KEY=your_api_key_here")
    
    main()