"""
이미지 처리 예제
CPU 집약적 작업의 병렬 처리
"""

import asyncio
import time
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

from ..core.process_processor import ProcessProcessor
from ..patterns.batch_processor import BatchProcessor, AsyncBatchProcessor
from ..utils.monitoring import Monitor, PerformanceTracker


@dataclass
class ImageProcessingResult:
    """이미지 처리 결과"""
    source_path: str
    output_path: str
    original_size: Tuple[int, int]
    processed_size: Tuple[int, int]
    processing_time: float
    operations: List[str]
    success: bool = True
    error: Optional[str] = None


class ImageProcessorExample:
    """이미지 처리 예제"""
    
    def __init__(self):
        self.tracker = PerformanceTracker()
        self.monitor = Monitor()
    
    @staticmethod
    def create_sample_images(output_dir: Path, count: int = 10) -> List[Path]:
        """샘플 이미지 생성"""
        output_dir.mkdir(exist_ok=True)
        image_paths = []
        
        print(f"📸 {count}개 샘플 이미지 생성 중...")
        
        for i in range(count):
            # 랜덤 패턴 이미지 생성
            size = (800, 600)
            
            # 그라디언트 + 노이즈 이미지
            img_array = np.zeros((*size[::-1], 3), dtype=np.uint8)
            
            # 그라디언트
            for y in range(size[1]):
                for x in range(size[0]):
                    img_array[y, x] = [
                        int(255 * x / size[0]),  # R
                        int(255 * y / size[1]),  # G
                        int(255 * (1 - x / size[0]) * (1 - y / size[1]))  # B
                    ]
            
            # 노이즈 추가
            noise = np.random.randint(-30, 30, img_array.shape)
            img_array = np.clip(img_array.astype(int) + noise, 0, 255).astype(np.uint8)
            
            # PIL 이미지로 변환
            img = Image.fromarray(img_array)
            
            # 텍스트 추가
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), f"Sample Image {i+1}", fill=(255, 255, 255))
            
            # 저장
            path = output_dir / f"sample_{i+1:03d}.png"
            img.save(path)
            image_paths.append(path)
        
        print(f"✅ 샘플 이미지 생성 완료: {output_dir}")
        return image_paths
    
    @staticmethod
    def process_image_single(image_path: str, output_dir: str) -> ImageProcessingResult:
        """단일 이미지 처리 (프로세스에서 실행)"""
        start_time = time.time()
        operations = []
        
        try:
            # 이미지 열기
            img = Image.open(image_path)
            original_size = img.size
            operations.append("load")
            
            # 1. 리사이즈
            new_size = (original_size[0] // 2, original_size[1] // 2)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            operations.append("resize")
            
            # 2. 필터 적용
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
            operations.append("gaussian_blur")
            
            img = img.filter(ImageFilter.SHARPEN)
            operations.append("sharpen")
            
            # 3. 색상 조정
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)
            operations.append("contrast_enhance")
            
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.9)
            operations.append("brightness_adjust")
            
            # 4. 회전
            img = img.rotate(5, expand=True, fillcolor='white')
            operations.append("rotate")
            
            # 5. 그레이스케일 변환
            img = img.convert('L')
            operations.append("grayscale")
            
            # 6. 엣지 검출
            img = img.filter(ImageFilter.FIND_EDGES)
            operations.append("edge_detection")
            
            # 저장
            output_path = Path(output_dir) / f"processed_{Path(image_path).name}"
            img.save(output_path)
            operations.append("save")
            
            processing_time = time.time() - start_time
            
            return ImageProcessingResult(
                source_path=image_path,
                output_path=str(output_path),
                original_size=original_size,
                processed_size=img.size,
                processing_time=processing_time,
                operations=operations
            )
        
        except Exception as e:
            return ImageProcessingResult(
                source_path=image_path,
                output_path="",
                original_size=(0, 0),
                processed_size=(0, 0),
                processing_time=time.time() - start_time,
                operations=operations,
                success=False,
                error=str(e)
            )
    
    async def process_images_comparison(self, image_paths: List[Path]):
        """다양한 처리 방식 비교"""
        output_dir = Path("processed_images")
        output_dir.mkdir(exist_ok=True)
        
        print("\n🔄 처리 방식 비교")
        print("=" * 60)
        
        # 1. 순차 처리
        print("\n1. 순차 처리")
        with self.tracker.track("Sequential Processing"):
            start_time = time.time()
            results_seq = []
            
            for path in image_paths:
                result = self.process_image_single(str(path), str(output_dir))
                results_seq.append(result)
            
            seq_time = time.time() - start_time
        
        print(f"  ⏱️  완료: {seq_time:.2f}초")
        
        # 2. 멀티프로세싱
        print("\n2. 멀티프로세싱 (ProcessPoolExecutor)")
        with self.tracker.track("Multiprocessing"):
            start_time = time.time()
            
            with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
                futures = [
                    executor.submit(self.process_image_single, str(path), str(output_dir))
                    for path in image_paths
                ]
                results_mp = [f.result() for f in futures]
            
            mp_time = time.time() - start_time
        
        print(f"  ⏱️  완료: {mp_time:.2f}초 (속도 향상: {seq_time/mp_time:.1f}x)")
        
        # 3. 배치 처리
        print("\n3. 배치 처리 (동기)")
        with self.tracker.track("Batch Processing"):
            batch_processor = BatchProcessor[str, ImageProcessingResult](
                batch_size=3,
                max_workers=mp.cpu_count(),
                use_processes=True
            )
            
            def batch_process_func(paths: List[str]) -> List[ImageProcessingResult]:
                return [self.process_image_single(path, str(output_dir)) for path in paths]
            
            start_time = time.time()
            batch_results = batch_processor.process(
                [str(p) for p in image_paths],
                batch_process_func,
                parallel=True
            )
            batch_time = time.time() - start_time
        
        print(f"  ⏱️  완료: {batch_time:.2f}초")
        
        # 통계 출력
        print("\n📊 처리 통계:")
        print(f"  총 이미지: {len(image_paths)}개")
        print(f"  순차 처리: {seq_time:.2f}초 ({seq_time/len(image_paths):.2f}초/이미지)")
        print(f"  멀티프로세싱: {mp_time:.2f}초 ({mp_time/len(image_paths):.2f}초/이미지)")
        print(f"  배치 처리: {batch_time:.2f}초 ({batch_time/len(image_paths):.2f}초/이미지)")
    
    async def process_with_monitoring(self, image_paths: List[Path]):
        """모니터링과 함께 처리"""
        print("\n\n📊 리소스 모니터링과 함께 처리")
        print("=" * 60)
        
        # 모니터링 시작
        self.monitor.start()
        
        # 이미지 처리
        output_dir = Path("monitored_processing")
        output_dir.mkdir(exist_ok=True)
        
        # CPU 집약적 작업
        print("\n🔥 CPU 집약적 이미지 처리 실행 중...")
        
        processor = ProcessProcessor(max_workers=mp.cpu_count())
        
        start_time = time.time()
        results = processor.process_files_parallel(
            [str(p) for p in image_paths],
            custom_processor=lambda path: self.process_image_single(path, str(output_dir))
        )
        duration = time.time() - start_time
        
        # 모니터링 중지
        self.monitor.stop()
        
        print(f"\n✅ 처리 완료: {duration:.2f}초")
        
        # 결과 분석
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        print(f"\n처리 결과:")
        print(f"  성공: {len(successful)}개")
        print(f"  실패: {len(failed)}개")
        
        if successful:
            avg_time = sum(r["result"].processing_time for r in successful) / len(successful)
            print(f"  평균 처리 시간: {avg_time:.3f}초/이미지")
        
        # 모니터링 결과
        self.monitor.print_summary()
        
        # 리소스 사용 그래프 (텍스트 기반)
        print("\n\n📈 CPU 사용률 추이:")
        if self.monitor.history:
            # 5개 구간으로 나누어 표시
            samples = list(self.monitor.history)
            interval = len(samples) // 5
            
            for i in range(0, len(samples), interval):
                idx = min(i, len(samples) - 1)
                cpu = samples[idx].cpu_percent
                bar = "█" * int(cpu / 10)
                print(f"  {i:3d}s: {bar:<10} {cpu:.1f}%")
    
    async def run(self):
        """예제 실행"""
        print("🖼️  이미지 처리 예제")
        print("=" * 60)
        
        # 샘플 이미지 생성
        sample_dir = Path("sample_images")
        image_paths = self.create_sample_images(sample_dir, count=12)
        
        # 1. 처리 방식 비교
        await self.process_images_comparison(image_paths)
        
        # 2. 모니터링과 함께 처리
        await self.process_with_monitoring(image_paths)
        
        # 3. 성능 리포트
        print("\n\n📋 전체 성능 리포트")
        print("=" * 60)
        self.tracker.print_report()
        
        # 리포트 저장
        self.tracker.save_report("image_processing_report.json")
        self.monitor.save_history("image_processing_monitor.json")
        
        print("\n✅ 리포트 저장 완료")


async def main():
    """메인 함수"""
    example = ImageProcessorExample()
    await example.run()


if __name__ == "__main__":
    asyncio.run(main())