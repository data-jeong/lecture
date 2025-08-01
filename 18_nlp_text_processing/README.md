# 18. NLP Text Processing - 자연어 처리

## 📚 과정 소개
마케팅 및 광고 도메인에 특화된 자연어 처리 기술을 학습합니다. 광고 카피 분석, 감정 분석, 키워드 추출, 자동 카피 생성까지 포괄적으로 다룹니다.

## 🎯 학습 목표
- 광고 텍스트 전처리 및 분석
- 감정 분석으로 브랜드 모니터링
- 키워드 추출 및 토픽 모델링
- 자동 광고 카피 생성

## 📖 주요 내용

### 광고 텍스트 전처리
```python
import re
import nltk
from konlpy.tag import Okt, Mecab
from typing import List, Dict, Tuple
import numpy as np
from collections import Counter

class AdTextPreprocessor:
    """광고 텍스트 전처리기"""
    
    def __init__(self, language='ko'):
        self.language = language
        if language == 'ko':
            self.tokenizer = Okt()
        else:
            nltk.download('punkt')
            nltk.download('stopwords')
            from nltk.corpus import stopwords
            self.stop_words = set(stopwords.words('english'))
    
    def clean_text(self, text: str) -> str:
        """텍스트 정제"""
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # URL 제거
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 이메일 제거
        text = re.sub(r'\S+@\S+', '', text)
        
        # 특수문자 정리 (한글, 영문, 숫자, 공백만 유지)
        if self.language == 'ko':
            text = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', text)
        else:
            text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        
        # 연속 공백 제거
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """토큰화"""
        if self.language == 'ko':
            # 명사, 형용사, 동사만 추출
            tokens = self.tokenizer.pos(text, stem=True)
            return [word for word, pos in tokens if pos in ['Noun', 'Adjective', 'Verb'] and len(word) > 1]
        else:
            from nltk.tokenize import word_tokenize
            tokens = word_tokenize(text.lower())
            return [word for word in tokens if word not in self.stop_words and len(word) > 2]
    
    def extract_ngrams(self, tokens: List[str], n: int = 2) -> List[str]:
        """N-gram 추출"""
        if len(tokens) < n:
            return []
        return [' '.join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
    
    def preprocess_ad_copy(self, text: str) -> Dict:
        """광고 카피 전처리 (전체 파이프라인)"""
        # 정제
        cleaned = self.clean_text(text)
        
        # 토큰화
        tokens = self.tokenize(cleaned)
        
        # N-gram 추출
        bigrams = self.extract_ngrams(tokens, 2)
        trigrams = self.extract_ngrams(tokens, 3)
        
        return {
            'original': text,
            'cleaned': cleaned,
            'tokens': tokens,
            'bigrams': bigrams,
            'trigrams': trigrams,
            'token_count': len(tokens),
            'unique_tokens': len(set(tokens))
        }
```

### 감정 분석 시스템
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from torch.nn.functional import softmax

class SentimentAnalyzer:
    """감정 분석기 (브랜드 모니터링용)"""
    
    def __init__(self, model_name='klue/roberta-base'):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # 감정 레이블
        self.sentiment_labels = ['매우 부정', '부정', '중립', '긍정', '매우 긍정']
    
    def analyze_sentiment(self, text: str) -> Dict:
        """단일 텍스트 감정 분석"""
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            truncation=True,
            padding=True,
            max_length=512
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = softmax(outputs.logits, dim=-1)
            
        pred_label_idx = torch.argmax(probabilities, dim=-1).item()
        confidence = probabilities[0][pred_label_idx].item()
        
        return {
            'sentiment': self.sentiment_labels[pred_label_idx],
            'confidence': confidence,
            'probabilities': {
                label: prob.item() 
                for label, prob in zip(self.sentiment_labels, probabilities[0])
            }
        }
    
    def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """배치 감정 분석"""
        results = []
        for text in texts:
            results.append(self.analyze_sentiment(text))
        return results
    
    def analyze_brand_mentions(self, texts: List[str], brand_keywords: List[str]) -> Dict:
        """브랜드 언급 감정 분석"""
        brand_mentions = []
        
        for text in texts:
            # 브랜드 키워드가 포함된 텍스트만 필터링
            if any(keyword.lower() in text.lower() for keyword in brand_keywords):
                sentiment = self.analyze_sentiment(text)
                brand_mentions.append({
                    'text': text,
                    'sentiment': sentiment['sentiment'],
                    'confidence': sentiment['confidence']
                })
        
        if not brand_mentions:
            return {'message': '브랜드 언급을 찾을 수 없습니다.'}
        
        # 감정 분포 계산
        sentiment_counts = Counter([mention['sentiment'] for mention in brand_mentions])
        total_mentions = len(brand_mentions)
        
        return {
            'total_mentions': total_mentions,
            'sentiment_distribution': {
                sentiment: count / total_mentions * 100
                for sentiment, count in sentiment_counts.items()
            },
            'detailed_mentions': brand_mentions[:10],  # 상위 10개만
            'overall_sentiment_score': self._calculate_sentiment_score(sentiment_counts)
        }
    
    def _calculate_sentiment_score(self, sentiment_counts: Counter) -> float:
        """전체 감정 점수 계산 (-2 ~ +2)"""
        weights = {'매우 부정': -2, '부정': -1, '중립': 0, '긍정': 1, '매우 긍정': 2}
        total_weighted = sum(weights[sentiment] * count for sentiment, count in sentiment_counts.items())
        total_count = sum(sentiment_counts.values())
        return total_weighted / total_count if total_count > 0 else 0
```

### 키워드 추출 및 토픽 모델링
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import networkx as nx
from textrank import TextRank4Keyword

class KeywordExtractor:
    """키워드 추출기"""
    
    def __init__(self):
        self.preprocessor = AdTextPreprocessor()
        
    def extract_tfidf_keywords(self, documents: List[str], top_k: int = 10) -> Dict:
        """TF-IDF 기반 키워드 추출"""
        # 전처리
        processed_docs = []
        for doc in documents:
            tokens = self.preprocessor.tokenize(self.preprocessor.clean_text(doc))
            processed_docs.append(' '.join(tokens))
        
        # TF-IDF 벡터화
        vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        
        tfidf_matrix = vectorizer.fit_transform(processed_docs)
        feature_names = vectorizer.get_feature_names_out()
        
        # 평균 TF-IDF 점수 계산
        mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
        keyword_scores = list(zip(feature_names, mean_scores))
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'keywords': keyword_scores[:top_k],
            'total_documents': len(documents),
            'vocabulary_size': len(feature_names)
        }
    
    def extract_textrank_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """TextRank 기반 키워드 추출"""
        tr4w = TextRank4Keyword()
        tr4w.analyze(text, candidate_pos=['NOUN', 'PROPN'], window_size=4, lower=False)
        
        keywords = tr4w.get_keywords(top_k)
        return [(kw, score) for kw, score in keywords]
    
    def extract_campaign_keywords(self, campaign_texts: List[str], 
                                 performance_data: List[Dict]) -> Dict:
        """캠페인별 성과 기반 키워드 추출"""
        # 성과 기준으로 텍스트 그룹화
        high_performance = []
        low_performance = []
        
        for text, perf in zip(campaign_texts, performance_data):
            if perf['ctr'] > np.median([p['ctr'] for p in performance_data]):
                high_performance.append(text)
            else:
                low_performance.append(text)
        
        # 각 그룹별 키워드 추출
        high_perf_keywords = self.extract_tfidf_keywords(high_performance)
        low_perf_keywords = self.extract_tfidf_keywords(low_performance)
        
        # 성과 차이 분석
        high_kw_set = set([kw[0] for kw in high_perf_keywords['keywords']])
        low_kw_set = set([kw[0] for kw in low_perf_keywords['keywords']])
        
        return {
            'high_performance_unique': list(high_kw_set - low_kw_set),
            'low_performance_unique': list(low_kw_set - high_kw_set),
            'common_keywords': list(high_kw_set & low_kw_set),
            'high_performance_keywords': high_perf_keywords['keywords'],
            'low_performance_keywords': low_perf_keywords['keywords']
        }

class TopicModeler:
    """토픽 모델링"""
    
    def __init__(self, n_topics: int = 5):
        self.n_topics = n_topics
        self.preprocessor = AdTextPreprocessor()
        
    def fit_lda(self, documents: List[str]) -> Dict:
        """LDA 토픽 모델링"""
        # 전처리
        processed_docs = []
        for doc in documents:
            tokens = self.preprocessor.tokenize(self.preprocessor.clean_text(doc))
            processed_docs.append(' '.join(tokens))
        
        # 벡터화
        vectorizer = TfidfVectorizer(
            max_features=1000,
            min_df=2,
            max_df=0.8,
            stop_words=None
        )
        
        doc_term_matrix = vectorizer.fit_transform(processed_docs)
        
        # LDA 학습
        lda = LatentDirichletAllocation(
            n_components=self.n_topics,
            random_state=42,
            max_iter=100
        )
        
        lda.fit(doc_term_matrix)
        
        # 토픽별 주요 단어 추출
        feature_names = vectorizer.get_feature_names_out()
        topics = []
        
        for topic_idx, topic in enumerate(lda.components_):
            top_words_idx = topic.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            top_scores = [topic[i] for i in top_words_idx]
            
            topics.append({
                'topic_id': topic_idx,
                'words': list(zip(top_words, top_scores)),
                'weight': topic.sum()
            })
        
        # 문서별 토픽 분포
        doc_topic_matrix = lda.transform(doc_term_matrix)
        
        return {
            'topics': topics,
            'document_topic_distribution': doc_topic_matrix,
            'perplexity': lda.perplexity(doc_term_matrix),
            'log_likelihood': lda.score(doc_term_matrix)
        }
```

### 자동 광고 카피 생성
```python
from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline

class AdCopyGenerator:
    """광고 카피 자동 생성기"""
    
    def __init__(self, model_name='skt/kogpt2-base-v2'):
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.generator = pipeline('text-generation', 
                                 model=self.model,
                                 tokenizer=self.tokenizer)
        
        # 광고 카피 템플릿
        self.templates = [
            "{product}로 {benefit}을 경험하세요!",
            "지금 {product} {discount}% 할인!",
            "{target_audience}를 위한 특별한 {product}",
            "{problem}에 지친 당신, {product}가 해답입니다",
            "한정 특가! {product} {action} 기회"
        ]
    
    def generate_copy_variants(self, product: str, keywords: List[str], 
                              target_audience: str = "", num_variants: int = 5) -> List[Dict]:
        """카피 변형 생성"""
        base_prompt = f"{product} 광고 카피: "
        if target_audience:
            base_prompt += f"{target_audience} 대상, "
        base_prompt += f"키워드: {', '.join(keywords[:3])}"
        
        variants = []
        
        # GPT 기반 생성
        for i in range(num_variants):
            generated = self.generator(
                base_prompt,
                max_length=50,
                num_return_sequences=1,
                temperature=0.8,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # 후처리
            text = generated[0]['generated_text'].replace(base_prompt, '').strip()
            text = self._clean_generated_text(text)
            
            variants.append({
                'copy': text,
                'method': 'gpt_generation',
                'score': self._score_copy(text, keywords)
            })
        
        # 템플릿 기반 생성
        for template in self.templates[:3]:
            try:
                filled_template = self._fill_template(template, product, keywords, target_audience)
                variants.append({
                    'copy': filled_template,
                    'method': 'template_based',
                    'score': self._score_copy(filled_template, keywords)
                })
            except:
                continue
        
        # 점수 기준 정렬
        variants.sort(key=lambda x: x['score'], reverse=True)
        return variants[:num_variants]
    
    def _clean_generated_text(self, text: str) -> str:
        """생성된 텍스트 정제"""
        # 불완전한 문장 제거
        sentences = text.split('.')
        if len(sentences) > 1:
            text = sentences[0] + '.'
        
        # 특수문자 정리
        text = re.sub(r'[^\w\s!?.,()%]', '', text)
        return text.strip()
    
    def _fill_template(self, template: str, product: str, 
                      keywords: List[str], target_audience: str) -> str:
        """템플릿 채우기"""
        replacements = {
            'product': product,
            'benefit': keywords[0] if keywords else '만족',
            'discount': np.random.choice([10, 20, 30, 50]),
            'target_audience': target_audience or '고객',
            'problem': keywords[1] if len(keywords) > 1 else '고민',
            'action': np.random.choice(['구매', '체험', '문의'])
        }
        
        for key, value in replacements.items():
            template = template.replace(f'{{{key}}}', str(value))
        
        return template
    
    def _score_copy(self, copy: str, keywords: List[str]) -> float:
        """카피 품질 점수 계산"""
        score = 0
        
        # 키워드 포함 점수
        for keyword in keywords:
            if keyword.lower() in copy.lower():
                score += 1
        
        # 길이 점수 (15-50자 적정)
        length = len(copy)
        if 15 <= length <= 50:
            score += 2
        elif 10 <= length <= 60:
            score += 1
        
        # 감정 표현 점수
        emotional_words = ['특별한', '놀라운', '혁신적인', '최고의', '완벽한', '새로운']
        for word in emotional_words:
            if word in copy:
                score += 0.5
        
        # CTA 포함 점수
        cta_words = ['지금', '오늘', '바로', '즉시', '클릭', '구매', '체험']
        for word in cta_words:
            if word in copy:
                score += 1
                break
        
        return score
    
    def optimize_for_platform(self, copy: str, platform: str) -> str:
        """플랫폼별 최적화"""
        if platform.lower() == 'facebook':
            # Facebook: 개인적이고 스토리텔링
            return f"친구들아! {copy} 진짜 추천해!"
        elif platform.lower() == 'google':
            # Google: 직접적이고 검색 친화적
            return copy.replace('!', '').replace('?', '') + ' | 할인가격 확인'
        elif platform.lower() == 'instagram':
            # Instagram: 해시태그 추가
            hashtags = ['#특가', '#할인', '#추천', '#광고']
            return f"{copy} {' '.join(hashtags[:2])}"
        else:
            return copy
```

## 🚀 프로젝트
1. **브랜드 모니터링 감정 분석 시스템**
2. **자동 광고 카피 생성 플랫폼**
3. **경쟁사 키워드 분석 도구**
4. **다국어 광고 번역 및 현지화**