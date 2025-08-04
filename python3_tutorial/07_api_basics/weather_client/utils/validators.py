"""
데이터 검증 유틸리티
"""

import re
from typing import Tuple, Optional


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """GPS 좌표 유효성 검증"""
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def validate_city_name(city: str) -> bool:
    """도시명 유효성 검증"""
    if not city or not city.strip():
        return False
    
    # 최소 2글자, 최대 100글자
    if len(city.strip()) < 2 or len(city.strip()) > 100:
        return False
    
    # 기본적인 문자만 허용 (영문, 한글, 숫자, 공백, 하이픈)
    pattern = r'^[a-zA-Z0-9가-힣\s\-]+$'
    return bool(re.match(pattern, city.strip()))


def validate_api_key(api_key: str) -> bool:
    """API 키 유효성 검증"""
    if not api_key or not api_key.strip():
        return False
    
    # OpenWeatherMap API 키는 32자의 16진수
    if len(api_key) == 32 and re.match(r'^[a-fA-F0-9]+$', api_key):
        return True
    
    # 다른 형태의 API 키도 허용 (최소 10글자)
    return len(api_key.strip()) >= 10


def validate_temperature(temp: float) -> bool:
    """온도 유효성 검증 (섭씨 기준)"""
    return -100 <= temp <= 60


def validate_humidity(humidity: int) -> bool:
    """습도 유효성 검증"""
    return 0 <= humidity <= 100


def validate_pressure(pressure: int) -> bool:
    """기압 유효성 검증 (hPa)"""
    return 800 <= pressure <= 1200


def validate_wind_speed(speed: float) -> bool:
    """풍속 유효성 검증 (m/s)"""
    return 0 <= speed <= 150


def validate_wind_direction(direction: float) -> bool:
    """풍향 유효성 검증 (도)"""
    return 0 <= direction <= 360


def validate_visibility(visibility: int) -> bool:
    """가시거리 유효성 검증 (m)"""
    return 0 <= visibility <= 50000


def validate_country_code(country_code: str) -> bool:
    """국가 코드 검증 (ISO 3166-1 alpha-2)"""
    if not country_code or len(country_code) != 2:
        return False
    
    # 기본적인 알파벳 검증
    return country_code.isalpha()


def validate_language_code(lang_code: str) -> bool:
    """언어 코드 검증"""
    supported_languages = ['ko', 'en', 'ja', 'zh', 'es', 'fr', 'de', 'ru', 'it', 'pt']
    return lang_code.lower() in supported_languages


def validate_units(units: str) -> bool:
    """단위 시스템 검증"""
    return units.lower() in ['metric', 'imperial', 'kelvin']


def sanitize_city_name(city: str) -> str:
    """도시명 정제"""
    if not city:
        return ""
    
    # 앞뒤 공백 제거
    city = city.strip()
    
    # 연속된 공백을 하나로
    city = re.sub(r'\s+', ' ', city)
    
    # 특수문자 제거 (하이픈, 점은 유지)
    city = re.sub(r'[^\w\s\-\.]', '', city)
    
    return city


def parse_coordinates_string(coord_str: str) -> Optional[Tuple[float, float]]:
    """좌표 문자열 파싱"""
    if not coord_str:
        return None
    
    # 다양한 형태의 좌표 문자열 지원
    patterns = [
        r'(-?\d+\.?\d*),\s*(-?\d+\.?\d*)',  # "37.5665, 126.9780"
        r'\((-?\d+\.?\d*),\s*(-?\d+\.?\d*)\)',  # "(37.5665, 126.9780)"
        r'lat:\s*(-?\d+\.?\d*),?\s*lon[g]?:\s*(-?\d+\.?\d*)',  # "lat: 37.5665, lon: 126.9780"
        r'(-?\d+\.?\d*)\s+(-?\d+\.?\d*)',  # "37.5665 126.9780"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, coord_str, re.IGNORECASE)
        if match:
            try:
                lat, lon = float(match.group(1)), float(match.group(2))
                if validate_coordinates(lat, lon):
                    return (lat, lon)
            except ValueError:
                continue
    
    return None


def validate_email(email: str) -> bool:
    """이메일 주소 검증"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_time_format(time_str: str) -> bool:
    """시간 형식 검증 (HH:MM)"""
    if not time_str:
        return False
    
    pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(pattern, time_str))


def validate_date_format(date_str: str) -> bool:
    """날짜 형식 검증 (YYYY-MM-DD)"""
    if not date_str:
        return False
    
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False
    
    # 추가 날짜 유효성 검증
    try:
        from datetime import datetime
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


class ValidationError(Exception):
    """검증 오류 예외"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)
    
    def __str__(self):
        if self.field:
            return f"{self.field}: {self.message}"
        return self.message


def validate_weather_data(data: dict) -> None:
    """날씨 데이터 종합 검증"""
    errors = []
    
    # 필수 필드 확인
    required_fields = ['temperature', 'humidity', 'pressure']
    for field in required_fields:
        if field not in data:
            errors.append(f"필수 필드 누락: {field}")
    
    # 온도 검증
    if 'temperature' in data:
        if not validate_temperature(data['temperature']):
            errors.append("온도가 유효 범위를 벗어났습니다")
    
    # 습도 검증
    if 'humidity' in data:
        if not validate_humidity(data['humidity']):
            errors.append("습도가 유효 범위를 벗어났습니다 (0-100%)")
    
    # 기압 검증
    if 'pressure' in data:
        if not validate_pressure(data['pressure']):
            errors.append("기압이 유효 범위를 벗어났습니다 (800-1200 hPa)")
    
    # 풍속 검증
    if 'wind_speed' in data:
        if not validate_wind_speed(data['wind_speed']):
            errors.append("풍속이 유효 범위를 벗어났습니다")
    
    # 풍향 검증
    if 'wind_direction' in data:
        if not validate_wind_direction(data['wind_direction']):
            errors.append("풍향이 유효 범위를 벗어났습니다 (0-360도)")
    
    if errors:
        raise ValidationError("; ".join(errors))