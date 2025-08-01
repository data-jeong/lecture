# 65. LLM Engineering - LLM 엔지니어링

## 📚 과정 소개
광고 분야에 특화된 LLM(Large Language Model) 엔지니어링을 마스터합니다. 광고 카피 생성부터 고객 세분화, 개인화 추천까지 LLM을 활용한 지능형 광고 시스템을 구축합니다.

## 🎯 학습 목표
- 광고 도메인 LLM 파인튜닝
- RAG 기반 개인화 콘텐츠 생성
- 실시간 광고 카피 최적화
- LLM 기반 고객 인사이트 분석

## 📖 주요 내용

### 광고 특화 LLM 시스템
```python
import openai
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    GPT2LMHeadModel, GPT2Tokenizer,
    pipeline, Trainer, TrainingArguments
)
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json
import re
from datetime import datetime
import asyncio
import logging
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AdCopyRequest:
    """광고 카피 생성 요청"""
    product_name: str
    target_audience: str
    key_benefits: List[str]
    brand_voice: str  # professional, casual, luxury, etc.
    campaign_goal: str  # awareness, conversion, retention
    constraints: Dict[str, Any]  # character limits, forbidden words, etc.

@dataclass
class GeneratedAdCopy:
    """생성된 광고 카피"""
    headline: str
    description: str
    cta: str
    keywords: List[str]
    confidence_score: float
    metadata: Dict[str, Any]

class AdCopyGenerator:
    """AI 광고 카피 생성기"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        self.client = openai.OpenAI()
        
        # 광고 카피 템플릿
        self.copy_templates = {
            'awareness': {
                'headline_templates': [
                    "Discover {product_name} - {key_benefit}",
                    "New {product_name}: {key_benefit}",
                    "Meet {product_name} - The Future of {category}"
                ],
                'description_templates': [
                    "Experience {key_benefit} with {product_name}. {additional_benefits}",
                    "Transform your {category} experience with {product_name}."
                ]
            },
            'conversion': {
                'headline_templates': [
                    "Get {discount}% Off {product_name} Today!",
                    "Limited Time: {product_name} at {price}",
                    "Save Big on {product_name} - {key_benefit}"
                ],
                'description_templates': [
                    "Don't miss out! {product_name} offers {key_benefit}. {urgency_text}",
                    "Special offer: Get {product_name} and enjoy {key_benefit}. {cta_text}"
                ]
            },
            'retention': {
                'headline_templates': [
                    "Welcome Back! New {product_name} Features",
                    "Exclusive for You: {product_name} Premium",
                    "Your {product_name} Journey Continues"
                ]
            }
        }
        
    def generate_ad_copy(self, request: AdCopyRequest) -> GeneratedAdCopy:
        """광고 카피 생성"""
        # 프롬프트 구성
        prompt = self._build_prompt(request)
        
        # LLM 호출
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are an expert advertising copywriter specializing in performance marketing."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        # 응답 파싱
        generated_content = response.choices[0].message.content
        parsed_copy = self._parse_generated_copy(generated_content, request)
        
        # 품질 평가
        confidence_score = self._evaluate_copy_quality(parsed_copy, request)
        
        return GeneratedAdCopy(
            headline=parsed_copy['headline'],
            description=parsed_copy['description'],
            cta=parsed_copy['cta'],
            keywords=self._extract_keywords(parsed_copy, request),
            confidence_score=confidence_score,
            metadata={
                'model_used': self.model_name,
                'generation_time': datetime.now().isoformat(),
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens
            }
        )
    
    def _build_prompt(self, request: AdCopyRequest) -> str:
        """프롬프트 구성"""
        prompt = f"""
Create a compelling advertisement copy for the following product:

Product: {request.product_name}
Target Audience: {request.target_audience}
Key Benefits: {', '.join(request.key_benefits)}
Brand Voice: {request.brand_voice}
Campaign Goal: {request.campaign_goal}

Constraints:
"""
        
        for key, value in request.constraints.items():
            prompt += f"- {key}: {value}\n"
        
        prompt += """
Please generate:
1. Headline (attention-grabbing, max 60 characters)
2. Description (compelling, max 150 characters)
3. Call-to-action (action-oriented, max 25 characters)

Format your response as:
HEADLINE: [your headline]
DESCRIPTION: [your description]
CTA: [your call-to-action]
"""
        
        return prompt
    
    def _parse_generated_copy(self, content: str, request: AdCopyRequest) -> Dict[str, str]:
        """생성된 콘텐츠 파싱"""
        lines = content.strip().split('\n')
        parsed = {'headline': '', 'description': '', 'cta': ''}
        
        for line in lines:
            if line.startswith('HEADLINE:'):
                parsed['headline'] = line.replace('HEADLINE:', '').strip()
            elif line.startswith('DESCRIPTION:'):
                parsed['description'] = line.replace('DESCRIPTION:', '').strip()
            elif line.startswith('CTA:'):
                parsed['cta'] = line.replace('CTA:', '').strip()
        
        # 기본값 설정
        if not parsed['headline']:
            parsed['headline'] = f"Discover {request.product_name}"
        if not parsed['description']:
            parsed['description'] = f"Experience {request.key_benefits[0] if request.key_benefits else 'amazing benefits'}"
        if not parsed['cta']:
            parsed['cta'] = "Learn More"
        
        return parsed
    
    def _evaluate_copy_quality(self, copy: Dict[str, str], request: AdCopyRequest) -> float:
        """카피 품질 평가"""
        score = 0.0
        max_score = 100.0
        
        # 길이 제약 체크
        if len(copy['headline']) <= 60:
            score += 20
        if len(copy['description']) <= 150:
            score += 20
        if len(copy['cta']) <= 25:
            score += 20
        
        # 키워드 포함 체크
        all_text = f"{copy['headline']} {copy['description']} {copy['cta']}".lower()
        product_mentioned = request.product_name.lower() in all_text
        benefits_mentioned = any(benefit.lower() in all_text for benefit in request.key_benefits)
        
        if product_mentioned:
            score += 20
        if benefits_mentioned:
            score += 20
        
        return score / max_score
    
    def _extract_keywords(self, copy: Dict[str, str], request: AdCopyRequest) -> List[str]:
        """키워드 추출"""
        text = f"{copy['headline']} {copy['description']}"
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 기본 키워드에 추출된 중요 단어 추가
        keywords = [request.product_name.lower()]
        keywords.extend([benefit.lower() for benefit in request.key_benefits])
        
        # 추가 의미있는 키워드 추출 (간단한 휴리스틱)
        important_words = [word for word in words if len(word) > 4]
        keywords.extend(important_words[:5])  # 상위 5개
        
        return list(set(keywords))

class RAGAdSystem:
    """RAG 기반 광고 시스템"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        self.knowledge_base = {}
        
    def build_knowledge_base(self, documents: List[Dict[str, Any]]):
        """지식 베이스 구축"""
        texts = []
        metadatas = []
        
        for doc in documents:
            if doc['type'] == 'product_info':
                text = f"Product: {doc['name']}\nCategory: {doc['category']}\nFeatures: {', '.join(doc['features'])}\nBenefits: {', '.join(doc['benefits'])}"
            elif doc['type'] == 'customer_segment':
                text = f"Segment: {doc['name']}\nDemographics: {doc['demographics']}\nInterests: {', '.join(doc['interests'])}\nBehavior: {doc['behavior']}"
            elif doc['type'] == 'campaign_history':
                text = f"Campaign: {doc['name']}\nPerformance: CTR {doc['ctr']}, CVR {doc['cvr']}\nAudience: {doc['audience']}\nCreatives: {doc['creative_elements']}"
            else:
                text = doc.get('content', '')
            
            texts.append(text)
            metadatas.append(doc)
        
        # 벡터 스토어 생성
        self.vector_store = FAISS.from_texts(texts, self.embeddings, metadatas=metadatas)
        logger.info(f"Knowledge base built with {len(texts)} documents")
    
    def generate_personalized_ad(self, user_profile: Dict[str, Any], 
                                product_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """개인화된 광고 생성"""
        # 사용자 프로필 기반 쿼리 생성
        query = self._build_rag_query(user_profile, product_id, context)
        
        # 관련 문서 검색
        relevant_docs = self.vector_store.similarity_search(query, k=5)
        
        # 컨텍스트 구성
        context_text = self._build_context_from_docs(relevant_docs)
        
        # 개인화된 프롬프트 생성
        personalized_prompt = self._build_personalization_prompt(
            user_profile, context_text, product_id, context
        )
        
        # LLM으로 광고 생성
        llm = OpenAI(temperature=0.7)
        response = llm(personalized_prompt)
        
        return {
            'generated_ad': response,
            'relevant_context': [doc.page_content for doc in relevant_docs],
            'personalization_factors': self._extract_personalization_factors(user_profile),
            'confidence_score': self._calculate_rag_confidence(relevant_docs)
        }
    
    def _build_rag_query(self, user_profile: Dict, product_id: str, context: Dict) -> str:
        """RAG 쿼리 구성"""
        query_parts = [f"product {product_id}"]
        
        if 'interests' in user_profile:
            query_parts.append(f"interests: {', '.join(user_profile['interests'])}")
        
        if 'demographics' in user_profile:
            demo = user_profile['demographics']
            query_parts.append(f"age {demo.get('age', '')}")
            query_parts.append(f"gender {demo.get('gender', '')}")
        
        if 'behavior' in user_profile:
            query_parts.append(f"behavior: {user_profile['behavior']}")
        
        return " ".join(query_parts)

class AdPerformancePredictor:
    """광고 성과 예측기"""
    
    def __init__(self):
        self.prediction_model = None
        self.feature_extractor = AdFeatureExtractor()
        
    def predict_ad_performance(self, ad_copy: GeneratedAdCopy, 
                             target_audience: Dict[str, Any],
                             campaign_context: Dict[str, Any]) -> Dict[str, float]:
        """광고 성과 예측"""
        # 특성 추출
        features = self.feature_extractor.extract_features(ad_copy, target_audience, campaign_context)
        
        # 예측 수행 (간단한 휴리스틱 모델)
        predictions = {
            'predicted_ctr': self._predict_ctr(features),
            'predicted_cvr': self._predict_cvr(features),
            'predicted_engagement': self._predict_engagement(features),
            'predicted_reach': self._predict_reach(features)
        }
        
        return predictions
    
    def _predict_ctr(self, features: Dict[str, float]) -> float:
        """CTR 예측"""
        base_ctr = 0.02
        
        # 간단한 가중치 모델
        ctr_factors = {
            'headline_length_score': features.get('headline_length_score', 0) * 0.1,
            'keyword_relevance': features.get('keyword_relevance', 0) * 0.15,
            'sentiment_score': features.get('sentiment_score', 0) * 0.05,
            'audience_match': features.get('audience_match', 0) * 0.2
        }
        
        adjustment = sum(ctr_factors.values())
        predicted_ctr = base_ctr * (1 + adjustment)
        
        return min(max(predicted_ctr, 0.001), 0.15)  # 0.1% ~ 15% 범위
    
    def _predict_cvr(self, features: Dict[str, float]) -> float:
        """CVR 예측"""
        base_cvr = 0.05
        
        cvr_factors = {
            'cta_strength': features.get('cta_strength', 0) * 0.3,
            'benefit_clarity': features.get('benefit_clarity', 0) * 0.2,
            'urgency_score': features.get('urgency_score', 0) * 0.1
        }
        
        adjustment = sum(cvr_factors.values())
        predicted_cvr = base_cvr * (1 + adjustment)
        
        return min(max(predicted_cvr, 0.01), 0.3)  # 1% ~ 30% 범위
    
    def _predict_engagement(self, features: Dict[str, float]) -> float:
        """참여도 예측"""
        engagement_score = (
            features.get('emotional_appeal', 0) * 0.4 +
            features.get('visual_appeal', 0) * 0.3 +
            features.get('relevance_score', 0) * 0.3
        )
        
        return min(max(engagement_score, 0), 1)
    
    def _predict_reach(self, features: Dict[str, float]) -> float:
        """도달률 예측"""
        reach_factors = {
            'audience_size': features.get('audience_size', 0),
            'budget_efficiency': features.get('budget_efficiency', 0),
            'competition_level': 1 - features.get('competition_level', 0.5)
        }
        
        reach_score = sum(reach_factors.values()) / len(reach_factors)
        return min(max(reach_score, 0), 1)

class AdFeatureExtractor:
    """광고 특성 추출기"""
    
    def extract_features(self, ad_copy: GeneratedAdCopy, 
                        target_audience: Dict[str, Any],
                        campaign_context: Dict[str, Any]) -> Dict[str, float]:
        """특성 추출"""
        features = {}
        
        # 텍스트 특성
        features.update(self._extract_text_features(ad_copy))
        
        # 오디언스 매칭 특성
        features.update(self._extract_audience_features(ad_copy, target_audience))
        
        # 캠페인 컨텍스트 특성
        features.update(self._extract_context_features(campaign_context))
        
        return features
    
    def _extract_text_features(self, ad_copy: GeneratedAdCopy) -> Dict[str, float]:
        """텍스트 특성 추출"""
        headline = ad_copy.headline
        description = ad_copy.description
        cta = ad_copy.cta
        
        features = {
            'headline_length_score': self._normalize_length_score(len(headline), 60),
            'description_length_score': self._normalize_length_score(len(description), 150),
            'cta_length_score': self._normalize_length_score(len(cta), 25),
            'keyword_density': len(ad_copy.keywords) / max(len(headline.split()) + len(description.split()), 1),
            'sentiment_score': self._calculate_sentiment(f"{headline} {description}"),
            'urgency_score': self._detect_urgency(headline + " " + description + " " + cta),
            'cta_strength': self._evaluate_cta_strength(cta)
        }
        
        return features
    
    def _normalize_length_score(self, actual_length: int, optimal_length: int) -> float:
        """길이 점수 정규화"""
        if actual_length == 0:
            return 0
        
        ratio = actual_length / optimal_length
        if ratio <= 1:
            return ratio  # 최적 길이 이하면 비례 점수
        else:
            return max(0, 2 - ratio)  # 초과 시 감점
    
    def _calculate_sentiment(self, text: str) -> float:
        """감정 점수 계산 (간단한 휴리스틱)"""
        positive_words = ['amazing', 'incredible', 'fantastic', 'awesome', 'perfect', 'best', 'great', 'excellent']
        negative_words = ['bad', 'worst', 'terrible', 'awful', 'poor', 'disappointing']
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if len(words) == 0:
            return 0.5
        
        sentiment = (positive_count - negative_count) / len(words) + 0.5
        return max(0, min(1, sentiment))
    
    def _detect_urgency(self, text: str) -> float:
        """긴급성 감지"""
        urgency_phrases = ['limited time', 'today only', 'hurry', 'don\'t miss', 'last chance', 'expires soon']
        text_lower = text.lower()
        
        urgency_score = sum(1 for phrase in urgency_phrases if phrase in text_lower)
        return min(1, urgency_score / 3)  # 최대 3개 구문으로 정규화
    
    def _evaluate_cta_strength(self, cta: str) -> float:
        """CTA 강도 평가"""
        strong_ctas = ['buy now', 'get started', 'sign up', 'download', 'book now', 'order today']
        medium_ctas = ['learn more', 'find out', 'discover', 'explore']
        weak_ctas = ['click here', 'see more', 'visit']
        
        cta_lower = cta.lower()
        
        if any(strong in cta_lower for strong in strong_ctas):
            return 1.0
        elif any(medium in cta_lower for medium in medium_ctas):
            return 0.6
        elif any(weak in cta_lower for weak in weak_ctas):
            return 0.3
        else:
            return 0.5  # 기본값

class LLMAdOptimizer:
    """LLM 기반 광고 최적화"""
    
    def __init__(self):
        self.copy_generator = AdCopyGenerator()
        self.performance_predictor = AdPerformancePredictor()
        self.optimization_history = []
        
    def optimize_ad_campaign(self, initial_request: AdCopyRequest,
                           target_audience: Dict[str, Any],
                           campaign_budget: float,
                           optimization_rounds: int = 5) -> Dict[str, Any]:
        """광고 캠페인 최적화"""
        optimization_results = []
        best_ad = None
        best_score = 0
        
        for round_num in range(optimization_rounds):
            # 라운드별 요청 조정
            optimized_request = self._adjust_request_for_round(initial_request, round_num, optimization_results)
            
            # 광고 생성
            generated_ad = self.copy_generator.generate_ad_copy(optimized_request)
            
            # 성과 예측
            predicted_performance = self.performance_predictor.predict_ad_performance(
                generated_ad, target_audience, {'budget': campaign_budget}
            )
            
            # 종합 점수 계산
            composite_score = self._calculate_composite_score(predicted_performance)
            
            round_result = {
                'round': round_num + 1,
                'ad_copy': generated_ad,
                'predicted_performance': predicted_performance,
                'composite_score': composite_score,
                'request_adjustments': optimized_request.__dict__
            }
            
            optimization_results.append(round_result)
            
            # 최고 성과 업데이트
            if composite_score > best_score:
                best_score = composite_score
                best_ad = generated_ad
        
        return {
            'best_ad': best_ad,
            'best_score': best_score,
            'optimization_rounds': optimization_results,
            'improvement_summary': self._generate_improvement_summary(optimization_results)
        }
    
    def _adjust_request_for_round(self, base_request: AdCopyRequest, 
                                round_num: int, previous_results: List[Dict]) -> AdCopyRequest:
        """라운드별 요청 조정"""
        adjusted_request = AdCopyRequest(**base_request.__dict__)
        
        if round_num == 0:
            return adjusted_request
        
        # 이전 결과 분석
        if previous_results:
            last_result = previous_results[-1]
            performance = last_result['predicted_performance']
            
            # 성과에 따른 조정
            if performance['predicted_ctr'] < 0.02:
                # CTR이 낮으면 더 매력적인 헤드라인 요구
                adjusted_request.constraints['style'] = 'attention_grabbing'
            
            if performance['predicted_cvr'] < 0.05:
                # CVR이 낮으면 더 강한 CTA 요구
                adjusted_request.constraints['cta_style'] = 'urgent'
        
        return adjusted_request
    
    def _calculate_composite_score(self, performance: Dict[str, float]) -> float:
        """종합 점수 계산"""
        weights = {
            'predicted_ctr': 0.3,
            'predicted_cvr': 0.4,
            'predicted_engagement': 0.2,
            'predicted_reach': 0.1
        }
        
        composite_score = sum(
            performance[metric] * weight 
            for metric, weight in weights.items()
        )
        
        return composite_score

# 사용 예시
async def example_llm_ad_system():
    """LLM 광고 시스템 예시"""
    # 광고 카피 생성기 초기화
    copy_generator = AdCopyGenerator()
    
    # 샘플 요청
    ad_request = AdCopyRequest(
        product_name="AI Marketing Platform",
        target_audience="Digital marketers aged 25-45",
        key_benefits=["Increase ROI by 300%", "Automated campaign optimization", "Real-time insights"],
        brand_voice="professional",
        campaign_goal="conversion",
        constraints={
            "max_headline_length": 60,
            "max_description_length": 150,
            "forbidden_words": ["cheap", "free"]
        }
    )
    
    print("=== LLM 광고 카피 생성 ===")
    
    # 광고 카피 생성
    try:
        generated_ad = copy_generator.generate_ad_copy(ad_request)
        
        print(f"Headline: {generated_ad.headline}")
        print(f"Description: {generated_ad.description}")
        print(f"CTA: {generated_ad.cta}")
        print(f"Keywords: {generated_ad.keywords}")
        print(f"Confidence Score: {generated_ad.confidence_score:.2f}")
        
    except Exception as e:
        print(f"광고 생성 중 오류: {e}")
        # 폴백 광고 생성
        generated_ad = GeneratedAdCopy(
            headline="Boost Your Marketing ROI with AI",
            description="Our AI platform increases campaign performance by 300%. Get real-time insights and automated optimization.",
            cta="Start Free Trial",
            keywords=["ai", "marketing", "roi", "automation"],
            confidence_score=0.8,
            metadata={"fallback": True}
        )
    
    # 성과 예측
    print("\n=== 성과 예측 ===")
    predictor = AdPerformancePredictor()
    
    target_audience = {
        "demographics": {"age_range": [25, 45], "interests": ["marketing", "technology"]},
        "behavior": "high_engagement",
        "size": 100000
    }
    
    campaign_context = {
        "budget": 10000,
        "duration_days": 30,
        "competition_level": 0.7
    }
    
    predictions = predictor.predict_ad_performance(generated_ad, target_audience, campaign_context)
    
    print(f"Predicted CTR: {predictions['predicted_ctr']:.2%}")
    print(f"Predicted CVR: {predictions['predicted_cvr']:.2%}")
    print(f"Predicted Engagement: {predictions['predicted_engagement']:.2f}")
    print(f"Predicted Reach: {predictions['predicted_reach']:.2f}")
    
    # 최적화 실행
    print("\n=== 캠페인 최적화 ===")
    optimizer = LLMAdOptimizer()
    
    try:
        optimization_result = optimizer.optimize_ad_campaign(
            ad_request, target_audience, 10000, optimization_rounds=3
        )
        
        best_ad = optimization_result['best_ad']
        print(f"최적화된 헤드라인: {best_ad.headline}")
        print(f"최적화된 설명: {best_ad.description}")
        print(f"최적화된 CTA: {best_ad.cta}")
        print(f"최고 점수: {optimization_result['best_score']:.3f}")
        
    except Exception as e:
        print(f"최적화 중 오류: {e}")
    
    return {
        'generated_ad': generated_ad,
        'predictions': predictions,
        'success': True
    }

if __name__ == "__main__":
    # 비동기 실행
    import asyncio
    result = asyncio.run(example_llm_ad_system())
    print("LLM 광고 시스템 테스트 완료!")
```

## 🚀 프로젝트
1. **AI 광고 카피 생성 플랫폼**
2. **RAG 기반 개인화 광고 시스템**
3. **LLM 광고 성과 예측 엔진**
4. **실시간 광고 최적화 도구**