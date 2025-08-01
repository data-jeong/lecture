#!/usr/bin/env python3
"""
비동기 파일 처리기 CLI
GIL, 비동기, 스레드, 프로세스 처리 방식 비교 및 실행
"""

import asyncio
import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional
import json

from core.gil_demo import GILDemo
from core.async_processor import AsyncProcessor
from core.thread_processor import ThreadProcessor
from core.process_processor import ProcessProcessor
from utils.monitoring import Monitor, PerformanceTracker
from patterns.rate_limiter import AsyncRateLimiter
from patterns.batch_processor import AsyncBatchProcessor
from examples.web_scraper import WebScraperExample
from examples.image_processor import ImageProcessorExample
from examples.log_analyzer import LogAnalyzerExample


class FileProcessorCLI:
    """파일 처리기 CLI"""
    
    def __init__(self):
        self.monitor = Monitor()
        self.tracker = PerformanceTracker()
    
    def run_gil_demo(self, args):
        """GIL 데모 실행"""
        print("🔍 GIL (Global Interpreter Lock) 데모")
        print("=" * 60)
        
        demo = GILDemo(task_size=args.task_size)
        
        # 모니터링 시작
        if args.monitor:
            self.monitor.start()
        
        # 각 방식 테스트
        results = []
        
        with self.tracker.track("GIL Demo - Single Thread"):
            result = demo.benchmark_single_thread()
            results.append(("단일 스레드", result))
        
        with self.tracker.track("GIL Demo - Multi Thread"):
            result = demo.benchmark_multi_thread()
            results.append(("멀티 스레드", result))
        
        with self.tracker.track("GIL Demo - Multi Process"):
            result = demo.benchmark_multi_process()
            results.append(("멀티 프로세스", result))
        
        with self.tracker.track("GIL Demo - Async"):
            result = demo.benchmark_async()
            results.append(("비동기", result))
        
        # 결과 출력
        print("\n📊 벤치마크 결과:")
        print("-" * 50)
        for name, result in results:
            print(f"\n{name}:")
            print(f"  실행 시간: {result.execution_time:.4f}초")
            print(f"  CPU 사용률: {result.cpu_usage:.1f}%")
            print(f"  작업 유형: {result.task_type}")
        
        # 모니터링 결과
        if args.monitor:
            self.monitor.stop()
            self.monitor.print_summary()
        
        # 성능 리포트
        self.tracker.print_report()
        
        if args.save_report:
            self.tracker.save_report("gil_demo_report.json")
            if args.monitor:
                self.monitor.save_history("gil_demo_monitor.json")
    
    async def run_async_processor(self, args):
        """비동기 처리기 실행"""
        print("⚡ 비동기 파일 처리기")
        print("=" * 60)
        
        processor = AsyncProcessor(
            max_concurrent=args.max_concurrent,
            timeout=args.timeout
        )
        
        # 파일 목록 가져오기
        files = self._get_files(args.path, args.pattern)
        if not files:
            print("처리할 파일이 없습니다.")
            return
        
        print(f"처리할 파일: {len(files)}개")
        
        # 처리 함수 선택
        if args.process_type == "count":
            process_func = lambda content: len(content.split())
        elif args.process_type == "lines":
            process_func = lambda content: len(content.splitlines())
        else:
            process_func = lambda content: len(content)
        
        # 배치 처리 설정
        if args.batch_size:
            batch_processor = AsyncBatchProcessor(
                batch_size=args.batch_size,
                max_concurrent_batches=3
            )
            
            # 배치 처리 함수
            async def batch_func(file_batch):
                results = []
                for file_path in file_batch:
                    result = await processor.process_file(str(file_path), process_func)
                    results.append(result)
                return results
            
            # 배치 처리 실행
            batch_results = await batch_processor.add_many(files, batch_func)
            
            # 결과 평탄화
            results = []
            for batch_result in batch_results:
                if batch_result.results:
                    results.extend(batch_result.results)
        else:
            # 일반 처리
            results = await processor.process_files(
                [str(f) for f in files],
                process_func
            )
        
        # 결과 출력
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        print(f"\n✅ 성공: {len(successful)}개")
        print(f"❌ 실패: {len(failed)}개")
        
        if failed and args.verbose:
            print("\n실패한 파일:")
            for result in failed:
                print(f"  - {result.file_path}: {result.error}")
        
        # 통계
        if successful:
            total_time = sum(r.processing_time for r in successful)
            avg_time = total_time / len(successful)
            print(f"\n평균 처리 시간: {avg_time:.4f}초/파일")
    
    def run_thread_processor(self, args):
        """스레드 처리기 실행"""
        print("🧵 스레드 기반 파일 처리기")
        print("=" * 60)
        
        processor = ThreadProcessor(max_workers=args.max_workers)
        
        # 파일 목록
        files = self._get_files(args.path, args.pattern)
        if not files:
            print("처리할 파일이 없습니다.")
            return
        
        print(f"처리할 파일: {len(files)}개 (워커: {args.max_workers}개)")
        
        # 처리 함수
        def process_func(content):
            # CPU 집약적 작업 시뮬레이션
            import hashlib
            for _ in range(100):
                hashlib.sha256(content.encode()).hexdigest()
            return len(content)
        
        # 처리 실행
        start_time = time.time()
        results = processor.process_files([str(f) for f in files], process_func)
        duration = time.time() - start_time
        
        # 결과 출력
        successful = sum(1 for r in results if r.success)
        print(f"\n✅ 성공: {successful}/{len(results)}개")
        print(f"⏱️  총 시간: {duration:.2f}초")
        
        # 통계
        stats = processor.get_statistics()
        print("\n📊 통계:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    def run_process_processor(self, args):
        """프로세스 처리기 실행"""
        print("🔧 프로세스 기반 파일 처리기")
        print("=" * 60)
        
        processor = ProcessProcessor(max_workers=args.max_workers)
        
        # 파일 목록
        files = self._get_files(args.path, args.pattern)
        if not files:
            print("처리할 파일이 없습니다.")
            return
        
        print(f"처리할 파일: {len(files)}개 (프로세스: {args.max_workers}개)")
        
        # 처리 실행
        start_time = time.time()
        results = processor.process_files_parallel([str(f) for f in files])
        duration = time.time() - start_time
        
        # 결과 출력
        successful = sum(1 for r in results if r["success"])
        print(f"\n✅ 성공: {successful}/{len(results)}개")
        print(f"⏱️  총 시간: {duration:.2f}초")
    
    async def run_examples(self, args):
        """예제 실행"""
        print("📚 예제 실행")
        print("=" * 60)
        
        if args.example == "web":
            example = WebScraperExample()
            await example.run()
        
        elif args.example == "image":
            example = ImageProcessorExample()
            await example.run()
        
        elif args.example == "log":
            example = LogAnalyzerExample()
            await example.run()
        
        elif args.example == "all":
            print("\n1. 웹 스크래퍼 예제")
            web_example = WebScraperExample()
            await web_example.run()
            
            print("\n\n2. 이미지 처리 예제")
            image_example = ImageProcessorExample()
            await image_example.run()
            
            print("\n\n3. 로그 분석 예제")
            log_example = LogAnalyzerExample()
            await log_example.run()
    
    def _get_files(self, path: str, pattern: str) -> List[Path]:
        """파일 목록 가져오기"""
        path = Path(path)
        
        if path.is_file():
            return [path]
        elif path.is_dir():
            return list(path.glob(pattern))
        else:
            return []
    
    def main(self):
        """메인 실행"""
        parser = argparse.ArgumentParser(
            description="비동기 파일 처리기 - GIL, 비동기, 스레드, 프로세스 비교"
        )
        
        subparsers = parser.add_subparsers(dest="command", help="실행할 명령")
        
        # GIL 데모
        gil_parser = subparsers.add_parser("gil-demo", help="GIL 데모 실행")
        gil_parser.add_argument("--task-size", type=int, default=1000000,
                              help="작업 크기")
        gil_parser.add_argument("--monitor", action="store_true",
                              help="리소스 모니터링")
        gil_parser.add_argument("--save-report", action="store_true",
                              help="리포트 저장")
        
        # 비동기 처리
        async_parser = subparsers.add_parser("async", help="비동기 처리")
        async_parser.add_argument("path", help="파일 또는 디렉토리 경로")
        async_parser.add_argument("--pattern", default="*.txt",
                                help="파일 패턴")
        async_parser.add_argument("--max-concurrent", type=int, default=10,
                                help="최대 동시 실행 수")
        async_parser.add_argument("--timeout", type=float, default=30.0,
                                help="타임아웃 (초)")
        async_parser.add_argument("--process-type", 
                                choices=["size", "count", "lines"],
                                default="size",
                                help="처리 유형")
        async_parser.add_argument("--batch-size", type=int,
                                help="배치 크기")
        async_parser.add_argument("--verbose", action="store_true",
                                help="상세 출력")
        
        # 스레드 처리
        thread_parser = subparsers.add_parser("thread", help="스레드 처리")
        thread_parser.add_argument("path", help="파일 또는 디렉토리 경로")
        thread_parser.add_argument("--pattern", default="*.txt",
                                 help="파일 패턴")
        thread_parser.add_argument("--max-workers", type=int, default=4,
                                 help="최대 워커 수")
        
        # 프로세스 처리
        process_parser = subparsers.add_parser("process", help="프로세스 처리")
        process_parser.add_argument("path", help="파일 또는 디렉토리 경로")
        process_parser.add_argument("--pattern", default="*.txt",
                                  help="파일 패턴")
        process_parser.add_argument("--max-workers", type=int, default=4,
                                  help="최대 프로세스 수")
        
        # 예제
        example_parser = subparsers.add_parser("example", help="예제 실행")
        example_parser.add_argument("example",
                                  choices=["web", "image", "log", "all"],
                                  help="실행할 예제")
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        # 명령 실행
        if args.command == "gil-demo":
            self.run_gil_demo(args)
        
        elif args.command == "async":
            asyncio.run(self.run_async_processor(args))
        
        elif args.command == "thread":
            self.run_thread_processor(args)
        
        elif args.command == "process":
            self.run_process_processor(args)
        
        elif args.command == "example":
            asyncio.run(self.run_examples(args))


if __name__ == "__main__":
    cli = FileProcessorCLI()
    cli.main()