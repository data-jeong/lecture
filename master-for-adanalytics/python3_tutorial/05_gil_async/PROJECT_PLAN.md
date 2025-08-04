# 05. GIL과 비동기 프로그래밍 - 비동기 파일 처리기

## 프로젝트 개요
Python의 GIL(Global Interpreter Lock)을 이해하고 비동기 프로그래밍으로 효율적인 파일 처리 시스템을 구축합니다.

## 학습 목표
- GIL의 작동 원리와 한계 이해
- async/await 문법 마스터
- asyncio 라이브러리 활용
- 동시성(Concurrency) vs 병렬성(Parallelism)
- Python 3.12+ GIL 개선사항 이해

## 프로젝트 기능
1. **비동기 파일 처리**
   - 여러 파일 동시 읽기/쓰기
   - 대용량 파일 청크 단위 처리
   - 실시간 진행률 표시
   - 비동기 파일 압축/해제

2. **성능 비교**
   - 동기 vs 비동기 처리 시간 측정
   - CPU 바운드 vs I/O 바운드 작업 비교
   - threading vs asyncio vs multiprocessing
   - GIL 영향도 분석

3. **고급 비동기 패턴**
   - 비동기 컨텍스트 매니저
   - 비동기 제너레이터
   - 세마포어와 락
   - 태스크 그룹과 취소

4. **실시간 모니터링**
   - 작업 큐 상태
   - 메모리 사용량
   - 처리 속도 차트
   - 에러 로깅

## 주요 학습 포인트
```python
import asyncio
import aiofiles
import aiohttp
from asyncio import Task, Queue, Semaphore
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
import threading
```

## 코드 구조
```
async_processor/
    core/
        __init__.py
        file_processor.py    # 비동기 파일 처리
        monitor.py          # 실시간 모니터링
        benchmarks.py       # 성능 테스트
    handlers/
        text_handler.py     # 텍스트 파일 처리
        image_handler.py    # 이미지 파일 처리
        csv_handler.py      # CSV 파일 처리
    utils/
        progress.py         # 진행률 표시
        async_helpers.py    # 비동기 유틸리티
    comparison/
        sync_version.py     # 동기 버전
        thread_version.py   # 스레드 버전
        process_version.py  # 프로세스 버전
main.py                    # 메인 프로그램
```

## GIL 이해하기
```python
# GIL이 문제가 되는 경우 (CPU 바운드)
def cpu_bound_task():
    result = sum(i * i for i in range(10_000_000))
    
# GIL이 문제가 되지 않는 경우 (I/O 바운드)
async def io_bound_task():
    async with aiofiles.open('large_file.txt', 'r') as f:
        content = await f.read()
```

## 실행 방법
```bash
# 비동기 파일 처리
python main.py --mode async --files *.txt

# 성능 비교 실행
python main.py --benchmark

# 실시간 모니터링
python main.py --monitor
```

## Python 3.12+ GIL 개선사항
- Per-Interpreter GIL
- 서브인터프리터 활용
- 향상된 멀티스레딩 성능
- nogil 빌드 옵션