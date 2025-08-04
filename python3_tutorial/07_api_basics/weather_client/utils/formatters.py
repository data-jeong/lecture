"""
데이터 포맷팅 유틸리티
"""

from typing import Optional
from datetime import datetime, date, timedelta


def format_temperature(temp: float, units: str = "metric", decimals: int = 1) -> str:
    """온도 포맷팅"""
    if units.lower() == "metric":
        return f"{temp:.{decimals}f}°C"
    elif units.lower() == "imperial":
        fahrenheit = (temp * 9/5) + 32
        return f"{fahrenheit:.{decimals}f}°F"
    elif units.lower() == "kelvin":
        kelvin = temp + 273.15
        return f"{kelvin:.{decimals}f}K"
    else:
        return f"{temp:.{decimals}f}°C"


def format_wind(speed: float, direction: Optional[float] = None, units: str = "metric") -> str:
    """바람 정보 포맷팅"""
    # 풍속 변환
    if units.lower() == "imperial":
        # m/s to mph
        speed_mph = speed * 2.237
        speed_str = f"{speed_mph:.1f} mph"
    else:
        speed_str = f"{speed:.1f} m/s"
    
    # 풍향 추가
    if direction is not None:
        direction_text = get_wind_direction_text(direction)
        return f"{direction_text} {speed_str}"
    
    return speed_str


def format_pressure(pressure: int, units: str = "metric") -> str:
    """기압 포맷팅"""
    if units.lower() == "imperial":
        # hPa to inHg
        inches = pressure * 0.02953
        return f"{inches:.2f} inHg"
    else:
        return f"{pressure} hPa"


def format_humidity(humidity: int) -> str:
    """습도 포맷팅"""
    return f"{humidity}%"


def format_visibility(visibility: int, units: str = "metric") -> str:
    """가시거리 포맷팅"""
    if units.lower() == "imperial":
        # meters to miles
        miles = visibility * 0.000621371
        if miles < 1:
            feet = visibility * 3.28084
            return f"{feet:.0f} ft"
        return f"{miles:.1f} mi"
    else:
        if visibility >= 1000:
            km = visibility / 1000
            return f"{km:.1f} km"
        return f"{visibility} m"


def format_precipitation(amount: Optional[float], units: str = "metric") -> str:
    """강수량 포맷팅"""
    if amount is None or amount == 0:
        return "0 mm"
    
    if units.lower() == "imperial":
        # mm to inches
        inches = amount * 0.0393701
        return f"{inches:.2f} in"
    else:
        return f"{amount:.1f} mm"


def format_uv_index(uv: float) -> str:
    """자외선 지수 포맷팅"""
    if uv <= 2:
        level = "낮음"
        color = "🟢"
    elif uv <= 5:
        level = "보통"
        color = "🟡"
    elif uv <= 7:
        level = "높음"
        color = "🟠"
    elif uv <= 10:
        level = "매우 높음"
        color = "🔴"
    else:
        level = "위험"
        color = "🟣"
    
    return f"{color} {uv:.1f} ({level})"


def format_air_quality(aqi: int) -> str:
    """대기질 지수 포맷팅"""
    quality_map = {
        1: ("매우 좋음", "🟢"),
        2: ("좋음", "🟡"), 
        3: ("보통", "🟠"),
        4: ("나쁨", "🔴"),
        5: ("매우 나쁨", "🟣")
    }
    
    level, color = quality_map.get(aqi, ("알 수 없음", "⚫"))
    return f"{color} {level} (AQI {aqi})"


def format_datetime(dt: datetime, format_type: str = "full", korean: bool = True) -> str:
    """날짜/시간 포맷팅"""
    if format_type == "date":
        if korean:
            return dt.strftime("%Y년 %m월 %d일")
        return dt.strftime("%Y-%m-%d")
    
    elif format_type == "time":
        return dt.strftime("%H:%M")
    
    elif format_type == "datetime":
        if korean:
            return dt.strftime("%Y년 %m월 %d일 %H:%M")
        return dt.strftime("%Y-%m-%d %H:%M")
    
    elif format_type == "full":
        if korean:
            weekdays = ["월", "화", "수", "목", "금", "토", "일"]
            weekday = weekdays[dt.weekday()]
            return dt.strftime(f"%Y년 %m월 %d일 ({weekday}) %H:%M")
        return dt.strftime("%Y-%m-%d (%A) %H:%M")
    
    return str(dt)


def format_time_ago(dt: datetime) -> str:
    """상대적 시간 포맷팅 (몇 분 전, 몇 시간 전 등)"""
    now = datetime.now()
    diff = now - dt
    
    if diff.total_seconds() < 60:
        return "방금 전"
    elif diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes}분 전"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"{hours}시간 전"
    elif diff.days == 1:
        return "어제"
    elif diff.days < 7:
        return f"{diff.days}일 전"
    else:
        return format_datetime(dt, "date")


def format_duration(seconds: float) -> str:
    """시간 길이 포맷팅"""
    if seconds < 60:
        return f"{seconds:.1f}초"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}분"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}시간"


def get_wind_direction_text(degrees: float) -> str:
    """풍향을 텍스트로 변환"""
    directions = [
        "북", "북북동", "북동", "동북동",
        "동", "동남동", "남동", "남남동", 
        "남", "남남서", "남서", "서남서",
        "서", "서북서", "북서", "북북서"
    ]
    
    index = round(degrees / 22.5) % 16
    return directions[index]


def format_coordinates(lat: float, lon: float, decimals: int = 4) -> str:
    """좌표 포맷팅"""
    lat_str = f"{abs(lat):.{decimals}f}°{'N' if lat >= 0 else 'S'}"
    lon_str = f"{abs(lon):.{decimals}f}°{'E' if lon >= 0 else 'W'}"
    return f"{lat_str}, {lon_str}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """백분율 포맷팅"""
    return f"{value:.{decimals}f}%"


def format_distance(meters: float, units: str = "metric") -> str:
    """거리 포맷팅"""
    if units.lower() == "imperial":
        # meters to feet/miles
        if meters < 1609.34:  # less than 1 mile
            feet = meters * 3.28084
            return f"{feet:.0f} ft"
        else:
            miles = meters * 0.000621371
            return f"{miles:.1f} mi"
    else:
        if meters < 1000:
            return f"{meters:.0f} m"
        else:
            km = meters / 1000
            return f"{km:.1f} km"


def format_speed(mps: float, units: str = "metric") -> str:
    """속도 포맷팅"""
    if units.lower() == "imperial":
        mph = mps * 2.237
        return f"{mph:.1f} mph"
    else:
        return f"{mps:.1f} m/s"


def format_temperature_range(min_temp: float, max_temp: float, units: str = "metric") -> str:
    """온도 범위 포맷팅"""
    min_str = format_temperature(min_temp, units, 0)
    max_str = format_temperature(max_temp, units, 0)
    return f"{min_str} ~ {max_str}"


def format_file_size(bytes_size: int) -> str:
    """파일 크기 포맷팅"""
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(bytes_size)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def format_location_string(city: str, country: str, state: Optional[str] = None) -> str:
    """위치 문자열 포맷팅"""
    parts = [city]
    if state:
        parts.append(state)
    parts.append(country)
    return ", ".join(parts)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """텍스트 줄이기"""
    if len(text) <= max_length:
        return text
    
    truncated_length = max_length - len(suffix)
    return text[:truncated_length] + suffix


def format_list(items: list, max_items: int = 5, separator: str = ", ") -> str:
    """리스트 포맷팅"""
    if len(items) <= max_items:
        return separator.join(str(item) for item in items)
    
    visible_items = items[:max_items]
    remaining = len(items) - max_items
    
    formatted = separator.join(str(item) for item in visible_items)
    return f"{formatted} 외 {remaining}개"