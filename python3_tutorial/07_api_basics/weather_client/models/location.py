"""
위치 관련 데이터 모델
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class Coordinates(BaseModel):
    """GPS 좌표"""
    
    latitude: float = Field(..., ge=-90, le=90, description="위도")
    longitude: float = Field(..., ge=-180, le=180, description="경도")
    
    def __str__(self) -> str:
        return f"({self.latitude:.4f}, {self.longitude:.4f})"
    
    def to_dict(self) -> dict:
        return {
            'lat': self.latitude,
            'lon': self.longitude
        }


class Location(BaseModel):
    """위치 정보"""
    
    city: str = Field(..., min_length=1, description="도시명")
    country: str = Field(..., min_length=2, max_length=2, description="국가 코드")
    state: Optional[str] = Field(None, description="주/도")
    coordinates: Optional[Coordinates] = Field(None, description="GPS 좌표")
    timezone: Optional[str] = Field(None, description="시간대")
    
    @validator('country')
    def validate_country_code(cls, v):
        """국가 코드 검증"""
        if len(v) != 2:
            raise ValueError('국가 코드는 2글자여야 합니다')
        return v.upper()
    
    @validator('city')
    def validate_city_name(cls, v):
        """도시명 검증"""
        if not v.strip():
            raise ValueError('도시명은 비어있을 수 없습니다')
        return v.strip()
    
    def __str__(self) -> str:
        if self.state:
            return f"{self.city}, {self.state}, {self.country}"
        return f"{self.city}, {self.country}"
    
    def full_name(self) -> str:
        """전체 이름 반환"""
        parts = [self.city]
        if self.state:
            parts.append(self.state)
        parts.append(self.country)
        return ", ".join(parts)
    
    def to_search_query(self) -> str:
        """검색 쿼리용 문자열"""
        if self.state:
            return f"{self.city},{self.state},{self.country}"
        return f"{self.city},{self.country}"
    
    @classmethod
    def from_openweather_response(cls, data: dict) -> 'Location':
        """OpenWeatherMap API 응답에서 Location 생성"""
        coordinates = None
        if 'coord' in data:
            coordinates = Coordinates(
                latitude=data['coord']['lat'],
                longitude=data['coord']['lon']
            )
        
        return cls(
            city=data['name'],
            country=data['sys']['country'],
            coordinates=coordinates
        )
    
    @classmethod
    def from_geocoding_response(cls, data: dict) -> 'Location':
        """지오코딩 API 응답에서 Location 생성"""
        return cls(
            city=data['name'],
            country=data['country'],
            state=data.get('state'),
            coordinates=Coordinates(
                latitude=data['lat'],
                longitude=data['lon']
            )
        )


class LocationSearch(BaseModel):
    """위치 검색 결과"""
    
    locations: list[Location] = Field(default_factory=list, description="검색된 위치 목록")
    query: str = Field(..., description="검색 쿼리")
    total_count: int = Field(0, description="총 결과 수")
    limit: int = Field(5, description="최대 결과 수")
    
    def has_results(self) -> bool:
        """결과가 있는지 확인"""
        return len(self.locations) > 0
    
    def get_best_match(self) -> Optional[Location]:
        """가장 적합한 결과 반환 (첫 번째)"""
        return self.locations[0] if self.locations else None
    
    def get_by_country(self, country_code: str) -> list[Location]:
        """특정 국가의 결과만 필터링"""
        return [loc for loc in self.locations if loc.country == country_code.upper()]