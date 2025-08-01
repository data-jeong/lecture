"""
프로세스 기반 파일 처리기
multiprocessing을 활용한 진정한 병렬 처리
"""

import multiprocessing as mp
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any, Tuple
from dataclasses import dataclass
import time
import hashlib
import json
import pickle
import os
from functools import partial


@dataclass
class ProcessResult:
    """프로세스 처리 결과"""
    process_id: int
    file_path: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    duration: float = 0.0


def process_file_worker(args: Tuple[str, bytes]) -> ProcessResult:
    """워커 프로세스에서 실행될 함수"""
    file_path, processor_bytes = args
    process_id = os.getpid()
    start_time = time.perf_counter()
    
    try:
        # 프로세서 역직렬화
        processor = pickle.loads(processor_bytes)
        
        # 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 처리
        result = processor(content)
        
        duration = time.perf_counter() - start_time
        
        return ProcessResult(
            process_id=process_id,
            file_path=file_path,
            success=True,
            result=result,
            duration=duration
        )
        
    except Exception as e:
        duration = time.perf_counter() - start_time
        return ProcessResult(
            process_id=process_id,
            file_path=file_path,
            success=False,
            error=str(e),
            duration=duration
        )


class ProcessProcessor:
    """프로세스 기반 파일 처리기"""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or mp.cpu_count()
        self.results: List[ProcessResult] = []
        self.manager = mp.Manager()
    
    def process_directory_pool(
        self,
        directory: str,
        pattern: str = "*",
        processor: Callable[[str], Any] = None,
        recursive: bool = True,
        chunksize: int = 1
    ) -> List[ProcessResult]:
        """프로세스 풀을 사용한 디렉토리 처리"""
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
        
        # 프로세서 직렬화
        processor_bytes = pickle.dumps(processor)
        
        # 작업 준비
        tasks = [(str(f), processor_bytes) for f in files]
        
        results = []
        
        # 프로세스 풀 사용
        with mp.Pool(processes=self.max_workers) as pool:
            # 진행 상황 표시를 위한 비동기 처리
            async_results = pool.map_async(
                process_file_worker, 
                tasks, 
                chunksize=chunksize
            )
            
            # 진행 상황 모니터링
            while not async_results.ready():
                time.sleep(0.1)
            
            results = async_results.get()
        
        self.results.extend(results)
        
        # 결과 요약
        success_count = sum(1 for r in results if r.success)
        print(f"\n✅ 완료: {success_count}/{len(results)} 성공")
        
        return results
    
    def process_directory_executor(
        self,
        directory: str,
        pattern: str = "*",
        processor: Callable[[str], Any] = None,
        recursive: bool = True
    ) -> List[ProcessResult]:
        """ProcessPoolExecutor를 사용한 디렉토리 처리"""
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
        
        # 프로세서 직렬화
        processor_bytes = pickle.dumps(processor)
        
        results = []
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # 작업 제출
            futures = {
                executor.submit(process_file_worker, (str(f), processor_bytes)): f
                for f in files
            }
            
            # 완료된 작업 처리
            completed = 0
            for future in concurrent.futures.as_completed(futures):
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
    
    def parallel_map(
        self,
        func: Callable[[Any], Any],
        items: List[Any],
        chunksize: int = 1
    ) -> List[Any]:
        """프로세스 기반 병렬 map"""
        with mp.Pool(processes=self.max_workers) as pool:
            return pool.map(func, items, chunksize=chunksize)
    
    def parallel_starmap(
        self,
        func: Callable[..., Any],
        items: List[Tuple],
        chunksize: int = 1
    ) -> List[Any]:
        """프로세스 기반 병렬 starmap (여러 인자)"""
        with mp.Pool(processes=self.max_workers) as pool:
            return pool.starmap(func, items, chunksize=chunksize)
    
    def producer_consumer_pattern(
        self,
        producer_func: Callable[[], Any],
        consumer_func: Callable[[Any], Any],
        num_consumers: int = None,
        max_queue_size: int = 100
    ) -> List[Any]:
        """프로세스 기반 생산자-소비자 패턴"""
        if num_consumers is None:
            num_consumers = self.max_workers
        
        # 공유 큐
        task_queue = self.manager.Queue(maxsize=max_queue_size)
        result_queue = self.manager.Queue()
        
        def producer_process():
            """생산자 프로세스"""
            try:
                while True:
                    item = producer_func()
                    if item is None:
                        break
                    task_queue.put(item)
            finally:
                # 종료 신호
                for _ in range(num_consumers):
                    task_queue.put(None)
        
        def consumer_process():
            """소비자 프로세스"""
            while True:
                try:
                    item = task_queue.get(timeout=1)
                    if item is None:
                        break
                    
                    result = consumer_func(item)
                    result_queue.put(result)
                except Exception as e:
                    result_queue.put({"error": str(e)})
        
        # 프로세스 시작
        producer = mp.Process(target=producer_process)
        consumers = [
            mp.Process(target=consumer_process)
            for _ in range(num_consumers)
        ]
        
        producer.start()
        for c in consumers:
            c.start()
        
        # 완료 대기
        producer.join()
        for c in consumers:
            c.join()
        
        # 결과 수집
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        
        return results
    
    def map_reduce(
        self,
        map_func: Callable[[Any], Any],
        reduce_func: Callable[[Any, Any], Any],
        items: List[Any],
        initial_value: Any = None
    ) -> Any:
        """맵-리듀스 패턴"""
        # Map 단계
        with mp.Pool(processes=self.max_workers) as pool:
            mapped_results = pool.map(map_func, items)
        
        # Reduce 단계
        if initial_value is not None:
            result = initial_value
        else:
            result = mapped_results[0]
            mapped_results = mapped_results[1:]
        
        for item in mapped_results:
            result = reduce_func(result, item)
        
        return result
    
    def batch_process(
        self,
        items: List[Any],
        processor: Callable[[List[Any]], Any],
        batch_size: int = 100
    ) -> List[Any]:
        """배치 처리"""
        batches = [
            items[i:i + batch_size]
            for i in range(0, len(items), batch_size)
        ]
        
        with mp.Pool(processes=self.max_workers) as pool:
            batch_results = pool.map(processor, batches)
        
        # 결과 평탄화
        results = []
        for batch_result in batch_results:
            if isinstance(batch_result, list):
                results.extend(batch_result)
            else:
                results.append(batch_result)
        
        return results
    
    def get_statistics(self) -> dict:
        """처리 통계"""
        if not self.results:
            return {"message": "No results available"}
        
        success_count = sum(1 for r in self.results if r.success)
        failed_count = len(self.results) - success_count
        total_duration = sum(r.duration for r in self.results)
        
        # 프로세스별 통계
        process_stats = {}
        for result in self.results:
            pid = result.process_id
            if pid not in process_stats:
                process_stats[pid] = {"count": 0, "duration": 0}
            process_stats[pid]["count"] += 1
            process_stats[pid]["duration"] += result.duration
        
        return {
            "total_files": len(self.results),
            "successful": success_count,
            "failed": failed_count,
            "total_duration": f"{total_duration:.2f}s",
            "average_duration": f"{total_duration / len(self.results):.2f}s",
            "throughput": f"{len(self.results) / total_duration:.2f} files/s",
            "processes_used": len(process_stats),
            "max_workers": self.max_workers,
            "process_statistics": process_stats
        }
    
    def save_results(self, output_file: str = "process_results.json"):
        """결과 저장"""
        data = {
            "statistics": self.get_statistics(),
            "results": [
                {
                    "process_id": r.process_id,
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


def cpu_intensive_processor(content: str) -> dict:
    """CPU 집약적 처리 예제"""
    # 해시 계산 (CPU 집약적)
    hash_md5 = hashlib.md5(content.encode()).hexdigest()
    hash_sha256 = hashlib.sha256(content.encode()).hexdigest()
    
    # 단어 빈도 계산
    words = content.lower().split()
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # 가장 빈번한 단어 10개
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "size": len(content),
        "lines": content.count('\n'),
        "words": len(words),
        "unique_words": len(word_freq),
        "hash_md5": hash_md5,
        "hash_sha256": hash_sha256,
        "top_words": top_words
    }


def example_usage():
    """사용 예제"""
    print("🚀 프로세스 기반 파일 처리기 예제")
    print("=" * 60)
    
    processor = ProcessProcessor(max_workers=4)
    
    # 1. 프로세스 풀 방식
    print(f"\n1. ProcessPool 방식 (워커: {processor.max_workers}):")
    results = processor.process_directory_pool(
        directory=".",
        pattern="*.py",
        processor=cpu_intensive_processor,
        recursive=False,
        chunksize=2
    )
    
    # 2. 통계 출력
    print("\n📊 처리 통계:")
    stats = processor.get_statistics()
    for key, value in stats.items():
        if key != "process_statistics":
            print(f"  {key}: {value}")
    
    # 3. 맵-리듀스 예제
    print("\n2. 맵-리듀스 예제:")
    
    # 숫자 리스트의 제곱 합 계산
    numbers = list(range(1, 101))
    
    def square(x):
        return x ** 2
    
    def add(x, y):
        return x + y
    
    result = processor.map_reduce(
        map_func=square,
        reduce_func=add,
        items=numbers,
        initial_value=0
    )
    
    print(f"1부터 100까지의 제곱 합: {result}")
    
    # 4. 결과 저장
    processor.save_results()


if __name__ == "__main__":
    # Windows에서 필요
    mp.freeze_support()
    example_usage()