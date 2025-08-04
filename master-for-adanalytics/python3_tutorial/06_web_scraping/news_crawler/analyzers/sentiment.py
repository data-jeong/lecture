"""
감정 분석기
텍스트의 감정(긍정/부정/중성) 분석
"""

import re
from typing import Dict, List, Optional, Union
from collections import Counter
import logging


class SentimentAnalyzer:
    """감정 분석기"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 감정 단어 사전 (간단한 한국어/영어)
        self.positive_words = {
            'ko': [
                '좋다', '훌륭하다', '멋지다', '완벽하다', '최고', '우수하다',
                '성공', '발전', '향상', '개선', '효과적', '긍정적', '만족',
                '행복', '기쁘다', '즐겁다', '감사', '축하', '환영', '희망'
            ],
            'en': [
                'good', 'great', 'excellent', 'perfect', 'amazing', 'wonderful',
                'success', 'improve', 'positive', 'happy', 'joy', 'love',
                'thank', 'congratulation', 'welcome', 'hope', 'best'
            ]
        }
        
        self.negative_words = {
            'ko': [
                '나쁘다', '최악', '끔찍하다', '실망', '문제', '심각하다',
                '실패', '위험', '걱정', '불안', '화나다', '슬프다',
                '비판', '반대', '거부', '충격', '우려', '위기', '손실'
            ],
            'en': [
                'bad', 'terrible', 'awful', 'worst', 'hate', 'angry',
                'sad', 'disappointed', 'problem', 'serious', 'fail',
                'danger', 'worry', 'concern', 'crisis', 'loss', 'shock'
            ]
        }
        
        # 감정 강도 수식어
        self.intensifiers = {
            'ko': ['매우', '정말', '너무', '아주', '완전히', '굉장히'],
            'en': ['very', 'really', 'extremely', 'quite', 'totally', 'absolutely']
        }
        
        self.diminishers = {
            'ko': ['조금', '약간', '다소', '그냥', '별로'],
            'en': ['little', 'slightly', 'somewhat', 'barely', 'hardly']
        }
    
    def analyze(self, text: str, language: str = 'auto') -> Dict[str, Union[str, float, int]]:
        """텍스트 감정 분석"""
        if not text:
            return self._empty_result()
        
        # 언어 감지
        if language == 'auto':
            language = self._detect_language(text)
        
        # 텍스트 전처리
        processed_text = self._preprocess_text(text)
        
        # 감정 점수 계산
        sentiment_score = self._calculate_sentiment_score(processed_text, language)
        
        # 감정 분류
        sentiment_label = self._classify_sentiment(sentiment_score)
        
        # 신뢰도 계산
        confidence = self._calculate_confidence(sentiment_score)
        
        # 감정 단어 추출
        emotion_words = self._extract_emotion_words(processed_text, language)
        
        return {
            'sentiment': sentiment_label,
            'score': sentiment_score,
            'confidence': confidence,
            'language': language,
            'positive_words': emotion_words['positive'],
            'negative_words': emotion_words['negative'],
            'word_count': len(processed_text.split()),
            'sentence_count': len(self._split_sentences(text))
        }
    
    def _detect_language(self, text: str) -> str:
        """언어 감지"""
        # 한글 문자 비율 확인
        korean_chars = len(re.findall(r'[가-힣]', text))
        total_chars = len(re.findall(r'\w', text))
        
        if total_chars > 0:
            korean_ratio = korean_chars / total_chars
            if korean_ratio > 0.3:
                return 'ko'
        
        return 'en'
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # 소문자 변환
        text = text.lower()
        
        # 특수문자 제거 (한글, 영문, 숫자, 공백만 유지)
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _calculate_sentiment_score(self, text: str, language: str) -> float:
        """감정 점수 계산 (-1.0 ~ 1.0)"""
        words = text.split()
        
        positive_score = 0
        negative_score = 0
        
        for i, word in enumerate(words):
            # 긍정 단어 체크
            if word in self.positive_words.get(language, []):
                score = 1.0
                
                # 이전 단어가 강화어인지 확인
                if i > 0 and words[i-1] in self.intensifiers.get(language, []):
                    score *= 1.5
                elif i > 0 and words[i-1] in self.diminishers.get(language, []):
                    score *= 0.5
                
                positive_score += score
            
            # 부정 단어 체크
            elif word in self.negative_words.get(language, []):
                score = 1.0
                
                # 이전 단어가 강화어인지 확인
                if i > 0 and words[i-1] in self.intensifiers.get(language, []):
                    score *= 1.5
                elif i > 0 and words[i-1] in self.diminishers.get(language, []):
                    score *= 0.5
                
                negative_score += score
        
        # 정규화
        total_emotional_words = positive_score + negative_score
        if total_emotional_words == 0:
            return 0.0
        
        # -1.0 ~ 1.0 범위로 정규화
        sentiment_score = (positive_score - negative_score) / total_emotional_words
        
        return max(-1.0, min(1.0, sentiment_score))
    
    def _classify_sentiment(self, score: float) -> str:
        """감정 분류"""
        if score > 0.1:
            return 'positive'
        elif score < -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_confidence(self, score: float) -> float:
        """신뢰도 계산"""
        # 절댓값이 클수록 신뢰도 높음
        confidence = abs(score)
        
        # 0.0 ~ 1.0 범위로 정규화
        return min(1.0, confidence * 2)
    
    def _extract_emotion_words(self, text: str, language: str) -> Dict[str, List[str]]:
        """감정 단어 추출"""
        words = text.split()
        
        positive_found = []
        negative_found = []
        
        for word in words:
            if word in self.positive_words.get(language, []):
                positive_found.append(word)
            elif word in self.negative_words.get(language, []):
                negative_found.append(word)
        
        return {
            'positive': list(set(positive_found)),
            'negative': list(set(negative_found))
        }
    
    def _split_sentences(self, text: str) -> List[str]:
        """문장 분할"""
        # 간단한 문장 분할 (마침표, 느낌표, 물음표 기준)
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _empty_result(self) -> Dict[str, Union[str, float, int]]:
        """빈 결과 반환"""
        return {
            'sentiment': 'neutral',
            'score': 0.0,
            'confidence': 0.0,
            'language': 'unknown',
            'positive_words': [],
            'negative_words': [],
            'word_count': 0,
            'sentence_count': 0
        }
    
    def analyze_batch(self, texts: List[str], language: str = 'auto') -> List[Dict]:
        """배치 감정 분석"""
        return [self.analyze(text, language) for text in texts]
    
    def get_summary(self, results: List[Dict]) -> Dict[str, Union[int, float]]:
        """분석 결과 요약"""
        if not results:
            return {}
        
        sentiments = [r['sentiment'] for r in results]
        scores = [r['score'] for r in results]
        
        sentiment_counts = Counter(sentiments)
        
        return {
            'total_count': len(results),
            'positive_count': sentiment_counts.get('positive', 0),
            'negative_count': sentiment_counts.get('negative', 0),
            'neutral_count': sentiment_counts.get('neutral', 0),
            'positive_ratio': sentiment_counts.get('positive', 0) / len(results),
            'negative_ratio': sentiment_counts.get('negative', 0) / len(results),
            'neutral_ratio': sentiment_counts.get('neutral', 0) / len(results),
            'average_score': sum(scores) / len(scores),
            'max_score': max(scores),
            'min_score': min(scores)
        }
    
    def compare_sentiments(self, text1: str, text2: str) -> Dict[str, any]:
        """두 텍스트의 감정 비교"""
        result1 = self.analyze(text1)
        result2 = self.analyze(text2)
        
        return {
            'text1_sentiment': result1['sentiment'],
            'text2_sentiment': result2['sentiment'],
            'score_difference': result1['score'] - result2['score'],
            'sentiment_changed': result1['sentiment'] != result2['sentiment'],
            'details': {
                'text1': result1,
                'text2': result2
            }
        }