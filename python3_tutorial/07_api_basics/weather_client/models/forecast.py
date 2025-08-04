"""
예보 데이터 모델
"""

from datetime import datetime, date
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from .weather import WeatherCondition
from .location import Location


class ForecastItem(BaseModel):
    """예보 아이템 (특정 시점)"""
    
    datetime: datetime = Field(..., description="예보 시간")
    temperature: float = Field(..., description="온도 (°C)")
    feels_like: float = Field(..., description="체감 온도 (°C)")
    temp_min: float = Field(..., description="최저 온도 (°C)")
    temp_max: float = Field(..., description="최고 온도 (°C)")
    pressure: int = Field(..., description="기압 (hPa)")
    humidity: int = Field(..., ge=0, le=100, description="습도 (%)")
    
    condition: WeatherCondition = Field(..., description="날씨 상태")
    description: str = Field(..., description="날씨 설명")
    icon_code: Optional[str] = Field(None, description="날씨 아이콘 코드")
    
    wind_speed: float = Field(0, description="풍속 (m/s)")
    wind_direction: Optional[float] = Field(None, description="풍향 (도)")
    wind_gust: Optional[float] = Field(None, description="돌풍 (m/s)")
    
    clouds: int = Field(0, ge=0, le=100, description="구름량 (%)")
    rain_3h: Optional[float] = Field(None, description="3시간 강수량 (mm)")
    snow_3h: Optional[float] = Field(None, description="3시간 적설량 (mm)")
    
    pop: float = Field(0, ge=0, le=1, description="강수 확률 (0-1)")
    visibility: Optional[int] = Field(None, description="가시거리 (m)")
    
    def get_time_str(self) -> str:
        """시간 문자열"""
        return self.datetime.strftime("%H:%M")
    
    def get_date_str(self) -> str:
        """날짜 문자열"""
        return self.datetime.strftime("%m-%d")
    
    def get_pop_percentage(self) -> int:
        """강수확률 백분율"""
        return int(self.pop * 100)
    
    def is_day_time(self) -> bool:
        """낮 시간인지 확인"""
        hour = self.datetime.hour
        return 6 <= hour <= 18
    
    def get_summary(self) -> str:
        """예보 요약"""
        icon = self.condition.get_icon()
        korean_condition = self.condition.to_korean()
        time_str = self.get_time_str()
        
        summary = f"{time_str} {icon} {korean_condition} {self.temperature}°C"
        
        if self.pop > 0.3:  # 30% 이상
            summary += f" (강수 {self.get_pop_percentage()}%)"
        
        return summary


class DailyForecast(BaseModel):
    """일별 예보"""
    
    date: date = Field(..., description="예보 날짜")
    temp_min: float = Field(..., description="최저 온도 (°C)")
    temp_max: float = Field(..., description="최고 온도 (°C)")
    condition: WeatherCondition = Field(..., description="주요 날씨 상태")
    description: str = Field(..., description="날씨 설명")
    
    humidity: int = Field(..., description="평균 습도 (%)")
    pressure: int = Field(..., description="평균 기압 (hPa)")
    wind_speed: float = Field(0, description="평균 풍속 (m/s)")
    
    rain_total: float = Field(0, description="총 강수량 (mm)")
    snow_total: float = Field(0, description="총 적설량 (mm)")
    pop_max: float = Field(0, description="최대 강수확률")
    
    sunrise: Optional[datetime] = Field(None, description="일출 시간")
    sunset: Optional[datetime] = Field(None, description="일몰 시간")
    
    hourly_items: List[ForecastItem] = Field(default_factory=list, description="시간별 예보")
    
    def get_date_str(self) -> str:
        """날짜 문자열 (한국어)"""
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        weekday = weekdays[self.date.weekday()]
        return f"{self.date.month}/{self.date.day} ({weekday})"
    
    def get_temperature_range(self) -> str:
        """온도 범위 문자열"""
        return f"{self.temp_min:.0f}°C ~ {self.temp_max:.0f}°C"
    
    def get_summary(self) -> str:
        """일별 예보 요약"""
        icon = self.condition.get_icon()
        korean_condition = self.condition.to_korean()
        date_str = self.get_date_str()
        temp_range = self.get_temperature_range()
        
        summary = f"{date_str} {icon} {korean_condition} {temp_range}"
        
        if self.rain_total > 0:
            summary += f", 강수 {self.rain_total:.1f}mm"
        
        return summary
    
    def is_rainy(self) -> bool:
        """비가 오는 날인지"""
        return self.rain_total > 0 or self.pop_max > 0.5
    
    def is_snowy(self) -> bool:
        """눈이 오는 날인지"""
        return self.snow_total > 0 or self.condition == WeatherCondition.SNOW


class HourlyForecast(BaseModel):
    """시간별 예보"""
    
    location: Location = Field(..., description="위치 정보")
    items: List[ForecastItem] = Field(default_factory=list, description="시간별 예보 목록")
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    
    def get_items_by_date(self, target_date: date) -> List[ForecastItem]:
        """특정 날짜의 예보만 반환"""
        return [item for item in self.items if item.datetime.date() == target_date]
    
    def get_next_24h(self) -> List[ForecastItem]:
        """다음 24시간 예보"""
        now = datetime.now()
        return [
            item for item in self.items 
            if item.datetime >= now and 
            (item.datetime - now).total_seconds() <= 24 * 3600
        ]
    
    def get_daily_summary(self) -> List[DailyForecast]:
        """일별 요약 생성"""
        daily_data: Dict[date, List[ForecastItem]] = {}
        
        # 날짜별로 그룹핑
        for item in self.items:
            day = item.datetime.date()
            if day not in daily_data:
                daily_data[day] = []
            daily_data[day].append(item)
        
        daily_forecasts = []
        for day, day_items in sorted(daily_data.items()):
            if not day_items:
                continue
            
            # 일별 통계 계산
            temps = [item.temperature for item in day_items]
            humidities = [item.humidity for item in day_items]
            pressures = [item.pressure for item in day_items]
            wind_speeds = [item.wind_speed for item in day_items]
            rain_amounts = [item.rain_3h or 0 for item in day_items]
            snow_amounts = [item.snow_3h or 0 for item in day_items]
            pops = [item.pop for item in day_items]
            
            # 주요 날씨 상태 결정 (가장 빈번한 것)
            conditions = [item.condition for item in day_items]
            main_condition = max(set(conditions), key=conditions.count)
            
            # 설명도 가장 빈번한 것
            descriptions = [item.description for item in day_items]
            main_description = max(set(descriptions), key=descriptions.count)
            
            daily_forecast = DailyForecast(
                date=day,
                temp_min=min(temps),
                temp_max=max(temps),
                condition=main_condition,
                description=main_description,
                
                humidity=int(sum(humidities) / len(humidities)),
                pressure=int(sum(pressures) / len(pressures)),
                wind_speed=sum(wind_speeds) / len(wind_speeds),
                
                rain_total=sum(rain_amounts),
                snow_total=sum(snow_amounts),
                pop_max=max(pops),
                
                hourly_items=day_items
            )
            
            daily_forecasts.append(daily_forecast)
        
        return daily_forecasts
    
    def find_rain_periods(self) -> List[tuple[datetime, datetime]]:
        """비가 오는 시간대 찾기"""
        rain_periods = []
        start_time = None
        
        for item in self.items:
            is_raining = (item.rain_3h and item.rain_3h > 0) or item.pop > 0.5
            
            if is_raining and start_time is None:
                start_time = item.datetime
            elif not is_raining and start_time is not None:
                rain_periods.append((start_time, item.datetime))
                start_time = None
        
        # 마지막 비가 끝까지 이어지는 경우
        if start_time is not None:
            rain_periods.append((start_time, self.items[-1].datetime))
        
        return rain_periods


class Forecast(BaseModel):
    """전체 예보 정보"""
    
    location: Location = Field(..., description="위치 정보")
    current_weather: Optional['Weather'] = Field(None, description="현재 날씨")
    hourly_forecast: Optional[HourlyForecast] = Field(None, description="시간별 예보")
    daily_forecast: List[DailyForecast] = Field(default_factory=list, description="일별 예보")
    
    generated_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    expires_at: Optional[datetime] = Field(None, description="만료 시간")
    
    def is_expired(self) -> bool:
        """예보가 만료되었는지 확인"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def get_today_forecast(self) -> Optional[DailyForecast]:
        """오늘 예보"""
        today = date.today()
        return next((df for df in self.daily_forecast if df.date == today), None)
    
    def get_tomorrow_forecast(self) -> Optional[DailyForecast]:
        """내일 예보"""
        from datetime import timedelta
        tomorrow = date.today() + timedelta(days=1)
        return next((df for df in self.daily_forecast if df.date == tomorrow), None)
    
    def get_summary(self) -> str:
        """예보 요약"""
        location_str = str(self.location)
        
        summary_parts = [f"📍 {location_str}"]
        
        if self.current_weather:
            summary_parts.append(f"현재: {self.current_weather.get_summary()}")
        
        today = self.get_today_forecast()
        if today:
            summary_parts.append(f"오늘: {today.get_summary()}")
        
        tomorrow = self.get_tomorrow_forecast()
        if tomorrow:
            summary_parts.append(f"내일: {tomorrow.get_summary()}")
        
        return "\n".join(summary_parts)
    
    @classmethod
    def from_openweather_5day(cls, data: dict, location: Location) -> 'Forecast':
        """OpenWeatherMap 5일 예보 API에서 생성"""
        forecast_items = []
        
        for item_data in data['list']:
            main = item_data['main']
            weather_data = item_data['weather'][0]
            wind = item_data.get('wind', {})
            rain = item_data.get('rain', {})
            snow = item_data.get('snow', {})
            
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
            
            item = ForecastItem(
                datetime=datetime.fromtimestamp(item_data['dt']),
                temperature=main['temp'],
                feels_like=main['feels_like'],
                temp_min=main['temp_min'],
                temp_max=main['temp_max'],
                pressure=main['pressure'],
                humidity=main['humidity'],
                
                condition=condition,
                description=weather_data['description'],
                icon_code=weather_data.get('icon'),
                
                wind_speed=wind.get('speed', 0),
                wind_direction=wind.get('deg'),
                wind_gust=wind.get('gust'),
                
                clouds=item_data.get('clouds', {}).get('all', 0),
                rain_3h=rain.get('3h'),
                snow_3h=snow.get('3h'),
                
                pop=item_data.get('pop', 0),
                visibility=item_data.get('visibility')
            )
            
            forecast_items.append(item)
        
        # 시간별 예보 생성
        hourly = HourlyForecast(
            location=location,
            items=forecast_items
        )
        
        # 일별 예보 생성
        daily = hourly.get_daily_summary()
        
        return cls(
            location=location,
            hourly_forecast=hourly,
            daily_forecast=daily
        )


# Forward reference 해결
from .weather import Weather
Forecast.model_rebuild()