"""
날씨 데이터 모델
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, validator
from .location import Location


class WeatherCondition(str, Enum):
    """날씨 상태 열거형"""
    
    CLEAR = "clear"
    CLOUDS = "clouds" 
    RAIN = "rain"
    DRIZZLE = "drizzle"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"
    MIST = "mist"
    SMOKE = "smoke"
    HAZE = "haze"
    DUST = "dust"
    FOG = "fog"
    SAND = "sand"
    ASH = "ash"
    SQUALL = "squall"
    TORNADO = "tornado"
    
    def to_korean(self) -> str:
        """한국어 변환"""
        korean_map = {
            self.CLEAR: "맑음",
            self.CLOUDS: "흐림",
            self.RAIN: "비",
            self.DRIZZLE: "이슬비",
            self.THUNDERSTORM: "뇌우",
            self.SNOW: "눈",
            self.MIST: "안개",
            self.SMOKE: "연기",
            self.HAZE: "실안개",
            self.DUST: "먼지",
            self.FOG: "짙은안개",
            self.SAND: "모래먼지",
            self.ASH: "화산재",
            self.SQUALL: "돌풍",
            self.TORNADO: "토네이도",
        }
        return korean_map.get(self, self.value)
    
    def get_icon(self) -> str:
        """날씨 아이콘 이모지"""
        icon_map = {
            self.CLEAR: "☀️",
            self.CLOUDS: "☁️",
            self.RAIN: "🌧️",
            self.DRIZZLE: "🌦️",
            self.THUNDERSTORM: "⛈️",
            self.SNOW: "❄️",
            self.MIST: "🌫️",
            self.SMOKE: "💨",
            self.HAZE: "🌫️",
            self.DUST: "💨",
            self.FOG: "🌫️",
            self.SAND: "💨",
            self.ASH: "🌋",
            self.SQUALL: "💨",
            self.TORNADO: "🌪️",
        }
        return icon_map.get(self, "🌡️")


class AirQuality(BaseModel):
    """대기질 정보"""
    
    aqi: int = Field(..., ge=1, le=5, description="대기질 지수 (1-5)")
    co: Optional[float] = Field(None, description="일산화탄소 (μg/m³)")
    no: Optional[float] = Field(None, description="일산화질소 (μg/m³)")
    no2: Optional[float] = Field(None, description="이산화질소 (μg/m³)")
    o3: Optional[float] = Field(None, description="오존 (μg/m³)")
    so2: Optional[float] = Field(None, description="이산화황 (μg/m³)")
    pm2_5: Optional[float] = Field(None, description="미세먼지 PM2.5 (μg/m³)")
    pm10: Optional[float] = Field(None, description="미세먼지 PM10 (μg/m³)")
    nh3: Optional[float] = Field(None, description="암모니아 (μg/m³)")
    
    def get_quality_text(self) -> str:
        """대기질 텍스트"""
        quality_map = {
            1: "매우 좋음",
            2: "좋음", 
            3: "보통",
            4: "나쁨",
            5: "매우 나쁨"
        }
        return quality_map.get(self.aqi, "알 수 없음")
    
    def get_quality_color(self) -> str:
        """대기질 색상 코드"""
        color_map = {
            1: "#00e400",  # 초록
            2: "#ffff00",  # 노랑
            3: "#ff7e00",  # 주황
            4: "#ff0000",  # 빨강
            5: "#8f3f97"   # 보라
        }
        return color_map.get(self.aqi, "#000000")


class Weather(BaseModel):
    """현재 날씨 정보"""
    
    location: Location = Field(..., description="위치 정보")
    temperature: float = Field(..., description="현재 온도 (°C)")
    feels_like: float = Field(..., description="체감 온도 (°C)")
    temp_min: float = Field(..., description="최저 온도 (°C)")
    temp_max: float = Field(..., description="최고 온도 (°C)")
    pressure: int = Field(..., description="기압 (hPa)")
    humidity: int = Field(..., ge=0, le=100, description="습도 (%)")
    visibility: Optional[int] = Field(None, description="가시거리 (m)")
    uv_index: Optional[float] = Field(None, description="자외선 지수")
    
    condition: WeatherCondition = Field(..., description="날씨 상태")
    description: str = Field(..., description="날씨 설명")
    icon_code: Optional[str] = Field(None, description="날씨 아이콘 코드")
    
    wind_speed: float = Field(0, description="풍속 (m/s)")
    wind_direction: Optional[float] = Field(None, ge=0, le=360, description="풍향 (도)")
    wind_gust: Optional[float] = Field(None, description="돌풍 (m/s)")
    
    clouds: int = Field(0, ge=0, le=100, description="구름량 (%)")
    rain_1h: Optional[float] = Field(None, description="1시간 강수량 (mm)")
    rain_3h: Optional[float] = Field(None, description="3시간 강수량 (mm)")
    snow_1h: Optional[float] = Field(None, description="1시간 적설량 (mm)")
    snow_3h: Optional[float] = Field(None, description="3시간 적설량 (mm)")
    
    sunrise: Optional[datetime] = Field(None, description="일출 시간")
    sunset: Optional[datetime] = Field(None, description="일몰 시간")
    
    timestamp: datetime = Field(default_factory=datetime.now, description="데이터 수집 시간")
    air_quality: Optional[AirQuality] = Field(None, description="대기질 정보")
    
    @validator('temperature', 'feels_like', 'temp_min', 'temp_max')
    def validate_temperature(cls, v):
        """온도 범위 검증"""
        if v < -100 or v > 60:
            raise ValueError('온도가 합리적 범위를 벗어났습니다')
        return v
    
    def get_wind_direction_text(self) -> str:
        """풍향을 텍스트로 변환"""
        if self.wind_direction is None:
            return "정보 없음"
        
        directions = [
            "북", "북동", "동", "남동",
            "남", "남서", "서", "북서"
        ]
        
        index = round(self.wind_direction / 45) % 8
        return directions[index]
    
    def get_wind_scale(self) -> str:
        """바람의 강도 등급"""
        if self.wind_speed < 0.3:
            return "무풍"
        elif self.wind_speed < 1.6:
            return "실바람"
        elif self.wind_speed < 3.4:
            return "가벼운 바람"
        elif self.wind_speed < 5.5:
            return "살랑바람"
        elif self.wind_speed < 8.0:
            return "약한 바람"
        elif self.wind_speed < 10.8:
            return "신선한 바람"
        elif self.wind_speed < 13.9:
            return "센바람"
        elif self.wind_speed < 17.2:
            return "돌바람"
        elif self.wind_speed < 20.8:
            return "큰바람"
        elif self.wind_speed < 24.5:
            return "강풍"
        else:
            return "폭풍"
    
    def is_comfortable(self) -> bool:
        """쾌적한 날씨인지 판단"""
        return (
            15 <= self.temperature <= 25 and
            30 <= self.humidity <= 70 and
            self.wind_speed < 10 and
            self.condition in [WeatherCondition.CLEAR, WeatherCondition.CLOUDS]
        )
    
    def get_summary(self) -> str:
        """날씨 요약"""
        icon = self.condition.get_icon()
        korean_condition = self.condition.to_korean()
        
        summary = f"{icon} {korean_condition}, {self.temperature}°C"
        
        if abs(self.temperature - self.feels_like) > 3:
            summary += f" (체감 {self.feels_like}°C)"
        
        if self.rain_1h and self.rain_1h > 0:
            summary += f", 강수 {self.rain_1h}mm"
        
        return summary
    
    @classmethod
    def from_openweather_response(cls, data: dict, location: Location) -> 'Weather':
        """OpenWeatherMap API 응답에서 Weather 생성"""
        main = data['main']
        weather_data = data['weather'][0]
        wind = data.get('wind', {})
        rain = data.get('rain', {})
        snow = data.get('snow', {})
        sys = data['sys']
        
        # 날씨 상태 매핑
        condition_map = {
            'Clear': WeatherCondition.CLEAR,
            'Clouds': WeatherCondition.CLOUDS,
            'Rain': WeatherCondition.RAIN,
            'Drizzle': WeatherCondition.DRIZZLE,
            'Thunderstorm': WeatherCondition.THUNDERSTORM,
            'Snow': WeatherCondition.SNOW,
            'Mist': WeatherCondition.MIST,
            'Smoke': WeatherCondition.SMOKE,
            'Haze': WeatherCondition.HAZE,
            'Dust': WeatherCondition.DUST,
            'Fog': WeatherCondition.FOG,
            'Sand': WeatherCondition.SAND,
            'Ash': WeatherCondition.ASH,
            'Squall': WeatherCondition.SQUALL,
            'Tornado': WeatherCondition.TORNADO,
        }
        
        condition = condition_map.get(weather_data['main'], WeatherCondition.CLEAR)
        
        # 일출/일몰 시간 변환
        sunrise = datetime.fromtimestamp(sys['sunrise']) if 'sunrise' in sys else None
        sunset = datetime.fromtimestamp(sys['sunset']) if 'sunset' in sys else None
        
        return cls(
            location=location,
            temperature=main['temp'],
            feels_like=main['feels_like'],
            temp_min=main['temp_min'],
            temp_max=main['temp_max'],
            pressure=main['pressure'],
            humidity=main['humidity'],
            visibility=data.get('visibility'),
            
            condition=condition,
            description=weather_data['description'],
            icon_code=weather_data.get('icon'),
            
            wind_speed=wind.get('speed', 0),
            wind_direction=wind.get('deg'),
            wind_gust=wind.get('gust'),
            
            clouds=data.get('clouds', {}).get('all', 0),
            rain_1h=rain.get('1h'),
            rain_3h=rain.get('3h'),
            snow_1h=snow.get('1h'),
            snow_3h=snow.get('3h'),
            
            sunrise=sunrise,
            sunset=sunset,
            timestamp=datetime.fromtimestamp(data['dt'])
        )