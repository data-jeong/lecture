"""
텍스트 분석 모듈
고급 텍스트 분석 기능을 제공하는 유틸리티 함수들
"""

import re
from collections import Counter
from typing import List, Tuple, Dict, Optional


def analyze_sentiment(text: str) -> Dict[str, float]:
    """간단한 감정 분석을 수행합니다."""
    positive_words = [
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
        'love', 'like', 'best', 'happy', 'joy', 'pleased', 'glad',
        '좋은', '훌륭한', '최고', '사랑', '행복', '기쁨'
    ]
    
    negative_words = [
        'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike',
        'worst', 'sad', 'angry', 'upset', 'disappointed',
        '나쁜', '최악', '싫어', '슬픔', '화남', '실망'
    ]
    
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    total_words = len(words)
    
    if total_words == 0:
        return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
    
    positive_ratio = positive_count / total_words
    negative_ratio = negative_count / total_words
    neutral_ratio = 1.0 - positive_ratio - negative_ratio
    
    return {
        'positive': round(positive_ratio, 3),
        'negative': round(negative_ratio, 3),
        'neutral': round(neutral_ratio, 3)
    }


def extract_keywords(text: str, top_n: int = 10) -> List[Tuple[str, int]]:
    """텍스트에서 주요 키워드를 추출합니다."""
    # 불용어 제거
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'been',
        '은', '는', '이', '가', '을', '를', '의', '에', '와', '과'
    }
    
    words = re.findall(r'\b\w+\b', text.lower())
    filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
    
    word_freq = Counter(filtered_words)
    return word_freq.most_common(top_n)


def language_detection(text: str) -> str:
    """간단한 언어 감지를 수행합니다."""
    korean_pattern = re.compile(r'[가-힣]+')
    english_pattern = re.compile(r'[a-zA-Z]+')
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    japanese_pattern = re.compile(r'[\u3040-\u309f\u30a0-\u30ff]+')
    
    korean_count = len(korean_pattern.findall(text))
    english_count = len(english_pattern.findall(text))
    chinese_count = len(chinese_pattern.findall(text))
    japanese_count = len(japanese_pattern.findall(text))
    
    counts = {
        'Korean': korean_count,
        'English': english_count,
        'Chinese': chinese_count,
        'Japanese': japanese_count
    }
    
    if all(count == 0 for count in counts.values()):
        return 'Unknown'
    
    return max(counts, key=counts.get)


def text_complexity(text: str) -> Dict[str, float]:
    """텍스트 복잡도를 분석합니다."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    words = re.findall(r'\b\w+\b', text)
    
    if not sentences or not words:
        return {
            'avg_sentence_length': 0,
            'avg_word_length': 0,
            'vocabulary_diversity': 0,
            'complexity_score': 0
        }
    
    avg_sentence_length = len(words) / len(sentences)
    avg_word_length = sum(len(word) for word in words) / len(words)
    unique_words = set(word.lower() for word in words)
    vocabulary_diversity = len(unique_words) / len(words)
    
    # 복잡도 점수 계산 (0-100)
    complexity_score = min(100, (
        avg_sentence_length * 2 +
        avg_word_length * 5 +
        vocabulary_diversity * 30
    ))
    
    return {
        'avg_sentence_length': round(avg_sentence_length, 2),
        'avg_word_length': round(avg_word_length, 2),
        'vocabulary_diversity': round(vocabulary_diversity, 3),
        'complexity_score': round(complexity_score, 1)
    }


def find_named_entities(text: str) -> Dict[str, List[str]]:
    """간단한 개체명 인식을 수행합니다."""
    entities = {
        'persons': [],
        'organizations': [],
        'locations': [],
        'dates': [],
        'money': []
    }
    
    # 사람 이름 패턴 (대문자로 시작하는 연속된 단어)
    person_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
    entities['persons'] = re.findall(person_pattern, text)
    
    # 조직명 패턴 (Inc., Corp., LLC 등)
    org_pattern = r'\b[A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*(?:,? (?:Inc|Corp|LLC|Ltd|Co|Company)\.?)\b'
    entities['organizations'] = re.findall(org_pattern, text)
    
    # 날짜 패턴
    date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}년 \d{1,2}월 \d{1,2}일\b'
    entities['dates'] = re.findall(date_pattern, text)
    
    # 금액 패턴
    money_pattern = r'\$[\d,]+(?:\.\d{2})?|\b\d+(?:,\d{3})*원\b'
    entities['money'] = re.findall(money_pattern, text)
    
    return entities


def text_similarity(text1: str, text2: str) -> float:
    """두 텍스트의 유사도를 계산합니다 (Jaccard similarity)."""
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)


def extract_summary(text: str, num_sentences: int = 3) -> str:
    """간단한 추출적 요약을 생성합니다."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= num_sentences:
        return text
    
    # 각 문장의 중요도 계산 (단어 빈도 기반)
    words = re.findall(r'\b\w+\b', text.lower())
    word_freq = Counter(words)
    
    sentence_scores = []
    for sentence in sentences:
        sentence_words = re.findall(r'\b\w+\b', sentence.lower())
        score = sum(word_freq[word] for word in sentence_words)
        sentence_scores.append((score, sentence))
    
    # 상위 n개 문장 선택
    sentence_scores.sort(reverse=True)
    selected_sentences = [sent for _, sent in sentence_scores[:num_sentences]]
    
    # 원래 순서대로 정렬
    summary_sentences = []
    for sentence in sentences:
        if sentence in selected_sentences:
            summary_sentences.append(sentence)
    
    return '. '.join(summary_sentences) + '.'


def detect_plagiarism(text1: str, text2: str, threshold: float = 0.8) -> Dict[str, any]:
    """두 텍스트 간의 표절 가능성을 검사합니다."""
    similarity = text_similarity(text1, text2)
    
    # n-gram 비교 (3-gram)
    def get_ngrams(text, n=3):
        words = re.findall(r'\b\w+\b', text.lower())
        return set(tuple(words[i:i+n]) for i in range(len(words)-n+1))
    
    ngrams1 = get_ngrams(text1)
    ngrams2 = get_ngrams(text2)
    
    if ngrams1 and ngrams2:
        ngram_similarity = len(ngrams1.intersection(ngrams2)) / len(ngrams1.union(ngrams2))
    else:
        ngram_similarity = 0.0
    
    is_plagiarized = similarity > threshold or ngram_similarity > threshold
    
    return {
        'word_similarity': round(similarity, 3),
        'ngram_similarity': round(ngram_similarity, 3),
        'is_plagiarized': is_plagiarized,
        'confidence': round(max(similarity, ngram_similarity), 3)
    }