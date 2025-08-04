"""
파일 유틸리티
파일 처리를 위한 공통 유틸리티 함수들
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Generator, Tuple
import hashlib
import mimetypes
import json
import csv
import asyncio
import aiofiles
from datetime import datetime


class FileUtils:
    """파일 관련 유틸리티"""
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """파일 정보 추출"""
        path = Path(file_path)
        
        if not path.exists():
            return {"error": "File not found"}
        
        stat = path.stat()
        
        return {
            "name": path.name,
            "path": str(path.absolute()),
            "size": stat.st_size,
            "size_human": FileUtils.human_readable_size(stat.st_size),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "extension": path.suffix,
            "mime_type": mimetypes.guess_type(str(path))[0]
        }
    
    @staticmethod
    def human_readable_size(size: int) -> str:
        """파일 크기를 읽기 쉬운 형태로 변환"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    @staticmethod
    def calculate_checksum(file_path: str, algorithm: str = 'md5') -> str:
        """파일 체크섬 계산"""
        hash_func = getattr(hashlib, algorithm)()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    async def calculate_checksum_async(file_path: str, algorithm: str = 'md5') -> str:
        """비동기 파일 체크섬 계산"""
        hash_func = getattr(hashlib, algorithm)()
        
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    def find_files(
        directory: str,
        pattern: str = "*",
        recursive: bool = True,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        extensions: Optional[List[str]] = None
    ) -> List[Path]:
        """조건에 맞는 파일 찾기"""
        path = Path(directory)
        
        if recursive:
            files = path.rglob(pattern)
        else:
            files = path.glob(pattern)
        
        result = []
        for file in files:
            if not file.is_file():
                continue
            
            # 크기 필터
            size = file.stat().st_size
            if min_size and size < min_size:
                continue
            if max_size and size > max_size:
                continue
            
            # 확장자 필터
            if extensions and file.suffix.lower() not in extensions:
                continue
            
            result.append(file)
        
        return result
    
    @staticmethod
    def split_file(
        file_path: str,
        chunk_size: int = 1024 * 1024,  # 1MB
        output_dir: Optional[str] = None
    ) -> List[str]:
        """파일 분할"""
        path = Path(file_path)
        
        if output_dir is None:
            output_dir = path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        chunks = []
        
        with open(file_path, 'rb') as f:
            chunk_num = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                chunk_file = output_dir / f"{path.stem}.part{chunk_num:03d}"
                with open(chunk_file, 'wb') as cf:
                    cf.write(chunk)
                
                chunks.append(str(chunk_file))
                chunk_num += 1
        
        return chunks
    
    @staticmethod
    def merge_files(
        chunk_files: List[str],
        output_file: str
    ) -> str:
        """분할된 파일 병합"""
        with open(output_file, 'wb') as output:
            for chunk_file in sorted(chunk_files):
                with open(chunk_file, 'rb') as chunk:
                    output.write(chunk.read())
        
        return output_file
    
    @staticmethod
    async def stream_large_file(
        file_path: str,
        chunk_size: int = 8192
    ) -> Generator[bytes, None, None]:
        """대용량 파일 스트리밍"""
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(chunk_size):
                yield chunk
    
    @staticmethod
    def compare_files(file1: str, file2: str) -> dict:
        """두 파일 비교"""
        path1 = Path(file1)
        path2 = Path(file2)
        
        if not path1.exists() or not path2.exists():
            return {"equal": False, "error": "One or both files not found"}
        
        # 크기 비교
        size1 = path1.stat().st_size
        size2 = path2.stat().st_size
        
        if size1 != size2:
            return {
                "equal": False,
                "reason": "Different sizes",
                "size1": size1,
                "size2": size2
            }
        
        # 내용 비교 (체크섬)
        hash1 = FileUtils.calculate_checksum(file1)
        hash2 = FileUtils.calculate_checksum(file2)
        
        return {
            "equal": hash1 == hash2,
            "size": size1,
            "hash1": hash1,
            "hash2": hash2
        }
    
    @staticmethod
    def backup_file(
        file_path: str,
        backup_dir: Optional[str] = None,
        timestamp: bool = True
    ) -> str:
        """파일 백업"""
        path = Path(file_path)
        
        if backup_dir is None:
            backup_dir = path.parent / "backups"
        else:
            backup_dir = Path(backup_dir)
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        if timestamp:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{path.stem}_{timestamp_str}{path.suffix}"
        else:
            backup_name = path.name
        
        backup_path = backup_dir / backup_name
        shutil.copy2(file_path, backup_path)
        
        return str(backup_path)
    
    @staticmethod
    def clean_directory(
        directory: str,
        days_old: int = 30,
        pattern: str = "*",
        dry_run: bool = True
    ) -> List[dict]:
        """오래된 파일 정리"""
        path = Path(directory)
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        removed_files = []
        
        for file in path.glob(pattern):
            if not file.is_file():
                continue
            
            if file.stat().st_mtime < cutoff_time:
                file_info = {
                    "path": str(file),
                    "size": file.stat().st_size,
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                }
                
                if not dry_run:
                    file.unlink()
                    file_info["removed"] = True
                else:
                    file_info["removed"] = False
                
                removed_files.append(file_info)
        
        return removed_files
    
    @staticmethod
    def read_json_file(file_path: str) -> dict:
        """JSON 파일 읽기"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def write_json_file(file_path: str, data: dict, indent: int = 2) -> None:
        """JSON 파일 쓰기"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def read_csv_file(
        file_path: str,
        delimiter: str = ',',
        has_header: bool = True
    ) -> List[dict]:
        """CSV 파일 읽기"""
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter) if has_header else csv.reader(f, delimiter=delimiter)
            return list(reader)
    
    @staticmethod
    def write_csv_file(
        file_path: str,
        data: List[dict],
        delimiter: str = ',',
        headers: Optional[List[str]] = None
    ) -> None:
        """CSV 파일 쓰기"""
        if not data:
            return
        
        if headers is None:
            headers = list(data[0].keys())
        
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(data)
    
    @staticmethod
    def monitor_file_changes(
        file_path: str,
        callback: callable,
        interval: float = 1.0
    ) -> None:
        """파일 변경 모니터링"""
        path = Path(file_path)
        last_modified = path.stat().st_mtime if path.exists() else 0
        
        while True:
            try:
                if path.exists():
                    current_modified = path.stat().st_mtime
                    if current_modified != last_modified:
                        callback(file_path, "modified")
                        last_modified = current_modified
                elif last_modified > 0:
                    callback(file_path, "deleted")
                    last_modified = 0
                
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error monitoring {file_path}: {e}")


def example_usage():
    """사용 예제"""
    print("📂 파일 유틸리티 예제")
    print("=" * 60)
    
    # 1. 파일 정보
    print("\n1. 파일 정보:")
    info = FileUtils.get_file_info(__file__)
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # 2. 파일 찾기
    print("\n2. Python 파일 찾기:")
    py_files = FileUtils.find_files(
        directory=".",
        pattern="*.py",
        recursive=False,
        min_size=1000  # 1KB 이상
    )
    
    for file in py_files[:5]:  # 처음 5개만
        print(f"  - {file.name} ({FileUtils.human_readable_size(file.stat().st_size)})")
    
    # 3. 체크섬 계산
    print("\n3. 체크섬 계산:")
    if py_files:
        checksum = FileUtils.calculate_checksum(str(py_files[0]))
        print(f"  {py_files[0].name}: {checksum}")
    
    # 4. JSON 작업
    print("\n4. JSON 파일 작업:")
    test_data = {
        "name": "File Utils Test",
        "timestamp": datetime.now().isoformat(),
        "files": len(py_files)
    }
    
    FileUtils.write_json_file("test_file_utils.json", test_data)
    loaded_data = FileUtils.read_json_file("test_file_utils.json")
    print(f"  저장된 데이터: {loaded_data}")
    
    # 정리
    Path("test_file_utils.json").unlink(missing_ok=True)


if __name__ == "__main__":
    example_usage()