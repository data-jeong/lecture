# 05. GIL & Async - 비동기 파일 처리기

## 📖 프로젝트 개요

이 프로젝트에서는 Python의 GIL(Global Interpreter Lock)을 이해하고, 비동기 프로그래밍을 활용하여 효율적인 파일 처리 시스템을 구축합니다. asyncio, threading, multiprocessing을 비교하며 각각의 장단점을 실습합니다.

## 🎯 학습 목표

1. **GIL 이해**: Python GIL의 동작 원리와 영향
2. **비동기 프로그래밍**: async/await 패턴 마스터
3. **동시성 vs 병렬성**: threading과 multiprocessing 비교
4. **asyncio 심화**: 태스크, 큐, 세마포어 등
5. **파일 I/O 최적화**: 비동기 파일 처리
6. **성능 측정**: 벤치마킹과 프로파일링
7. **실전 패턴**: 실무에서 사용하는 비동기 패턴

## 🏗️ 프로젝트 구조

```
05_gil_async/
├── async_file_processor/
│   ├── __init__.py
│   ├── main.py                    # CLI 메인 애플리케이션
│   ├── core/                      # 핵심 기능
│   │   ├── __init__.py
│   │   ├── gil_demo.py           # GIL 데모
│   │   ├── async_processor.py    # 비동기 처리기
│   │   ├── thread_processor.py   # 스레드 처리기
│   │   └── process_processor.py  # 프로세스 처리기
│   ├── utils/                     # 유틸리티
│   │   ├── __init__.py
│   │   ├── file_utils.py         # 파일 유틸리티
│   │   ├── benchmark.py          # 벤치마킹
│   │   └── monitoring.py         # 모니터링
│   ├── patterns/                  # 비동기 패턴
│   │   ├── __init__.py
│   │   ├── producer_consumer.py  # 생산자-소비자
│   │   ├── rate_limiter.py       # 속도 제한
│   │   └── batch_processor.py    # 배치 처리
│   └── examples/                  # 예제
│       ├── __init__.py
│       ├── web_scraper.py        # 비동기 웹 스크래퍼
│       ├── image_processor.py    # 이미지 처리
│       └── log_analyzer.py       # 로그 분석
├── tests/                         # 테스트
│   ├── __init__.py
│   ├── test_gil.py
│   ├── test_async.py
│   └── test_performance.py
├── benchmarks/                    # 벤치마크 결과
│   └── results.json
├── step_by_step.md               # 이 파일
├── examples.py                    # 사용 예제
└── README.md                      # 프로젝트 설명
```

## 🔍 주요 기능

### 1. GIL 이해하기

#### GIL이란?
```python
import threading
import time

# CPU 집약적 작업
def cpu_bound_task(n):
    """CPU를 많이 사용하는 작업"""
    result = 0
    for i in range(n):
        result += i ** 2
    return result

# I/O 집약적 작업
async def io_bound_task(url):
    """I/O를 많이 사용하는 작업"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

#### GIL의 영향 측정
```python
import time
import threading
import multiprocessing

def measure_gil_impact():
    """GIL의 영향 측정"""
    # 단일 스레드
    start = time.time()
    cpu_bound_task(10_000_000)
    cpu_bound_task(10_000_000)
    single_thread_time = time.time() - start
    
    # 멀티 스레드 (GIL 때문에 느림)
    start = time.time()
    t1 = threading.Thread(target=cpu_bound_task, args=(10_000_000,))
    t2 = threading.Thread(target=cpu_bound_task, args=(10_000_000,))
    t1.start(); t2.start()
    t1.join(); t2.join()
    multi_thread_time = time.time() - start
    
    # 멀티 프로세스 (진정한 병렬 처리)
    start = time.time()
    with multiprocessing.Pool(2) as pool:
        pool.map(cpu_bound_task, [10_000_000, 10_000_000])
    multi_process_time = time.time() - start
    
    print(f"단일 스레드: {single_thread_time:.2f}초")
    print(f"멀티 스레드: {multi_thread_time:.2f}초")
    print(f"멀티 프로세스: {multi_process_time:.2f}초")
```

### 2. 비동기 프로그래밍 기초

#### async/await 패턴
```python
import asyncio
import aiofiles

async def read_file_async(filename: str) -> str:
    """비동기 파일 읽기"""
    async with aiofiles.open(filename, 'r') as f:
        content = await f.read()
    return content

async def process_files(filenames: List[str]) -> List[str]:
    """여러 파일 동시 처리"""
    tasks = [read_file_async(f) for f in filenames]
    results = await asyncio.gather(*tasks)
    return results
```

#### 비동기 컨텍스트 매니저
```python
class AsyncFileProcessor:
    """비동기 파일 처리기"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.file = None
    
    async def __aenter__(self):
        self.file = await aiofiles.open(self.filename, 'r')
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.file.close()
    
    async def process_lines(self):
        """라인별 처리"""
        async for line in self.file:
            yield line.strip()
```

### 3. 고급 비동기 패턴

#### 생산자-소비자 패턴
```python
import asyncio
from typing import AsyncIterator

class AsyncProducerConsumer:
    """비동기 생산자-소비자 패턴"""
    
    def __init__(self, max_queue_size: int = 100):
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.running = True
    
    async def producer(self, items: AsyncIterator[any]):
        """아이템 생산"""
        async for item in items:
            await self.queue.put(item)
        await self.queue.put(None)  # 종료 신호
    
    async def consumer(self, process_func):
        """아이템 소비"""
        while True:
            item = await self.queue.get()
            if item is None:
                break
            
            result = await process_func(item)
            self.queue.task_done()
            yield result
    
    async def run(self, items: AsyncIterator[any], process_func, num_workers: int = 5):
        """생산자-소비자 실행"""
        # 생산자 시작
        producer_task = asyncio.create_task(self.producer(items))
        
        # 소비자 워커들
        consumers = []
        for _ in range(num_workers):
            consumer = self.consumer(process_func)
            consumers.append(consumer)
        
        # 모든 결과 수집
        async for result in asyncio.as_completed(consumers):
            yield result
```

#### 속도 제한 (Rate Limiting)
```python
class AsyncRateLimiter:
    """비동기 속도 제한기"""
    
    def __init__(self, rate: int, per: float):
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = asyncio.get_event_loop().time()
    
    async def acquire(self):
        """허가 획득"""
        current = asyncio.get_event_loop().time()
        time_passed = current - self.last_check
        self.last_check = current
        
        self.allowance += time_passed * (self.rate / self.per)
        if self.allowance > self.rate:
            self.allowance = self.rate
        
        if self.allowance < 1.0:
            sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
            await asyncio.sleep(sleep_time)
            self.allowance = 0.0
        else:
            self.allowance -= 1.0
```

### 4. 파일 처리 최적화

#### 병렬 파일 처리
```python
class ParallelFileProcessor:
    """병렬 파일 처리기"""
    
    def __init__(self, max_workers: int = 10):
        self.semaphore = asyncio.Semaphore(max_workers)
    
    async def process_file(self, filepath: str, processor):
        """단일 파일 처리"""
        async with self.semaphore:
            async with aiofiles.open(filepath, 'r') as f:
                content = await f.read()
            
            result = await processor(content)
            return filepath, result
    
    async def process_directory(self, directory: str, pattern: str, processor):
        """디렉토리 전체 처리"""
        import pathlib
        
        files = list(pathlib.Path(directory).glob(pattern))
        tasks = [self.process_file(str(f), processor) for f in files]
        
        results = {}
        for coro in asyncio.as_completed(tasks):
            filepath, result = await coro
            results[filepath] = result
            print(f"처리 완료: {filepath}")
        
        return results
```

#### 스트리밍 처리
```python
async def stream_large_file(filepath: str, chunk_size: int = 8192):
    """대용량 파일 스트리밍"""
    async with aiofiles.open(filepath, 'rb') as f:
        while chunk := await f.read(chunk_size):
            yield chunk

async def process_stream(filepath: str, processor):
    """스트림 처리"""
    total_processed = 0
    
    async for chunk in stream_large_file(filepath):
        processed = await processor(chunk)
        total_processed += len(processed)
        
        # 진행 상황 업데이트
        print(f"\r처리중: {total_processed:,} bytes", end='')
    
    print(f"\n완료: {total_processed:,} bytes")
```

### 5. 성능 비교 및 모니터링

#### 벤치마킹
```python
import time
import asyncio
from functools import wraps

def async_benchmark(func):
    """비동기 함수 벤치마킹 데코레이터"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        
        print(f"{func.__name__} 실행 시간: {end - start:.4f}초")
        return result
    
    return wrapper

class PerformanceMonitor:
    """성능 모니터"""
    
    def __init__(self):
        self.metrics = {}
    
    async def measure(self, name: str, coro):
        """코루틴 실행 시간 측정"""
        start = time.perf_counter()
        try:
            result = await coro
            elapsed = time.perf_counter() - start
            
            if name not in self.metrics:
                self.metrics[name] = []
            self.metrics[name].append(elapsed)
            
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start
            print(f"{name} 실패 ({elapsed:.4f}초): {e}")
            raise
    
    def report(self):
        """성능 리포트"""
        for name, times in self.metrics.items():
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"\n{name}:")
            print(f"  평균: {avg_time:.4f}초")
            print(f"  최소: {min_time:.4f}초")
            print(f"  최대: {max_time:.4f}초")
```

## 🚀 실행 방법

### 1. 기본 실행
```bash
cd 05_gil_async
python -m async_file_processor.main --help
```

### 2. GIL 데모
```bash
# GIL 영향 측정
python -m async_file_processor.main gil-demo

# CPU vs I/O 바운드 비교
python -m async_file_processor.main compare --task-type cpu
python -m async_file_processor.main compare --task-type io
```

### 3. 파일 처리
```bash
# 비동기 파일 처리
python -m async_file_processor.main process --pattern "*.txt" --workers 10

# 이미지 일괄 처리
python -m async_file_processor.main images --input-dir ./images --output-dir ./processed

# 로그 분석
python -m async_file_processor.main analyze-logs --log-dir ./logs --pattern "*.log"
```

### 4. 벤치마킹
```bash
# 성능 비교
python -m async_file_processor.main benchmark --mode all

# 특정 모드만 테스트
python -m async_file_processor.main benchmark --mode async
python -m async_file_processor.main benchmark --mode thread
python -m async_file_processor.main benchmark --mode process
```

## 🧪 테스트 실행

```bash
# 모든 테스트
python -m pytest tests/ -v

# 특정 테스트
python -m pytest tests/test_async.py -v

# 성능 테스트
python -m pytest tests/test_performance.py -v --benchmark
```

## 💡 실전 예제

### 1. 웹 스크래핑
```python
async def scrape_urls(urls: List[str]) -> Dict[str, str]:
    """여러 URL 동시 스크래핑"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = fetch_url(session, url)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            url: result if not isinstance(result, Exception) else str(result)
            for url, result in zip(urls, results)
        }
```

### 2. 이미지 처리
```python
async def process_images_parallel(image_dir: str):
    """이미지 병렬 처리"""
    from PIL import Image
    
    async def resize_image(filepath: str):
        loop = asyncio.get_event_loop()
        
        # CPU 집약적 작업은 executor에서 실행
        def _resize():
            with Image.open(filepath) as img:
                resized = img.resize((800, 600))
                output_path = filepath.replace('.jpg', '_resized.jpg')
                resized.save(output_path)
                return output_path
        
        return await loop.run_in_executor(None, _resize)
    
    # 모든 이미지 파일 찾기
    import glob
    images = glob.glob(f"{image_dir}/*.jpg")
    
    # 병렬 처리
    tasks = [resize_image(img) for img in images]
    results = await asyncio.gather(*tasks)
    
    print(f"{len(results)}개 이미지 처리 완료")
```

### 3. 실시간 로그 모니터링
```python
async def monitor_log_file(filepath: str):
    """실시간 로그 파일 모니터링"""
    async with aiofiles.open(filepath, 'r') as f:
        # 파일 끝으로 이동
        await f.seek(0, 2)
        
        while True:
            line = await f.readline()
            if line:
                # 로그 라인 처리
                if 'ERROR' in line:
                    print(f"🚨 에러 감지: {line.strip()}")
                elif 'WARNING' in line:
                    print(f"⚠️ 경고: {line.strip()}")
            else:
                # 새 데이터 대기
                await asyncio.sleep(0.1)
```

## 🔧 확장 아이디어

1. **분산 처리**: Redis/RabbitMQ와 연동
2. **모니터링 대시보드**: 실시간 성능 모니터링
3. **자동 스케일링**: 부하에 따른 워커 조정
4. **에러 복구**: 실패한 작업 재시도
5. **캐싱**: 결과 캐싱으로 성능 향상
6. **프로파일링**: 병목 지점 찾기

## 📚 학습 포인트

### GIL의 이해
1. **CPU 바운드**: multiprocessing 사용
2. **I/O 바운드**: asyncio 사용
3. **혼합 작업**: 적절한 조합 필요

### 비동기 프로그래밍
1. **이벤트 루프**: 단일 스레드에서 동시성
2. **코루틴**: 일시 중단 가능한 함수
3. **태스크**: 독립적으로 실행되는 코루틴
4. **동시성 제어**: 세마포어, 락, 큐

### 성능 최적화
1. **프로파일링**: 병목 지점 찾기
2. **벤치마킹**: 정확한 성능 측정
3. **리소스 관리**: 메모리와 CPU 사용량
4. **스케일링**: 수평/수직 확장

이 프로젝트를 통해 Python의 동시성과 병렬성을 깊이 이해하고, 실전에서 활용할 수 있는 비동기 프로그래밍 능력을 기를 수 있습니다.