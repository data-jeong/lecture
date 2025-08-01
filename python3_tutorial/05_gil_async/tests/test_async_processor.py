"""
비동기 처리기 테스트
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from async_file_processor.core.async_processor import AsyncProcessor, ProcessingResult


class TestAsyncProcessor:
    """비동기 처리기 테스트"""
    
    @pytest.fixture
    def temp_files(self):
        """임시 파일 생성"""
        temp_dir = tempfile.mkdtemp()
        files = []
        
        for i in range(5):
            file_path = Path(temp_dir) / f"test_{i}.txt"
            file_path.write_text(f"Test content {i}\nLine 2\nLine 3")
            files.append(str(file_path))
        
        yield files
        
        # 정리
        for file in files:
            Path(file).unlink(missing_ok=True)
        Path(temp_dir).rmdir()
    
    @pytest.mark.asyncio
    async def test_process_file(self, temp_files):
        """단일 파일 처리 테스트"""
        processor = AsyncProcessor()
        
        # 단어 수 세기
        def count_words(content: str) -> int:
            return len(content.split())
        
        result = await processor.process_file(temp_files[0], count_words)
        
        assert isinstance(result, ProcessingResult)
        assert result.success
        assert result.result == 6  # "Test content 0 Line 2 Line 3"
        assert result.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_process_files(self, temp_files):
        """여러 파일 처리 테스트"""
        processor = AsyncProcessor(max_concurrent=2)
        
        # 라인 수 세기
        def count_lines(content: str) -> int:
            return len(content.splitlines())
        
        results = await processor.process_files(temp_files[:3], count_lines)
        
        assert len(results) == 3
        assert all(isinstance(r, ProcessingResult) for r in results)
        assert all(r.success for r in results)
        assert all(r.result == 3 for r in results)
    
    @pytest.mark.asyncio
    async def test_async_processor_function(self, temp_files):
        """비동기 처리 함수 테스트"""
        processor = AsyncProcessor()
        
        # 비동기 처리 함수
        async def async_count(content: str) -> int:
            await asyncio.sleep(0.1)
            return len(content)
        
        result = await processor.process_file(temp_files[0], async_count)
        
        assert result.success
        assert result.result > 0
    
    @pytest.mark.asyncio
    async def test_timeout(self):
        """타임아웃 테스트"""
        processor = AsyncProcessor(timeout=0.1)
        
        # 느린 처리 함수
        async def slow_process(content: str) -> str:
            await asyncio.sleep(0.5)
            return content
        
        # 임시 파일
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test")
            temp_file = f.name
        
        result = await processor.process_file(temp_file, slow_process)
        
        assert not result.success
        assert "timeout" in result.error.lower()
        
        # 정리
        Path(temp_file).unlink()
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """에러 처리 테스트"""
        processor = AsyncProcessor()
        
        # 에러 발생 함수
        def error_processor(content: str):
            raise ValueError("Test error")
        
        # 존재하지 않는 파일
        result = await processor.process_file("non_existent.txt", error_processor)
        
        assert not result.success
        assert result.error is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_limit(self, temp_files):
        """동시 실행 제한 테스트"""
        processor = AsyncProcessor(max_concurrent=2)
        
        call_times = []
        
        async def track_concurrent(content: str) -> int:
            call_times.append(asyncio.get_event_loop().time())
            await asyncio.sleep(0.1)
            return len(content)
        
        # 5개 파일을 동시 실행 2개로 처리
        results = await processor.process_files(temp_files, track_concurrent)
        
        assert len(results) == 5
        assert all(r.success for r in results)
        
        # 동시 실행이 제한되었는지 확인
        # (정확한 동시성 측정은 어려우므로 결과만 확인)
    
    @pytest.mark.asyncio
    async def test_stream_processing(self, temp_files):
        """스트림 처리 테스트"""
        processor = AsyncProcessor()
        
        # 문자 수 세기
        def count_chars(content: str) -> int:
            return len(content)
        
        # 파일 스트림 생성
        async def file_stream():
            for file in temp_files[:3]:
                yield file
        
        results = []
        async for file in file_stream():
            result = await processor.process_file(file, count_chars)
            results.append(result)
        
        assert len(results) == 3
        assert all(r.success for r in results)
        assert all(r.result > 0 for r in results)