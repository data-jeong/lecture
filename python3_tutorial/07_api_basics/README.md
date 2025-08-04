# Weather API Client

RESTful API를 활용한 날씨 정보 조회 애플리케이션

## 프로젝트 구조

```
07_api_basics/
├── weather_client/
│   ├── api/              # API 클라이언트
│   ├── models/           # 데이터 모델
│   ├── services/         # 비즈니스 로직
│   ├── utils/            # 유틸리티 함수
│   └── visualization/    # 데이터 시각화
├── tests/                # 테스트 코드
├── main.py              # 메인 실행 파일
└── requirements.txt     # 의존성 패키지
```

## 설치 방법

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 OpenWeatherMap API 키 입력
```

## API 키 발급

1. [OpenWeatherMap](https://openweathermap.org/api) 가입
2. API Keys 메뉴에서 키 생성
3. `.env` 파일에 키 입력

## 사용 방법

### 현재 날씨 조회
```bash
python main.py --city Seoul
```

### 5일 예보
```bash
python main.py --city Seoul --forecast
```

### 시간별 예보
```bash
python main.py --city Seoul --hourly 24
```

### 도시 비교
```bash
python main.py --compare Seoul Tokyo "New York"
```

### 시각화
```bash
python main.py --city Seoul --visualize
```

### 날씨 지도
```bash
python main.py --city Seoul --map
```

## 예제 실행

```bash
python -m weather_client.examples
```

## 주요 기능

- 🌡️ 현재 날씨 정보 조회
- 📅 5일 일기예보
- ⏰ 시간별 예보
- 🗺️ 날씨 지도 생성
- 📊 데이터 시각화
- 💨 대기질 정보
- 🔔 날씨 알림 설정
- 💾 데이터 캐싱

## 테스트

```bash
pytest tests/ -v
```

## 학습 포인트

- REST API 원칙 이해
- HTTP 메서드 활용
- JSON 데이터 처리
- API 인증 방식
- 에러 처리와 재시도 로직
- 데이터 캐싱 전략
- 비동기 처리