"""
텍스트 처리 유틸리티 테스트
모든 함수가 올바르게 작동하는지 확인합니다.
"""

import unittest
from text_utils import *

class TestStatistics(unittest.TestCase):
    """통계 함수 테스트"""
    
    def test_count_words(self):
        """단어 수 계산 테스트"""
        self.assertEqual(count_words("Hello World"), 2)
        self.assertEqual(count_words("한글 테스트 입니다"), 3)
        self.assertEqual(count_words(""), 0)
    
    def test_count_sentences(self):
        """문장 수 계산 테스트"""
        self.assertEqual(count_sentences("Hello. World!"), 2)
        self.assertEqual(count_sentences("첫 문장. 두 번째 문장! 세 번째?"), 3)
        self.assertEqual(count_sentences("문장 부호 없음"), 1)
    
    def test_average_word_length(self):
        """평균 단어 길이 테스트"""
        self.assertAlmostEqual(average_word_length("Hi Python"), 4.0)  # Hi(2) + Python(6) = 8/2 = 4
        self.assertEqual(average_word_length(""), 0)
    
    def test_word_frequency(self):
        """단어 빈도 테스트"""
        text = "Python Python Java Python Java C++"
        freq = word_frequency(text, top_n=None)
        self.assertEqual(freq['python'], 3)
        self.assertEqual(freq['java'], 2)

class TestTransformers(unittest.TestCase):
    """변환 함수 테스트"""
    
    def test_case_conversion(self):
        """대소문자 변환 테스트"""
        text = "Hello Python"
        self.assertEqual(to_uppercase(text), "HELLO PYTHON")
        self.assertEqual(to_lowercase(text), "hello python")
        self.assertEqual(to_title(text), "Hello Python")
    
    def test_remove_punctuation(self):
        """구두점 제거 테스트"""
        text = "Hello, World!"
        self.assertEqual(remove_punctuation(text), "Hello World")
    
    def test_remove_extra_spaces(self):
        """공백 정리 테스트"""
        text = "  too    many   spaces  "
        self.assertEqual(remove_extra_spaces(text), "too many spaces")
    
    def test_mask_sensitive_data(self):
        """민감정보 마스킹 테스트"""
        text = "이메일: test@example.com"
        masked = mask_sensitive_data(text)
        self.assertIn("***@example.com", masked)
        
        text = "전화: 010-1234-5678"
        masked = mask_sensitive_data(text)
        self.assertIn("010-****-5678", masked)

class TestSearchers(unittest.TestCase):
    """검색 함수 테스트"""
    
    def test_find_emails(self):
        """이메일 찾기 테스트"""
        text = "연락처: admin@example.com, test@sub.example.co.kr"
        emails = find_emails(text)
        self.assertEqual(len(emails), 2)
        self.assertIn("admin@example.com", emails)
    
    def test_find_phone_numbers(self):
        """전화번호 찾기 테스트"""
        text = "전화: 010-1234-5678, 02-123-4567"
        phones = find_phone_numbers(text)
        self.assertIn("010-1234-5678", phones)
        self.assertIn("02-123-4567", phones)
    
    def test_find_urls(self):
        """URL 찾기 테스트"""
        text = "웹사이트: https://www.example.com, http://blog.example.com"
        urls = find_urls(text)
        self.assertEqual(len(urls), 2)
    
    def test_find_pattern(self):
        """패턴 찾기 테스트"""
        text = "Python 3.9"
        result = find_pattern(text, r'\d+\.\d+')
        self.assertEqual(result['match'], '3.9')

class TestFileHandlers(unittest.TestCase):
    """파일 처리 함수 테스트"""
    
    def setUp(self):
        """테스트 파일 생성"""
        self.test_file = 'test_temp.txt'
        self.test_content = 'Test content\n테스트 내용'
    
    def tearDown(self):
        """테스트 파일 삭제"""
        import os
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists('backup'):
            import shutil
            shutil.rmtree('backup')
    
    def test_write_and_read(self):
        """파일 쓰기/읽기 테스트"""
        # 쓰기
        result = write_text_file(self.test_file, self.test_content)
        self.assertTrue(result)
        
        # 읽기
        content = read_text_file(self.test_file)
        self.assertEqual(content, self.test_content)
    
    def test_file_info(self):
        """파일 정보 테스트"""
        write_text_file(self.test_file, self.test_content)
        info = get_file_info(self.test_file)
        
        self.assertTrue(info['exists'])
        self.assertEqual(info['name'], self.test_file)
        self.assertGreater(info['size'], 0)
    
    def test_backup_file(self):
        """파일 백업 테스트"""
        write_text_file(self.test_file, self.test_content)
        backup_path = backup_file(self.test_file)
        
        self.assertIsNotNone(backup_path)
        self.assertTrue(os.path.exists(backup_path))

class TestIntegration(unittest.TestCase):
    """통합 테스트"""
    
    def test_text_processing_pipeline(self):
        """텍스트 처리 파이프라인 테스트"""
        # 원본 텍스트
        text = """
        HELLO   WORLD!   
        Contact: test@EXAMPLE.COM
        Phone: 010-1234-5678
        """
        
        # 1. 공백 정리
        text = remove_extra_spaces(text)
        
        # 2. 소문자 변환
        text = to_lowercase(text)
        
        # 3. 이메일 찾기
        emails = find_emails(text)
        self.assertIn("test@example.com", emails)
        
        # 4. 전화번호 찾기
        phones = find_phone_numbers(text)
        self.assertIn("010-1234-5678", phones)
        
        # 5. 민감정보 마스킹
        masked = mask_sensitive_data(text)
        self.assertIn("***@example.com", masked)
        self.assertIn("010-****-5678", masked)

def run_tests():
    """모든 테스트 실행"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    print("텍스트 처리 유틸리티 테스트 시작...\n")
    run_tests()