"""
텍스트 검색 모듈
정규표현식을 활용한 다양한 패턴 검색 기능을 제공합니다.
"""

import re
from typing import List, Tuple, Optional

def find_pattern(text, pattern, case_sensitive=True):
    """텍스트에서 패턴과 일치하는 첫 번째 항목을 찾습니다."""
    flags = 0 if case_sensitive else re.IGNORECASE
    match = re.search(pattern, text, flags=flags)
    
    if match:
        return {
            'match': match.group(),
            'start': match.start(),
            'end': match.end(),
            'groups': match.groups()
        }
    return None

def find_all_patterns(text, pattern, case_sensitive=True):
    """텍스트에서 패턴과 일치하는 모든 항목을 찾습니다."""
    flags = 0 if case_sensitive else re.IGNORECASE
    matches = []
    
    for match in re.finditer(pattern, text, flags=flags):
        matches.append({
            'match': match.group(),
            'start': match.start(),
            'end': match.end(),
            'groups': match.groups()
        })
    
    return matches

def find_emails(text):
    """텍스트에서 이메일 주소를 찾습니다."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return list(set(emails))  # 중복 제거

def find_phone_numbers(text):
    """텍스트에서 전화번호를 찾습니다."""
    patterns = [
        r'\d{3}-\d{4}-\d{4}',  # 010-1234-5678
        r'\d{3}\.\d{4}\.\d{4}',  # 010.1234.5678
        r'\d{3}\s\d{4}\s\d{4}',  # 010 1234 5678
        r'\(\d{3}\)\s?\d{4}-\d{4}',  # (010) 1234-5678
        r'\d{2,3}-\d{3,4}-\d{4}',  # 02-123-4567
    ]
    
    phone_numbers = []
    for pattern in patterns:
        found = re.findall(pattern, text)
        phone_numbers.extend(found)
    
    return list(set(phone_numbers))  # 중복 제거

def find_urls(text):
    """텍스트에서 URL을 찾습니다."""
    url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
    urls = re.findall(url_pattern, text)
    return list(set(urls))  # 중복 제거

def find_korean_words(text):
    """텍스트에서 한글 단어를 찾습니다."""
    korean_pattern = r'[가-힣]+'
    korean_words = re.findall(korean_pattern, text)
    return korean_words

def find_english_words(text):
    """텍스트에서 영어 단어를 찾습니다."""
    english_pattern = r'\b[A-Za-z]+\b'
    english_words = re.findall(english_pattern, text)
    return english_words

def find_numbers(text, include_decimal=True):
    """텍스트에서 숫자를 찾습니다."""
    if include_decimal:
        number_pattern = r'-?\d+\.?\d*'
    else:
        number_pattern = r'-?\d+'
    
    numbers = re.findall(number_pattern, text)
    return numbers

def find_dates(text):
    """텍스트에서 날짜를 찾습니다."""
    date_patterns = [
        r'\d{4}[-/년]\s?\d{1,2}[-/월]\s?\d{1,2}일?',  # 2024-01-01, 2024년 1월 1일
        r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',  # 01-01-2024, 1/1/2024
        r'\d{4}\.\d{1,2}\.\d{1,2}',  # 2024.01.01
    ]
    
    dates = []
    for pattern in date_patterns:
        found = re.findall(pattern, text)
        dates.extend(found)
    
    return list(set(dates))  # 중복 제거

def find_times(text):
    """텍스트에서 시간을 찾습니다."""
    time_patterns = [
        r'\d{1,2}:\d{2}(?::\d{2})?(?:\s?[AP]M)?',  # 12:30, 12:30:45, 12:30 PM
        r'\d{1,2}시\s?\d{0,2}분?',  # 12시, 12시 30분
    ]
    
    times = []
    for pattern in time_patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        times.extend(found)
    
    return list(set(times))  # 중복 제거

def highlight_pattern(text, pattern, prefix='[', suffix=']', case_sensitive=True):
    """패턴과 일치하는 부분을 강조 표시합니다."""
    flags = 0 if case_sensitive else re.IGNORECASE
    
    def replace_func(match):
        return f"{prefix}{match.group()}{suffix}"
    
    return re.sub(pattern, replace_func, text, flags=flags)

def find_sentences_with_word(text, word, case_sensitive=False):
    """특정 단어를 포함하는 문장을 찾습니다."""
    # 문장 분리
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # 단어를 포함하는 문장 찾기
    matching_sentences = []
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = r'\b' + re.escape(word) + r'\b'
    
    for sentence in sentences:
        if re.search(pattern, sentence, flags=flags):
            matching_sentences.append(sentence)
    
    return matching_sentences

def extract_quotes(text):
    """텍스트에서 인용문을 추출합니다."""
    # 큰따옴표 안의 내용
    double_quotes = re.findall(r'"([^"]*)"', text)
    # 작은따옴표 안의 내용
    single_quotes = re.findall(r"'([^']*)'", text)
    
    return {
        'double_quotes': double_quotes,
        'single_quotes': single_quotes,
        'all': double_quotes + single_quotes
    }

def find_hashtags(text):
    """텍스트에서 해시태그를 찾습니다."""
    hashtag_pattern = r'#[가-힣A-Za-z0-9_]+'
    hashtags = re.findall(hashtag_pattern, text)
    return list(set(hashtags))  # 중복 제거

def find_mentions(text):
    """텍스트에서 멘션(@사용자명)을 찾습니다."""
    mention_pattern = r'@[A-Za-z0-9_]+'
    mentions = re.findall(mention_pattern, text)
    return list(set(mentions))  # 중복 제거