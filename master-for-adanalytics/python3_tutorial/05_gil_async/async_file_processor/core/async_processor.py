"""
비동기 파일 처리기
asyncio를 활용한 효율적인 파일 처리
"""

import asyncio
import aiofiles
import aiohttp
from pathlib import Path
from typing import List, Dict, Optional, Callable, AsyncIterator, Any
from dataclasses import dataclass
import time
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor


@dataclass
class ProcessingResult:
    """처리 결과"""
    file_path: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    duration: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "success": self.success,
            "result": str(self.result) if self.result else None,
            "error": self.error,
            "duration": self.duration
        }


class AsyncProcessor:
    """비동기 파일 처리기"""
    
    def __init__(self, max_workers: int = 10, chunk_size: int = 8192):
        self.max_workers = max_workers
        self.chunk_size = chunk_size
        self.semaphore = asyncio.Semaphore(max_workers)
        self.results: List[ProcessingResult] = []
        self._process_pool = None
    
    async def __aenter__(self):
        """컨텍스트 매니저 진입"""
        self._process_pool = ProcessPoolExecutor(max_workers=4)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        if self._process_pool:
            self._process_pool.shutdown(wait=True)
    
    async def read_file_async(self, file_path: str) -> str:
        """비동기 파일 읽기"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        return content
    
    async def write_file_async(self, file_path: str, content: str) -> None:
        """비동기 파일 쓰기"""
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(content)
    
    async def stream_file(self, file_path: str) -> AsyncIterator[bytes]:
        """파일 스트리밍"""
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(self.chunk_size):
                yield chunk
    
    async def process_file(
        self, 
        file_path: str, 
        processor: Callable[[str], Any]
    ) -> ProcessingResult:
        """단일 파일 처리"""
        start_time = time.perf_counter()
        
        try:
            async with self.semaphore:
                # 파일 읽기
                content = await self.read_file_async(file_path)
                
                # CPU 집약적 작업은 프로세스 풀에서 실행
                if self._process_pool:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self._process_pool, 
                        processor, 
                        content
                    )
                else:
                    result = processor(content)
                
                duration = time.perf_counter() - start_time
                
                return ProcessingResult(
                    file_path=file_path,
                    success=True,
                    result=result,
                    duration=duration
                )
                
        except Exception as e:
            duration = time.perf_counter() - start_time
            return ProcessingResult(
                file_path=file_path,
                success=False,
                error=str(e),
                duration=duration
            )
    
    async def process_directory(
        self,
        directory: str,
        pattern: str = "*",
        processor: Callable[[str], Any] = None,
        recursive: bool = True
    ) -> List[ProcessingResult]:
        """디렉토리 내 파일들 처리"""
        path = Path(directory)
        
        if recursive:
            files = list(path.rglob(pattern))
        else:
            files = list(path.glob(pattern))
        
        print(f"📁 {len(files)}개 파일 발견")
        
        # 기본 처리기: 파일 크기와 해시
        if processor is None:
            processor = self._default_processor
        
        # 비동기 처리
        tasks = []
        for file_path in files:
            if file_path.is_file():
                task = self.process_file(str(file_path), processor)
                tasks.append(task)
        
        # 진행 상황 표시하며 처리
        results = []
        for i, coro in enumerate(asyncio.as_completed(tasks), 1):
            result = await coro
            results.append(result)
            
            # 진행 상황 출력
            success_count = sum(1 for r in results if r.success)
            print(f"\r진행: {i}/{len(tasks)} | 성공: {success_count} | "
                  f"실패: {i - success_count}", end='')
        
        print()  # 줄바꿈
        self.results.extend(results)
        return results
    
    def _default_processor(self, content: str) -> dict:
        """기본 처리기: 파일 정보 추출"""
        return {
            "size": len(content),
            "lines": content.count('\n'),
            "words": len(content.split()),
            "hash": hashlib.md5(content.encode()).hexdigest()
        }
    
    async def batch_process(
        self,
        items: List[Any],
        processor: Callable[[List[Any]], Any],
        batch_size: int = 100
    ) -> List[Any]:
        """배치 처리"""
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            async with self.semaphore:
                if self._process_pool:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self._process_pool,
                        processor,
                        batch
                    )
                else:
                    result = processor(batch)
                
                results.extend(result)
        
        return results
    
    async def download_files(
        self,
        urls: List[str],
        output_dir: str,
        headers: Optional[dict] = None
    ) -> List[ProcessingResult]:
        """여러 파일 동시 다운로드"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = []
            for url in urls:
                task = self._download_file(session, url, output_path)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 변환
            processed_results = []
            for url, result in zip(urls, results):
                if isinstance(result, Exception):
                    processed_results.append(
                        ProcessingResult(
                            file_path=url,
                            success=False,
                            error=str(result)
                        )
                    )
                else:
                    processed_results.append(result)
            
            return processed_results
    
    async def _download_file(
        self,
        session: aiohttp.ClientSession,
        url: str,
        output_dir: Path
    ) -> ProcessingResult:
        """단일 파일 다운로드"""
        start_time = time.perf_counter()
        
        try:
            async with self.semaphore:
                async with session.get(url) as response:
                    response.raise_for_status()
                    
                    # 파일명 추출
                    filename = url.split('/')[-1] or 'download'
                    file_path = output_dir / filename
                    
                    # 스트리밍 다운로드
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(self.chunk_size):
                            await f.write(chunk)
                    
                    duration = time.perf_counter() - start_time
                    
                    return ProcessingResult(
                        file_path=str(file_path),
                        success=True,
                        result={"size": response.headers.get('Content-Length', 'unknown')},
                        duration=duration
                    )
                    
        except Exception as e:
            duration = time.perf_counter() - start_time
            return ProcessingResult(
                file_path=url,
                success=False,
                error=str(e),
                duration=duration
            )
    
    async def parallel_map(
        self,
        func: Callable[[Any], Any],
        items: List[Any]
    ) -> List[Any]:
        """병렬 map 연산"""
        async def wrapped_func(item):
            async with self.semaphore:
                if asyncio.iscoroutinefunction(func):
                    return await func(item)
                else:
                    # 동기 함수는 executor에서 실행
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, func, item)
        
        tasks = [wrapped_func(item) for item in items]
        return await asyncio.gather(*tasks)
    
    def get_statistics(self) -> dict:
        """처리 통계"""
        if not self.results:
            return {"message": "No results available"}
        
        success_count = sum(1 for r in self.results if r.success)
        failed_count = len(self.results) - success_count
        total_duration = sum(r.duration for r in self.results)
        
        return {
            "total_files": len(self.results),
            "successful": success_count,
            "failed": failed_count,
            "total_duration": f"{total_duration:.2f}s",
            "average_duration": f"{total_duration / len(self.results):.2f}s",
            "throughput": f"{len(self.results) / total_duration:.2f} files/s"
        }
    
    def save_results(self, output_file: str = "processing_results.json"):
        """결과 저장"""
        data = {
            "statistics": self.get_statistics(),
            "results": [r.to_dict() for r in self.results]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 결과가 {output_file}에 저장되었습니다.")


async def example_usage():
    """사용 예제"""
    print("🚀 비동기 파일 처리기 예제")
    print("=" * 60)
    
    # 텍스트 처리 함수
    def count_words(content: str) -> dict:
        words = content.split()
        return {
            "word_count": len(words),
            "unique_words": len(set(words)),
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0
        }
    
    async with AsyncProcessor(max_workers=5) as processor:
        # 1. 디렉토리 처리
        print("\n1. 디렉토리 내 텍스트 파일 처리:")
        results = await processor.process_directory(
            directory=".",
            pattern="*.py",
            processor=count_words,
            recursive=False
        )
        
        # 2. 통계 출력
        print("\n📊 처리 통계:")
        stats = processor.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # 3. URL 다운로드 (예제)
        print("\n2. 파일 다운로드 예제:")
        urls = [
            "https://raw.githubusercontent.com/python/cpython/main/README.rst",
            "https://raw.githubusercontent.com/python/cpython/main/LICENSE"
        ]
        
        download_results = await processor.download_files(
            urls=urls,
            output_dir="./downloads"
        )
        
        for result in download_results:
            status = "✅" if result.success else "❌"
            print(f"{status} {result.file_path}")


if __name__ == "__main__":
    # 예제 실행
    asyncio.run(example_usage())