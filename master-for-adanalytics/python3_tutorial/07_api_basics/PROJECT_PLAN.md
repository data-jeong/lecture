# 07. API 기초 - 날씨 API 클라이언트

## 프로젝트 개요
RESTful API의 개념을 이해하고 외부 API를 활용하여 날씨 정보 조회 앱을 만듭니다.

## 학습 목표
- REST API 원칙 이해
- HTTP 메서드 (GET, POST, PUT, DELETE)
- JSON 데이터 처리
- API 인증 방식 (API Key, OAuth)
- 에러 처리와 재시도 로직

## 프로젝트 기능
1. **날씨 정보 조회**
   - 현재 날씨
   - 5일 예보
   - 시간별 예보
   - 특정 도시 검색

2. **데이터 시각화**
   - 온도 그래프
   - 날씨 아이콘 표시
   - 지도 표시 (folium)
   - 데이터 차트 (matplotlib)

3. **다중 API 통합**
   - OpenWeatherMap API
   - 공공 데이터 포털 API
   - 지역 좌표 변환 API
   - 대기질 정보 API

4. **부가 기능**
   - 날씨 알림 설정
   - 데이터 캐싱
   - 오프라인 모드
   - 다국어 지원

## 주요 학습 포인트
- `requests` 라이브러리 활용
- API 응답 상태 코드 처리
- JSON 파싱과 데이터 추출
- 환경 변수로 API 키 관리
- Rate Limiting 대응

## 코드 구조
```
weather_client/
    api/
        __init__.py
        base_client.py       # 기본 API 클라이언트
        weather_api.py       # 날씨 API 래퍼
        geocoding_api.py     # 지오코딩 API
        air_quality_api.py   # 대기질 API
    models/
        weather.py           # 날씨 데이터 모델
        location.py          # 위치 데이터 모델
        forecast.py          # 예보 데이터 모델
    services/
        weather_service.py   # 비즈니스 로직
        cache_service.py     # 캐싱 로직
        notification.py      # 알림 서비스
    utils/
        config.py           # 설정 관리
        validators.py       # 입력 검증
        formatters.py       # 데이터 포맷팅
    visualization/
        charts.py           # 차트 생성
        maps.py             # 지도 생성
main.py                    # 메인 프로그램
.env.example              # 환경 변수 예제
```

## API 사용 예제
```python
class WeatherAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def get_current_weather(self, city: str) -> dict:
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        response = requests.get(f"{self.base_url}/weather", params=params)
        response.raise_for_status()
        return response.json()
```

## 실행 방법
```bash
# 환경 변수 설정
export WEATHER_API_KEY="your_api_key"

# 현재 날씨 조회
python main.py --city Seoul

# 5일 예보
python main.py --city Seoul --forecast

# 시각화 포함
python main.py --city Seoul --visualize
```

## 환경 설정 (.env)
```
OPENWEATHER_API_KEY=your_key_here
GOOGLE_MAPS_API_KEY=your_key_here
CACHE_EXPIRY_MINUTES=30
DEFAULT_LANGUAGE=ko
```