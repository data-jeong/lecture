"""
파일 처리 모듈
텍스트 파일을 읽고 쓰고 처리하는 기능을 제공합니다.
"""

import os
from pathlib import Path
import glob
import shutil
from typing import List, Optional

def read_text_file(file_path, encoding='utf-8'):
    """텍스트 파일을 읽습니다."""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return None
    except UnicodeDecodeError:
        print(f"인코딩 오류. 다른 인코딩으로 시도해보세요: {file_path}")
        return None
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
        return None

def write_text_file(file_path, content, encoding='utf-8', mode='w'):
    """텍스트 파일을 작성합니다."""
    try:
        # 디렉토리가 없으면 생성
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"파일 쓰기 오류: {e}")
        return False

def process_multiple_files(file_pattern, process_func, output_dir=None):
    """여러 파일을 일괄 처리합니다."""
    files = glob.glob(file_pattern)
    results = []
    
    for file_path in files:
        print(f"처리 중: {file_path}")
        content = read_text_file(file_path)
        
        if content is not None:
            # 처리 함수 적용
            processed_content = process_func(content)
            
            # 출력 디렉토리가 지정된 경우
            if output_dir:
                output_path = os.path.join(output_dir, os.path.basename(file_path))
                write_text_file(output_path, processed_content)
                results.append({
                    'input': file_path,
                    'output': output_path,
                    'status': 'success'
                })
            else:
                results.append({
                    'input': file_path,
                    'content': processed_content,
                    'status': 'success'
                })
        else:
            results.append({
                'input': file_path,
                'status': 'failed'
            })
    
    return results

def merge_files(file_list, output_file, separator='\n\n'):
    """여러 파일을 하나로 합칩니다."""
    merged_content = []
    
    for file_path in file_list:
        content = read_text_file(file_path)
        if content:
            # 파일명을 헤더로 추가 (옵션)
            header = f"=== {os.path.basename(file_path)} ==="
            merged_content.append(header)
            merged_content.append(content)
    
    # 합친 내용 저장
    final_content = separator.join(merged_content)
    return write_text_file(output_file, final_content)

def split_file(file_path, lines_per_file=100, output_prefix='part'):
    """파일을 여러 개로 분할합니다."""
    content = read_text_file(file_path)
    if not content:
        return []
    
    lines = content.split('\n')
    total_lines = len(lines)
    
    output_files = []
    part_number = 1
    
    for i in range(0, total_lines, lines_per_file):
        part_lines = lines[i:i + lines_per_file]
        part_content = '\n'.join(part_lines)
        
        # 출력 파일명 생성
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = f"{output_prefix}_{part_number}_{base_name}.txt"
        
        if write_text_file(output_file, part_content):
            output_files.append(output_file)
        
        part_number += 1
    
    return output_files

def get_file_info(file_path):
    """파일 정보를 반환합니다."""
    try:
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'size_human': format_file_size(stat.st_size),
            'modified': stat.st_mtime,
            'created': stat.st_ctime,
            'extension': os.path.splitext(file_path)[1],
            'exists': True
        }
    except FileNotFoundError:
        return {
            'path': file_path,
            'exists': False
        }

def format_file_size(size_bytes):
    """파일 크기를 사람이 읽기 쉬운 형식으로 변환합니다."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def backup_file(file_path, backup_dir='backup'):
    """파일을 백업합니다."""
    if not os.path.exists(file_path):
        return False
    
    # 백업 디렉토리 생성
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # 타임스탬프를 포함한 백업 파일명 생성
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_name = os.path.basename(file_path)
    backup_name = f"{timestamp}_{base_name}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"백업 실패: {e}")
        return None

def find_files(directory, pattern='*', recursive=True):
    """디렉토리에서 파일을 검색합니다."""
    if recursive:
        pattern = f"**/{pattern}"
        files = list(Path(directory).glob(pattern))
    else:
        files = list(Path(directory).glob(pattern))
    
    return [str(f) for f in files if f.is_file()]

def compare_files(file1, file2):
    """두 파일의 내용을 비교합니다."""
    content1 = read_text_file(file1)
    content2 = read_text_file(file2)
    
    if content1 is None or content2 is None:
        return None
    
    lines1 = content1.splitlines()
    lines2 = content2.splitlines()
    
    differences = []
    max_lines = max(len(lines1), len(lines2))
    
    for i in range(max_lines):
        line1 = lines1[i] if i < len(lines1) else None
        line2 = lines2[i] if i < len(lines2) else None
        
        if line1 != line2:
            differences.append({
                'line_number': i + 1,
                'file1': line1,
                'file2': line2
            })
    
    return {
        'identical': len(differences) == 0,
        'differences': differences,
        'total_differences': len(differences)
    }