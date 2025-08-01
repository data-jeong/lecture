# 프로젝트 5: 비동기 파일 처리기 (GIL & Async)

Python의 GIL(Global Interpreter Lock)을 이해하고, 비동기 프로그래밍, 멀티스레딩, 멀티프로세싱을 활용한 고성능 파일 처리기입니다.

## 🎯 학습 목표

- Python GIL의 이해와 영향
- 비동기 프로그래밍 (asyncio)
- 멀티스레딩 vs 멀티프로세싱
- CPU 집약적 vs I/O 집약적 작업
- 고급 비동기 패턴 (생산자-소비자, 속도 제한, 배치 처리)

## 📁 프로젝트 구조

```
05_gil_async/
├── async_file_processor/
│   ├── __init__.py
│   ├── core/               # 핵심 처리 모듈
│   │   ├── __init__.py
│   │   ├── gil_demo.py     # GIL 시연
│   │   ├── async_processor.py    # 비동기 처리기
│   │   ├── thread_processor.py   # 스레드 처리기
│   │   └── process_processor.py  # 프로세스 처리기
│   ├── utils/              # 유틸리티 모듈
│   │   ├── __init__.py
│   │   ├── file_utils.py   # 파일 유틸리티
│   │   ├── benchmark.py    # 성능 측정
│   │   └── monitoring.py   # 리소스 모니터링
│   ├── patterns/           # 비동기 패턴
│   │   ├── __init__.py
│   │   ├── producer_consumer.py  # 생산자-소비자
│   │   ├── rate_limiter.py      # 속도 제한
│   │   └── batch_processor.py   # 배치 처리
│   ├── examples/           # 예제 모듈
│   │   ├── __init__.py
│   │   ├── web_scraper.py       # 웹 스크래핑
│   │   ├── image_processor.py   # 이미지 처리
│   │   └── log_analyzer.py      # 로그 분석
│   ├── main.py            # CLI 인터페이스
│   └── examples.py        # 예제 모음
├── tests/
│   ├── __init__.py
│   ├── test_gil_demo.py
│   ├── test_async_processor.py
│   └── test_patterns.py
├── requirements.txt
└── README.md
```

## 🚀 시작하기

### 설치
```bash
cd 05_gil_async
pip install -r requirements.txt
```

### 실행 예제

#### 1. GIL 데모
```bash
# GIL의 영향 비교
python -m async_file_processor.main gil-demo --monitor

# 큰 작업으로 테스트
python -m async_file_processor.main gil-demo --task-size 5000000 --save-report
```

#### 2. 비동기 파일 처리
```bash
# 디렉토리의 모든 텍스트 파일 처리
python -m async_file_processor.main async ./data --pattern "*.txt"

# 배치 처리
python -m async_file_processor.main async ./data --batch-size 10 --verbose
```

#### 3. 예제 실행
```bash
# 모든 예제 실행
python -m async_file_processor.examples

# 개별 예제
python -m async_file_processor.main example web    # 웹 스크래핑
python -m async_file_processor.main example image  # 이미지 처리
python -m async_file_processor.main example log    # 로그 분석
```

## 📚 주요 개념

### 1. GIL (Global Interpreter Lock)
```python
# CPU 집약적 작업 - GIL의 영향을 받음
def cpu_bound_task(n):
    return sum(i ** 2 for i in range(n))

# I/O 집약적 작업 - GIL 해제
async def io_bound_task():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

### 2. 비동기 프로그래밍
```python
# 비동기 파일 처리
async def process_file(file_path):
    async with aiofiles.open(file_path) as f:
        content = await f.read()
        return process(content)

# 동시 실행
results = await asyncio.gather(*[process_file(f) for f in files])
```

### 3. 비동기 패턴

#### 생산자-소비자 패턴
```python
pc = AsyncProducerConsumer(max_queue_size=100, num_consumers=5)
results = await pc.run(
    source=data_generator(),
    processor=process_data
)
```

#### 속도 제한
```python
@rate_limiter(rate=10, per=1.0)  # 10 requests/second
async def api_call(url):
    return await fetch(url)
```

#### 배치 처리
```python
batch_processor = AsyncBatchProcessor(batch_size=100)
results = await batch_processor.add_many(items, process_batch)
```

## 🔍 핵심 기능

### 1. GIL 시연
- 단일 스레드 vs 멀티 스레드 vs 멀티 프로세스 vs 비동기
- CPU 집약적 작업과 I/O 집약적 작업 비교
- 실시간 성능 모니터링

### 2. 고급 비동기 처리
- 세마포어를 이용한 동시성 제어
- 타임아웃 처리
- 에러 복구 및 재시도
- 스트림 처리

### 3. 실용적인 예제
- **웹 스크래핑**: 속도 제한, 재귀적 크롤링
- **이미지 처리**: CPU 집약적 작업의 병렬화
- **로그 분석**: 대용량 파일의 스트림 처리

## 📊 성능 비교

### CPU 집약적 작업
```
단일 스레드:    10.5초 (기준)
멀티 스레드:    10.8초 (GIL로 인해 개선 없음)
멀티 프로세스:   3.2초  (3.3x 빠름)
비동기:          10.4초 (CPU 작업에는 부적합)
```

### I/O 집약적 작업
```
단일 스레드:    20.1초 (기준)
멀티 스레드:    4.2초  (4.8x 빠름)
멀티 프로세스:   4.5초  (오버헤드 존재)
비동기:          2.1초  (9.6x 빠름!)
```

## 🧪 테스트

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 실행
pytest tests/test_gil_demo.py -v

# 커버리지 확인
pytest --cov=async_file_processor
```

## 💡 학습 포인트

1. **GIL 이해**: Python의 GIL이 멀티스레딩에 미치는 영향
2. **작업 유형 구분**: CPU vs I/O 집약적 작업의 최적 처리 방법
3. **비동기 패턴**: 실전에서 사용하는 고급 비동기 패턴
4. **성능 최적화**: 작업 특성에 맞는 처리 방식 선택

## 🎓 다음 단계

- 프로젝트 6: 웹 스크래핑 (Selenium, Scrapy, requests)
- 프로젝트 7: API 기초 (날씨 API 클라이언트)
- 프로젝트 8: 데이터베이스 (학생 성적 관리)