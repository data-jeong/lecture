"""
텍스트 통계 모듈
텍스트의 다양한 통계 정보를 계산합니다.
"""

import re
from collections import Counter

def count_words(text):
    """단어 수를 계산합니다."""
    # 한글, 영어, 숫자를 단어로 인식
    words = re.findall(r'\b\w+\b', text)
    return len(words)

def count_sentences(text):
    """문장 수를 계산합니다."""
    # . ! ? 로 끝나는 문장 찾기
    sentences = re.split(r'[.!?]+', text)
    # 빈 문자열 제거
    sentences = [s.strip() for s in sentences if s.strip()]
    return len(sentences)

def count_characters(text, include_spaces=True):
    """문자 수를 계산합니다."""
    if include_spaces:
        return len(text)
    else:
        return len(text.replace(' ', '').replace('\n', '').replace('\t', ''))

def average_word_length(text):
    """평균 단어 길이를 계산합니다."""
    words = re.findall(r'\b\w+\b', text)
    if not words:
        return 0
    
    total_length = sum(len(word) for word in words)
    return total_length / len(words)

def word_frequency(text, top_n=10):
    """단어 빈도를 계산합니다."""
    # 소문자로 변환하여 대소문자 구분 없이 계산
    words = re.findall(r'\b\w+\b', text.lower())
    
    # 불용어 제거 (옵션)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                  '은', '는', '이', '가', '을', '를', '에', '의', '와', '과'}
    words = [word for word in words if word not in stop_words and len(word) > 1]
    
    # 빈도 계산
    word_count = Counter(words)
    
    if top_n:
        return word_count.most_common(top_n)
    else:
        return dict(word_count)

def get_statistics(text):
    """텍스트의 전체 통계를 계산합니다."""
    stats = {
        '총 문자 수': count_characters(text, include_spaces=True),
        '공백 제외 문자 수': count_characters(text, include_spaces=False),
        '단어 수': count_words(text),
        '문장 수': count_sentences(text),
        '평균 단어 길이': round(average_word_length(text), 2),
        '줄 수': text.count('\n') + 1,
        '공백 수': text.count(' '),
        '숫자 수': len(re.findall(r'\d', text)),
        '영문자 수': len(re.findall(r'[a-zA-Z]', text)),
        '한글 수': len(re.findall(r'[가-힣]', text))
    }
    
    # 단어당 평균 문자 수
    if stats['단어 수'] > 0:
        stats['단어당 평균 문자'] = round(stats['공백 제외 문자 수'] / stats['단어 수'], 2)
    else:
        stats['단어당 평균 문자'] = 0
    
    # 문장당 평균 단어 수
    if stats['문장 수'] > 0:
        stats['문장당 평균 단어'] = round(stats['단어 수'] / stats['문장 수'], 2)
    else:
        stats['문장당 평균 단어'] = 0
    
    return stats

def reading_time(text, words_per_minute=200):
    """예상 읽기 시간을 계산합니다 (분 단위)."""
    word_count = count_words(text)
    minutes = word_count / words_per_minute
    
    if minutes < 1:
        return "1분 미만"
    else:
        return f"약 {round(minutes)}분"

def lexical_diversity(text):
    """어휘 다양성을 계산합니다 (고유 단어 비율)."""
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0
    
    unique_words = set(words)
    return len(unique_words) / len(words)

def syllable_count(word):
    """단어의 음절 수를 추정합니다 (영어 기준)."""
    word = word.lower()
    vowels = 'aeiou'
    count = 0
    previous_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            count += 1
        previous_was_vowel = is_vowel
    
    # 'e'로 끝나는 경우 조정
    if word.endswith('e') and count > 1:
        count -= 1
    
    return max(1, count)

def readability_score(text):
    """가독성 점수를 계산합니다 (Flesch Reading Ease 변형)."""
    sentences = count_sentences(text)
    words = count_words(text)
    
    if sentences == 0 or words == 0:
        return 0
    
    # 평균 문장 길이
    avg_sentence_length = words / sentences
    
    # 평균 음절 수 (간단히 평균 단어 길이로 대체)
    avg_syllables = average_word_length(text) / 3  # 대략적인 추정
    
    # Flesch Reading Ease 공식의 간소화 버전
    score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables
    
    # 0-100 범위로 조정
    score = max(0, min(100, score))
    
    if score >= 90:
        return f"{score:.1f} (매우 쉬움)"
    elif score >= 80:
        return f"{score:.1f} (쉬움)"
    elif score >= 70:
        return f"{score:.1f} (보통)"
    elif score >= 60:
        return f"{score:.1f} (약간 어려움)"
    elif score >= 50:
        return f"{score:.1f} (어려움)"
    else:
        return f"{score:.1f} (매우 어려움)"