"""
스레드 기반 파일 처리기
threading과 concurrent.futures를 활용한 파일 처리
"""

import threading
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass
import time
import queue
import hashlib
from threading import Lock, Event
import json


@dataclass 
class ThreadResult:
    """스레드 처리 결과"""
    thread_id: int
    file_path: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    duration: float = 0.0


class ThreadProcessor:
    """스레드 기반 파일 처리기"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.results: List[ThreadResult] = []
        self.results_lock = Lock()
        self.task_queue = queue.Queue()
        self.stop_event = Event()
        self.active_threads = 0
        self.active_threads_lock = Lock()
    
    def process_file(self, file_path: str, processor: Callable[[str], Any]) -> ThreadResult:
        """단일 파일 처리"""
        thread_id = threading.get_ident()
        start_time = time.perf_counter()
        
        try:
            # 파일 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 처리
            result = processor(content)
            
            duration = time.perf_counter() - start_time
            
            return ThreadResult(
                thread_id=thread_id,
                file_path=file_path,
                success=True,
                result=result,
                duration=duration
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            return ThreadResult(
                thread_id=thread_id,
                file_path=file_path,
                success=False,
                error=str(e),
                duration=duration
            )
    
    def worker(self, processor: Callable[[str], Any]):
        """워커 스레드"""
        with self.active_threads_lock:
            self.active_threads += 1
        
        try:
            while not self.stop_event.is_set():
                try:
                    file_path = self.task_queue.get(timeout=0.1)
                    
                    # 파일 처리
                    result = self.process_file(file_path, processor)
                    
                    # 결과 저장
                    with self.results_lock:
                        self.results.append(result)
                    
                    self.task_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Worker error: {e}")
                    
        finally:
            with self.active_threads_lock:
                self.active_threads -= 1
    
    def process_directory_threaded(
        self,
        directory: str,
        pattern: str = "*",
        processor: Callable[[str], Any] = None,
        recursive: bool = True
    ) -> List[ThreadResult]:
        """스레드를 사용한 디렉토리 처리"""
        path = Path(directory)
        
        if recursive:
            files = list(path.rglob(pattern))
        else:
            files = list(path.glob(pattern))
        
        # 파일만 필터링
        files = [f for f in files if f.is_file()]
        print(f"📁 {len(files)}개 파일 발견")
        
        if processor is None:
            processor = self._default_processor
        
        # 작업 큐에 파일 추가
        for file_path in files:
            self.task_queue.put(str(file_path))
        
        # 워커 스레드 시작
        threads = []
        for i in range(min(self.max_workers, len(files))):
            t = threading.Thread(target=self.worker, args=(processor,))
            t.start()
            threads.append(t)
        
        # 진행 상황 모니터링
        total_files = len(files)
        while not self.task_queue.empty() or self.active_threads > 0:
            processed = len(self.results)
            remaining = self.task_queue.qsize()
            
            print(f"\r진행: {processed}/{total_files} | "
                  f"대기: {remaining} | "
                  f"활성 스레드: {self.active_threads}", end='')
            
            time.sleep(0.1)
        
        # 스레드 종료
        self.stop_event.set()
        for t in threads:
            t.join()
        
        print()  # 줄바꿈
        return self.results
    
    def process_directory_pool(
        self,
        directory: str,
        pattern: str = "*",
        processor: Callable[[str], Any] = None,
        recursive: bool = True
    ) -> List[ThreadResult]:
        """ThreadPoolExecutor를 사용한 디렉토리 처리"""
        path = Path(directory)
        
        if recursive:
            files = list(path.rglob(pattern))
        else:
            files = list(path.glob(pattern))
        
        # 파일만 필터링
        files = [f for f in files if f.is_file()]
        print(f"📁 {len(files)}개 파일 발견")
        
        if processor is None:
            processor = self._default_processor
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 작업 제출
            future_to_file = {
                executor.submit(self.process_file, str(f), processor): f
                for f in files
            }
            
            # 완료된 작업 처리
            completed = 0
            for future in concurrent.futures.as_completed(future_to_file):
                completed += 1
                result = future.result()
                results.append(result)
                
                # 진행 상황 출력
                success_count = sum(1 for r in results if r.success)
                print(f"\r진행: {completed}/{len(files)} | "
                      f"성공: {success_count} | "
                      f"실패: {completed - success_count}", end='')
        
        print()  # 줄바꿈
        self.results.extend(results)
        return results
    
    def _default_processor(self, content: str) -> dict:
        """기본 처리기"""
        return {
            "size": len(content),
            "lines": content.count('\n'),
            "words": len(content.split()),
            "hash": hashlib.md5(content.encode()).hexdigest()
        }
    
    def parallel_map_threaded(
        self,
        func: Callable[[Any], Any],
        items: List[Any]
    ) -> List[Any]:
        """스레드 기반 병렬 map"""
        results = [None] * len(items)
        results_lock = Lock()
        
        def process_item(index: int, item: Any):
            result = func(item)
            with results_lock:
                results[index] = result
        
        threads = []
        for i, item in enumerate(items):
            t = threading.Thread(target=process_item, args=(i, item))
            t.start()
            threads.append(t)
            
            # 동시 스레드 수 제한
            if len(threads) >= self.max_workers:
                threads[0].join()
                threads.pop(0)
        
        # 남은 스레드 대기
        for t in threads:
            t.join()
        
        return results
    
    def parallel_map_pool(
        self,
        func: Callable[[Any], Any],
        items: List[Any],
        chunksize: int = 1
    ) -> List[Any]:
        """ThreadPoolExecutor 기반 병렬 map"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(func, items, chunksize=chunksize))
    
    def producer_consumer_pattern(
        self,
        producer_func: Callable[[], Any],
        consumer_func: Callable[[Any], Any],
        num_consumers: int = 5,
        max_queue_size: int = 100
    ) -> List[Any]:
        """생산자-소비자 패턴"""
        work_queue = queue.Queue(maxsize=max_queue_size)
        results_queue = queue.Queue()
        stop_event = Event()
        
        def producer():
            """생산자 스레드"""
            try:
                while not stop_event.is_set():
                    item = producer_func()
                    if item is None:
                        break
                    work_queue.put(item)
            finally:
                # 종료 신호
                for _ in range(num_consumers):
                    work_queue.put(None)
        
        def consumer():
            """소비자 스레드"""
            while True:
                item = work_queue.get()
                if item is None:
                    break
                
                try:
                    result = consumer_func(item)
                    results_queue.put(result)
                except Exception as e:
                    results_queue.put({"error": str(e)})
                finally:
                    work_queue.task_done()
        
        # 스레드 시작
        producer_thread = threading.Thread(target=producer)
        consumer_threads = [
            threading.Thread(target=consumer)
            for _ in range(num_consumers)
        ]
        
        producer_thread.start()
        for t in consumer_threads:
            t.start()
        
        # 완료 대기
        producer_thread.join()
        for t in consumer_threads:
            t.join()
        
        # 결과 수집
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        return results
    
    def get_statistics(self) -> dict:
        """처리 통계"""
        if not self.results:
            return {"message": "No results available"}
        
        success_count = sum(1 for r in self.results if r.success)
        failed_count = len(self.results) - success_count
        total_duration = sum(r.duration for r in self.results)
        
        # 스레드별 통계
        thread_stats = {}
        for result in self.results:
            tid = result.thread_id
            if tid not in thread_stats:
                thread_stats[tid] = {"count": 0, "duration": 0}
            thread_stats[tid]["count"] += 1
            thread_stats[tid]["duration"] += result.duration
        
        return {
            "total_files": len(self.results),
            "successful": success_count,
            "failed": failed_count,
            "total_duration": f"{total_duration:.2f}s",
            "average_duration": f"{total_duration / len(self.results):.2f}s",
            "throughput": f"{len(self.results) / total_duration:.2f} files/s",
            "threads_used": len(thread_stats),
            "thread_statistics": thread_stats
        }
    
    def save_results(self, output_file: str = "thread_results.json"):
        """결과 저장"""
        data = {
            "statistics": self.get_statistics(),
            "results": [
                {
                    "thread_id": r.thread_id,
                    "file_path": r.file_path,
                    "success": r.success,
                    "result": str(r.result) if r.result else None,
                    "error": r.error,
                    "duration": r.duration
                }
                for r in self.results
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 결과가 {output_file}에 저장되었습니다.")


def example_usage():
    """사용 예제"""
    print("🧵 스레드 기반 파일 처리기 예제")
    print("=" * 60)
    
    # 단어 수 계산 함수
    def count_words(content: str) -> dict:
        words = content.split()
        return {
            "word_count": len(words),
            "unique_words": len(set(words)),
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0
        }
    
    processor = ThreadProcessor(max_workers=5)
    
    # 1. 스레드 풀 방식
    print("\n1. ThreadPoolExecutor 방식:")
    results = processor.process_directory_pool(
        directory=".",
        pattern="*.py",
        processor=count_words,
        recursive=False
    )
    
    # 2. 통계 출력
    print("\n📊 처리 통계:")
    stats = processor.get_statistics()
    for key, value in stats.items():
        if key != "thread_statistics":
            print(f"  {key}: {value}")
    
    # 3. 생산자-소비자 패턴 예제
    print("\n2. 생산자-소비자 패턴:")
    
    counter = [0]
    def producer():
        if counter[0] < 10:
            counter[0] += 1
            return f"Item {counter[0]}"
        return None
    
    def consumer(item):
        time.sleep(0.1)  # 처리 시뮬레이션
        return f"Processed: {item}"
    
    results = processor.producer_consumer_pattern(
        producer_func=producer,
        consumer_func=consumer,
        num_consumers=3
    )
    
    print(f"처리된 아이템: {len(results)}개")


if __name__ == "__main__":
    example_usage()