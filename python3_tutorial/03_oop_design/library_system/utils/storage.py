"""
데이터 저장/불러오기 유틸리티
"""

import json
import os
from datetime import datetime

class Storage:
    """파일 저장소"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self._ensure_directory()
    
    def _ensure_directory(self):
        """데이터 디렉토리 생성"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save(self, data, filename):
        """데이터 저장"""
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            # 백업 생성
            if os.path.exists(filepath):
                backup_name = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                backup_path = os.path.join(self.data_dir, backup_name)
                os.rename(filepath, backup_path)
            
            # 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True, f"데이터가 {filepath}에 저장되었습니다."
        
        except Exception as e:
            return False, f"저장 실패: {str(e)}"
    
    def load(self, filename):
        """데이터 불러오기"""
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            if not os.path.exists(filepath):
                return None, "파일이 존재하지 않습니다."
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data, "데이터를 성공적으로 불러왔습니다."
        
        except json.JSONDecodeError:
            return None, "잘못된 JSON 형식입니다."
        except Exception as e:
            return None, f"불러오기 실패: {str(e)}"
    
    def list_files(self):
        """저장된 파일 목록"""
        try:
            files = []
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json') and not filename.endswith('.backup'):
                    filepath = os.path.join(self.data_dir, filename)
                    stat = os.stat(filepath)
                    files.append({
                        'name': filename,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime)
                    })
            
            # 수정일 기준 정렬
            files.sort(key=lambda x: x['modified'], reverse=True)
            return files
        
        except Exception as e:
            return []
    
    def delete(self, filename):
        """파일 삭제"""
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            if not os.path.exists(filepath):
                return False, "파일이 존재하지 않습니다."
            
            # 백업 생성
            backup_name = f"{filename}.deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = os.path.join(self.data_dir, backup_name)
            os.rename(filepath, backup_path)
            
            return True, f"파일이 삭제되었습니다. (백업: {backup_name})"
        
        except Exception as e:
            return False, f"삭제 실패: {str(e)}"
    
    def export_csv(self, data, filename):
        """CSV로 내보내기"""
        import csv
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                if not data:
                    return False, "내보낼 데이터가 없습니다."
                
                # 헤더 추출
                headers = list(data[0].keys())
                writer = csv.DictWriter(f, fieldnames=headers)
                
                writer.writeheader()
                writer.writerows(data)
            
            return True, f"데이터가 {filepath}에 저장되었습니다."
        
        except Exception as e:
            return False, f"CSV 내보내기 실패: {str(e)}"