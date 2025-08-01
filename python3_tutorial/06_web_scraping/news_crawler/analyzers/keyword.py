"""
키워드 추출기
텍스트에서 주요 키워드 추출
"""

import re
from typing import List, Dict, Tuple, Set
from collections import Counter
import logging


class KeywordExtractor:
    """키워드 추출기"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 불용어 (한국어/영어)
        self.stopwords = {
            'ko': {
                '그', '그것', '그리고', '그런', '그럼', '그래서', '그러나', '그러면',
                '이', '이것', '이는', '이런', '이렇게', '있다', '있는', '있으며',
                '하다', '하는', '하지만', '하여', '한', '할', '함께', '했다',
                '것', '것은', '것이', '것을', '수', '및', '등', '의', '을', '를',
                '은', '는', '가', '이', '에', '에서', '으로', '로', '와', '과',
                '도', '만', '부터', '까지', '보다', '처럼', '같이', '위해',
                '때', '때문에', '경우', '통해', '대해', '대한', '관련', '따라',
                '위한', '위해서', '아니다', '없다', '같다', '되다', '라고', '다고'
            },
            'en': {
                'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
                'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
                'had', 'what', 'said', 'each', 'which', 'their', 'time', 'would',
                'there', 'been', 'many', 'may', 'these', 'some', 'very', 'when',
                'much', 'can', 'says', 'each', 'just', 'those', 'you', 'all',
                'any', 'your', 'how', 'them', 'than', 'his', 'her', 'him'
            }
        }
        
        # 키워드 패턴 (정규표현식)
        self.patterns = {
            'ko': {
                'noun_endings': r'[가-힣]+(?:이|가|을|를|에|의|로|으로|와|과|도|만|부터|까지|보다|처럼|같이)?',
                'compound_noun': r'[가-힣]{2,}(?:\s+[가-힣]{2,})*',
                'technical_term': r'[A-Z]{2,}|[가-힣]+[A-Z]+|[A-Z]+[가-힣]+'
            },
            'en': {
                'noun_phrase': r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*',
                'compound_word': r'[a-z]+-[a-z]+',
                'technical_term': r'[A-Z]{2,}|[a-z]+[A-Z]+[a-z]*'
            }
        }
    
    def extract(self, text: str, top_n: int = 20, language: str = 'auto') -> List[Tuple[str, int]]:
        """키워드 추출"""
        if not text:
            return []
        
        # 언어 감지
        if language == 'auto':
            language = self._detect_language(text)
        
        # 텍스트 전처리
        processed_text = self._preprocess_text(text)
        
        # 후보 키워드 추출
        candidates = self._extract_candidates(processed_text, language)
        
        # 키워드 점수 계산
        scored_keywords = self._calculate_scores(candidates, processed_text)
        
        # 상위 키워드 반환
        return scored_keywords[:top_n]
    
    def _detect_language(self, text: str) -> str:
        """언어 감지"""
        korean_chars = len(re.findall(r'[가-힣]', text))
        total_chars = len(re.findall(r'\w', text))
        
        if total_chars > 0:
            korean_ratio = korean_chars / total_chars
            if korean_ratio > 0.3:
                return 'ko'
        
        return 'en'
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # URL 제거
        text = re.sub(r'https?://\S+', '', text)
        
        # 이메일 제거
        text = re.sub(r'\S+@\S+', '', text)
        
        # 연속된 공백 정리
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_candidates(self, text: str, language: str) -> List[str]:
        """후보 키워드 추출"""
        candidates = []
        
        # 1. 단어 기반 추출
        words = self._extract_words(text, language)
        candidates.extend(words)
        
        # 2. 구문 기반 추출
        phrases = self._extract_phrases(text, language)
        candidates.extend(phrases)
        
        # 3. 패턴 기반 추출
        pattern_matches = self._extract_patterns(text, language)
        candidates.extend(pattern_matches)
        
        # 중복 제거 및 정리
        candidates = list(set(candidates))
        candidates = [c for c in candidates if self._is_valid_keyword(c, language)]
        
        return candidates
    
    def _extract_words(self, text: str, language: str) -> List[str]:
        """단어 추출"""
        # 기본 단어 분리
        if language == 'ko':
            # 한국어: 2글자 이상의 한글 단어
            words = re.findall(r'[가-힣]{2,}', text)
        else:
            # 영어: 3글자 이상의 영문 단어
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # 불용어 제거
        stopwords = self.stopwords.get(language, set())
        words = [w for w in words if w not in stopwords]
        
        return words
    
    def _extract_phrases(self, text: str, language: str) -> List[str]:
        """구문 추출"""
        phrases = []
        
        if language == 'ko':
            # 한국어 복합명사 패턴
            compound_nouns = re.findall(r'[가-힣]{2,}\s+[가-힣]{2,}', text)
            phrases.extend(compound_nouns)
            
            # 숫자와 명사 조합
            number_noun = re.findall(r'\d+[가-힣]{1,3}', text)
            phrases.extend(number_noun)
            
        else:
            # 영어 명사구 패턴
            noun_phrases = re.findall(r'\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*\b', text)
            phrases.extend(noun_phrases)
            
            # 형용사 + 명사 패턴
            adj_noun = re.findall(r'\b[a-z]+(?:ing|ed|ly)\s+[a-z]+\b', text.lower())
            phrases.extend(adj_noun)
        
        return phrases
    
    def _extract_patterns(self, text: str, language: str) -> List[str]:
        """패턴 기반 추출"""
        matches = []
        patterns = self.patterns.get(language, {})
        
        for pattern_name, pattern in patterns.items():
            found = re.findall(pattern, text)
            matches.extend(found)
        
        return matches
    
    def _is_valid_keyword(self, keyword: str, language: str) -> bool:
        """유효한 키워드인지 확인"""
        keyword = keyword.strip()
        
        # 최소 길이 확인
        if len(keyword) < 2:
            return False
        
        # 숫자만으로 구성된 키워드 제외
        if keyword.isdigit():
            return False
        
        # 특수문자만으로 구성된 키워드 제외
        if re.match(r'^[^\w가-힣]+$', keyword):
            return False
        
        # 불용어 확인
        stopwords = self.stopwords.get(language, set())
        if keyword.lower() in stopwords:
            return False
        
        return True
    
    def _calculate_scores(self, candidates: List[str], text: str) -> List[Tuple[str, int]]:
        """키워드 점수 계산"""
        # 빈도 계산
        keyword_counts = Counter(candidates)
        
        # TF 점수 계산
        total_words = len(text.split())
        tf_scores = {}
        
        for keyword, count in keyword_counts.items():
            tf = count / total_words
            
            # 키워드 길이 보너스
            length_bonus = min(len(keyword) / 10, 1.0)
            
            # 대문자 보너스 (고유명사)
            case_bonus = 1.2 if keyword[0].isupper() else 1.0
            
            # 복합어 보너스
            compound_bonus = 1.3 if ' ' in keyword else 1.0
            
            # 최종 점수
            score = tf * length_bonus * case_bonus * compound_bonus
            tf_scores[keyword] = score
        
        # 점수 기준 정렬
        sorted_keywords = sorted(tf_scores.items(), key=lambda x: x[1], reverse=True)
        
        # (키워드, 빈도) 형태로 반환
        return [(keyword, keyword_counts[keyword]) for keyword, score in sorted_keywords]
    
    def extract_from_multiple_texts(self, texts: List[str], top_n: int = 50) -> List[Tuple[str, int]]:
        """여러 텍스트에서 키워드 추출"""
        all_keywords = []
        
        for text in texts:
            keywords = self.extract(text, top_n=100)
            all_keywords.extend([kw for kw, count in keywords])
        
        # 전체 키워드 빈도 계산
        keyword_counts = Counter(all_keywords)
        
        return keyword_counts.most_common(top_n)
    
    def get_top_keywords(self, keyword_list: List[str], top_n: int = 20) -> List[Tuple[str, int]]:
        """키워드 리스트에서 상위 키워드 추출"""
        keyword_counts = Counter(keyword_list)
        return keyword_counts.most_common(top_n)
    
    def find_related_keywords(self, target_keyword: str, text: str, window_size: int = 5) -> List[str]:
        """특정 키워드와 관련된 키워드 찾기"""
        words = text.split()
        related = []
        
        for i, word in enumerate(words):
            if target_keyword.lower() in word.lower():
                # 윈도우 범위 내 단어들 수집
                start = max(0, i - window_size)
                end = min(len(words), i + window_size + 1)
                
                context_words = words[start:end]
                related.extend([w for w in context_words if w.lower() != target_keyword.lower()])
        
        # 빈도 기준 정렬
        related_counts = Counter(related)
        return [word for word, count in related_counts.most_common(10)]
    
    def extract_named_entities(self, text: str) -> Dict[str, List[str]]:
        """개체명 추출 (간단한 구현)"""
        entities = {
            'PERSON': [],
            'ORGANIZATION': [],
            'LOCATION': [],
            'DATE': [],
            'NUMBER': []
        }
        
        # 사람 이름 패턴 (한국어)
        person_pattern = r'[가-힣]{2,3}(?:\s+[가-힣]{1,2})*(?:\s+(?:씨|님|박사|교수|대표|회장|사장))?'
        persons = re.findall(person_pattern, text)
        entities['PERSON'].extend(persons)
        
        # 조직 패턴
        org_pattern = r'[가-힣]+(?:회사|기업|그룹|법인|재단|협회|대학교|대학|학교|병원|연구소)'
        orgs = re.findall(org_pattern, text)
        entities['ORGANIZATION'].extend(orgs)
        
        # 지명 패턴
        location_pattern = r'[가-힣]+(?:시|도|구|군|동|리|읍|면|로|길|대로)'
        locations = re.findall(location_pattern, text)
        entities['LOCATION'].extend(locations)
        
        # 날짜 패턴
        date_pattern = r'\d{4}년\s*\d{1,2}월\s*\d{1,2}일|\d{1,2}월\s*\d{1,2}일|\d{4}-\d{2}-\d{2}'
        dates = re.findall(date_pattern, text)
        entities['DATE'].extend(dates)
        
        # 숫자 패턴
        number_pattern = r'\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:원|달러|엔|유로|억|만|천|개|명|대|건))?'
        numbers = re.findall(number_pattern, text)
        entities['NUMBER'].extend(numbers)
        
        # 중복 제거
        for category in entities:
            entities[category] = list(set(entities[category]))
        
        return entities