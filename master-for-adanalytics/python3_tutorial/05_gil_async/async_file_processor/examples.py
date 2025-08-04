#!/usr/bin/env python3
"""
비동기 파일 처리기 예제 모음
다양한 사용 사례와 패턴 시연
"""

import asyncio
import time
from pathlib import Path
import random
import string

from core.gil_demo import GILDemo
from core.async_processor import AsyncProcessor
from core.thread_processor import ThreadProcessor
from core.process_processor import ProcessProcessor
from patterns.rate_limiter import AsyncRateLimiter
from patterns.batch_processor import AsyncBatchProcessor
from patterns.producer_consumer import AsyncProducerConsumer
from utils.monitoring import Monitor, PerformanceTracker
from examples.web_scraper import WebScraperExample
from examples.image_processor import ImageProcessorExample
from examples.log_analyzer import LogAnalyzerExample


async def example_gil_comparison():
    """GIL 비교 예제"""
    print("🔍 GIL (Global Interpreter Lock) 비교")
    print("=" * 60)
    
    demo = GILDemo(task_size=1000000)
    
    # CPU 집약적 작업
    print("\n1. CPU 집약적 작업")
    results = []
    
    result = demo.benchmark_single_thread()
    results.append(("단일 스레드", result))
    print(f"  단일 스레드: {result.execution_time:.4f}초")
    
    result = demo.benchmark_multi_thread()
    results.append(("멀티 스레드", result))
    print(f"  멀티 스레드: {result.execution_time:.4f}초")
    
    result = demo.benchmark_multi_process()
    results.append(("멀티 프로세스", result))
    print(f"  멀티 프로세스: {result.execution_time:.4f}초")
    
    # I/O 집약적 작업
    print("\n2. I/O 집약적 작업")
    
    result = demo.benchmark_async()
    results.append(("비동기", result))
    print(f"  비동기: {result.execution_time:.4f}초")
    
    # 요약
    print("\n📊 요약:")
    fastest = min(results, key=lambda x: x[1].execution_time)
    print(f"  가장 빠른 방식: {fastest[0]} ({fastest[1].execution_time:.4f}초)")


async def example_async_file_processing():
    """비동기 파일 처리 예제"""
    print("\n\n⚡ 비동기 파일 처리")
    print("=" * 60)
    
    # 샘플 파일 생성
    sample_dir = Path("sample_files")
    sample_dir.mkdir(exist_ok=True)
    
    print("📝 샘플 파일 생성 중...")
    for i in range(10):
        file_path = sample_dir / f"file_{i+1}.txt"
        content = ''.join(random.choices(string.ascii_letters + string.digits, k=1000))
        file_path.write_text(content)
    
    # 비동기 처리
    processor = AsyncProcessor(max_concurrent=5)
    
    # 단어 수 세기
    async def count_words(content: str) -> int:
        await asyncio.sleep(0.1)  # I/O 시뮬레이션
        return len(content.split())
    
    # 파일 처리
    files = list(sample_dir.glob("*.txt"))
    start_time = time.time()
    
    results = await processor.process_files(
        [str(f) for f in files],
        count_words
    )
    
    duration = time.time() - start_time
    
    # 결과 출력
    successful = [r for r in results if r.success]
    total_words = sum(r.result for r in successful if r.result)
    
    print(f"\n✅ 처리 완료:")
    print(f"  파일 수: {len(files)}개")
    print(f"  총 단어 수: {total_words}")
    print(f"  처리 시간: {duration:.2f}초")
    print(f"  평균: {duration/len(files):.3f}초/파일")


async def example_rate_limited_api():
    """속도 제한 API 호출 예제"""
    print("\n\n🚦 속도 제한 API 호출")
    print("=" * 60)
    
    # 속도 제한기 (3 requests/second)
    rate_limiter = AsyncRateLimiter(rate=3, per=1.0)
    
    # API 호출 시뮬레이션
    @rate_limiter
    async def api_call(endpoint: str) -> dict:
        print(f"  → 호출: {endpoint}")
        await asyncio.sleep(0.1)  # API 응답 시뮬레이션
        return {"endpoint": endpoint, "status": "success"}
    
    # 10개 요청
    print("10개 API 호출 (3/초 제한):")
    start_time = time.time()
    
    tasks = [api_call(f"/api/v1/resource/{i}") for i in range(10)]
    results = await asyncio.gather(*tasks)
    
    duration = time.time() - start_time
    print(f"\n✅ 완료: {duration:.2f}초 (예상: ~3.3초)")


async def example_batch_processing():
    """배치 처리 예제"""
    print("\n\n📦 배치 처리")
    print("=" * 60)
    
    # 데이터 생성
    data = list(range(100))
    
    # 배치 처리 함수
    async def process_batch(items: list) -> list:
        print(f"  → 배치 처리: {len(items)}개 아이템")
        await asyncio.sleep(0.2)  # 처리 시뮬레이션
        return [item ** 2 for item in items]
    
    # 배치 처리기
    batch_processor = AsyncBatchProcessor(
        batch_size=20,
        max_concurrent_batches=3
    )
    
    # 처리 실행
    print("100개 아이템을 20개씩 배치 처리:")
    start_time = time.time()
    
    results = await batch_processor.add_many(data, process_batch)
    
    duration = time.time() - start_time
    print(f"\n✅ 완료:")
    print(f"  배치 수: {len(results)}")
    print(f"  처리 시간: {duration:.2f}초")


async def example_producer_consumer():
    """생산자-소비자 패턴 예제"""
    print("\n\n🔄 생산자-소비자 패턴")
    print("=" * 60)
    
    # 데이터 생성기
    async def data_generator():
        for i in range(20):
            await asyncio.sleep(0.05)  # 생산 속도
            yield f"Data-{i+1}"
            print(f"  📤 생산: Data-{i+1}")
    
    # 처리 함수
    async def process_data(data: str) -> str:
        await asyncio.sleep(0.1)  # 처리 시간
        result = f"Processed-{data}"
        print(f"  ✅ 소비: {data} → {result}")
        return result
    
    # 생산자-소비자 실행
    pc = AsyncProducerConsumer(
        max_queue_size=5,
        num_consumers=3
    )
    
    print("생산자 1개, 소비자 3개로 처리:")
    results = await pc.run(
        source=data_generator(),
        processor=process_data
    )
    
    print(f"\n✅ 처리 완료: {len(results)}개")
    
    # 통계
    stats = pc.get_statistics()
    print("\n📊 통계:")
    for key, value in stats.items():
        print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")


async def example_monitoring():
    """모니터링 예제"""
    print("\n\n📊 성능 모니터링")
    print("=" * 60)
    
    monitor = Monitor()
    tracker = PerformanceTracker()
    
    # 모니터링 시작
    monitor.start()
    
    # 다양한 작업 실행
    print("다양한 작업 실행 중...")
    
    # 1. CPU 작업
    with tracker.track("CPU Task"):
        result = sum(i ** 2 for i in range(1000000))
    
    # 2. I/O 작업
    async with tracker.track_async("I/O Task"):
        await asyncio.sleep(0.5)
    
    # 3. 메모리 작업
    with tracker.track("Memory Task"):
        data = [i for i in range(100000)]
    
    # 모니터링 중지
    monitor.stop()
    
    # 결과 출력
    print("\n✅ 작업 완료")
    
    monitor.print_summary()
    tracker.print_report()


async def main():
    """메인 함수"""
    print("🚀 비동기 파일 처리기 예제 모음")
    print("=" * 80)
    
    # 1. GIL 비교
    await example_gil_comparison()
    
    # 2. 비동기 파일 처리
    await example_async_file_processing()
    
    # 3. 속도 제한 API
    await example_rate_limited_api()
    
    # 4. 배치 처리
    await example_batch_processing()
    
    # 5. 생산자-소비자
    await example_producer_consumer()
    
    # 6. 모니터링
    await example_monitoring()
    
    print("\n\n✨ 모든 예제 완료!")
    print("\n💡 더 많은 예제:")
    print("  - python main.py example web    # 웹 스크래핑")
    print("  - python main.py example image  # 이미지 처리")
    print("  - python main.py example log    # 로그 분석")


if __name__ == "__main__":
    asyncio.run(main())