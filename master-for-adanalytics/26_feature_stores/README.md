# 26. Feature Stores - 피처 스토어

## 📚 과정 소개
광고 머신러닝을 위한 피처 스토어 아키텍처를 마스터합니다. 실시간 특성 서빙, 특성 파이프라인, 데이터 품질 관리까지 포괄적인 MLOps 피처 관리 시스템을 구축합니다.

## 🎯 학습 목표
- 대규모 피처 파이프라인 구축
- 실시간 피처 서빙 시스템
- 피처 드리프트 모니터링
- A/B 테스트용 피처 관리

## 📖 주요 내용

### 광고 피처 스토어 시스템
```python
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import logging
import redis
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import time
from collections import defaultdict
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

@dataclass
class FeatureDefinition:
    """피처 정의 클래스"""
    name: str
    description: str
    feature_type: str  # categorical, numerical, binary, embedding
    data_source: str
    computation_logic: str
    update_frequency: str  # real_time, hourly, daily, weekly
    version: str
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class FeatureValue:
    """피처 값 클래스"""
    entity_id: str
    feature_name: str
    value: Union[float, int, str, List]
    timestamp: datetime
    version: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class FeatureRegistry(Base):
    """피처 레지스트리 테이블"""
    __tablename__ = 'feature_registry'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    feature_type = Column(String(50))
    data_source = Column(String(255))
    computation_logic = Column(Text)
    update_frequency = Column(String(50))
    version = Column(String(50))
    tags = Column(Text)  # JSON string
    dependencies = Column(Text)  # JSON string
    validation_rules = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)

class FeatureStore:
    """피처 스토어 관리자"""
    
    def __init__(self, database_url: str = "sqlite:///feature_store.db",
                 redis_host: str = "localhost", redis_port: int = 6379):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Redis 연결 (실시간 피처 서빙용)
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis 연결 성공")
        except Exception as e:
            logger.warning(f"Redis 연결 실패: {e}")
            self.redis_client = None
        
        # 피처 캐시
        self.feature_cache = {}
        self.feature_definitions = {}
        
        # 실행자 풀
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        self.load_feature_definitions()
    
    def register_feature(self, feature_def: FeatureDefinition) -> bool:
        """피처 등록"""
        try:
            feature_registry = FeatureRegistry(
                name=feature_def.name,
                description=feature_def.description,
                feature_type=feature_def.feature_type,
                data_source=feature_def.data_source,
                computation_logic=feature_def.computation_logic,
                update_frequency=feature_def.update_frequency,
                version=feature_def.version,
                tags=json.dumps(feature_def.tags),
                dependencies=json.dumps(feature_def.dependencies),
                validation_rules=json.dumps(feature_def.validation_rules)
            )
            
            # 기존 피처 비활성화
            existing = self.session.query(FeatureRegistry).filter_by(name=feature_def.name).first()
            if existing:
                existing.is_active = False
            
            self.session.add(feature_registry)
            self.session.commit()
            
            # 메모리 캐시 업데이트
            self.feature_definitions[feature_def.name] = feature_def
            
            logger.info(f"피처 등록 완료: {feature_def.name}")
            return True
            
        except Exception as e:
            logger.error(f"피처 등록 실패 {feature_def.name}: {e}")
            self.session.rollback()
            return False
    
    def load_feature_definitions(self):
        """피처 정의 로드"""
        try:
            features = self.session.query(FeatureRegistry).filter_by(is_active=True).all()
            
            for feature in features:
                feature_def = FeatureDefinition(
                    name=feature.name,
                    description=feature.description,
                    feature_type=feature.feature_type,
                    data_source=feature.data_source,
                    computation_logic=feature.computation_logic,
                    update_frequency=feature.update_frequency,
                    version=feature.version,
                    tags=json.loads(feature.tags) if feature.tags else [],
                    dependencies=json.loads(feature.dependencies) if feature.dependencies else [],
                    validation_rules=json.loads(feature.validation_rules) if feature.validation_rules else {},
                    created_at=feature.created_at,
                    updated_at=feature.updated_at
                )
                
                self.feature_definitions[feature.name] = feature_def
            
            logger.info(f"피처 정의 로드 완료: {len(self.feature_definitions)}개")
            
        except Exception as e:
            logger.error(f"피처 정의 로드 실패: {e}")
    
    def get_feature_definition(self, feature_name: str) -> Optional[FeatureDefinition]:
        """피처 정의 조회"""
        return self.feature_definitions.get(feature_name)
    
    def list_features(self, tags: List[str] = None) -> List[FeatureDefinition]:
        """피처 목록 조회"""
        features = list(self.feature_definitions.values())
        
        if tags:
            features = [f for f in features if any(tag in f.tags for tag in tags)]
        
        return features

class AdFeatureComputer:
    """광고 피처 계산기"""
    
    def __init__(self, feature_store: FeatureStore):
        self.feature_store = feature_store
        self.computation_functions = {
            'user_ctr': self._compute_user_ctr,
            'user_cvr': self._compute_user_cvr,
            'user_ltv': self._compute_user_ltv,
            'user_engagement_score': self._compute_user_engagement,
            'user_recency': self._compute_user_recency,
            'user_frequency': self._compute_user_frequency,
            'user_monetary': self._compute_user_monetary,
            'campaign_performance': self._compute_campaign_performance,
            'ad_quality_score': self._compute_ad_quality_score,
            'audience_similarity': self._compute_audience_similarity,
            'seasonal_factor': self._compute_seasonal_factor,
            'device_preference': self._compute_device_preference,
            'time_of_day_factor': self._compute_time_factor,
            'keyword_relevance': self._compute_keyword_relevance,
            'competitor_pressure': self._compute_competitor_pressure
        }
    
    def compute_feature(self, feature_name: str, entity_id: str, 
                       context: Dict[str, Any] = None) -> Optional[FeatureValue]:
        """개별 피처 계산"""
        if feature_name not in self.computation_functions:
            logger.error(f"알 수 없는 피처: {feature_name}")
            return None
        
        try:
            feature_def = self.feature_store.get_feature_definition(feature_name)
            if not feature_def:
                logger.error(f"피처 정의를 찾을 수 없음: {feature_name}")
                return None
            
            # 피처 계산
            computation_func = self.computation_functions[feature_name]
            value = computation_func(entity_id, context or {})
            
            feature_value = FeatureValue(
                entity_id=entity_id,
                feature_name=feature_name,
                value=value,
                timestamp=datetime.now(),
                version=feature_def.version,
                metadata={'computation_context': context}
            )
            
            return feature_value
            
        except Exception as e:
            logger.error(f"피처 계산 실패 {feature_name}: {e}")
            return None
    
    def compute_feature_set(self, feature_names: List[str], entity_id: str,
                          context: Dict[str, Any] = None) -> Dict[str, FeatureValue]:
        """피처 셋 일괄 계산"""
        results = {}
        
        # 의존성 정렬
        sorted_features = self._sort_by_dependencies(feature_names)
        
        for feature_name in sorted_features:
            feature_value = self.compute_feature(feature_name, entity_id, context)
            if feature_value:
                results[feature_name] = feature_value
                # 컨텍스트에 계산된 피처 추가 (의존성 처리용)
                if context is None:
                    context = {}
                context[f"computed_{feature_name}"] = feature_value.value
        
        return results
    
    def _sort_by_dependencies(self, feature_names: List[str]) -> List[str]:
        """의존성에 따른 피처 정렬"""
        # 간단한 토폴로지 정렬 구현
        sorted_features = []
        remaining = feature_names.copy()
        
        while remaining:
            # 의존성이 없거나 모든 의존성이 해결된 피처 찾기
            ready_features = []
            for feature_name in remaining:
                feature_def = self.feature_store.get_feature_definition(feature_name)
                if not feature_def or not feature_def.dependencies:
                    ready_features.append(feature_name)
                else:
                    # 모든 의존성이 이미 처리되었는지 확인
                    deps_resolved = all(dep in sorted_features for dep in feature_def.dependencies 
                                      if dep in feature_names)
                    if deps_resolved:
                        ready_features.append(feature_name)
            
            if not ready_features:
                # 순환 의존성이 있을 수 있으므로 나머지를 그대로 추가
                sorted_features.extend(remaining)
                break
            
            sorted_features.extend(ready_features)
            remaining = [f for f in remaining if f not in ready_features]
        
        return sorted_features
    
    # 개별 피처 계산 함수들
    def _compute_user_ctr(self, user_id: str, context: Dict[str, Any]) -> float:
        """사용자 CTR 계산"""
        # 실제 구현에서는 데이터베이스에서 사용자의 과거 클릭/노출 데이터를 조회
        # 여기서는 시뮬레이션
        np.random.seed(hash(user_id) % 2**32)
        base_ctr = np.random.uniform(0.01, 0.15)
        
        # 컨텍스트 요인 반영
        if context.get('device_type') == 'mobile':
            base_ctr *= 1.2
        if context.get('time_of_day', 12) in [19, 20, 21]:  # 저녁 시간대
            base_ctr *= 1.1
        
        return round(base_ctr, 4)
    
    def _compute_user_cvr(self, user_id: str, context: Dict[str, Any]) -> float:
        """사용자 CVR 계산"""
        np.random.seed(hash(user_id + "cvr") % 2**32)
        base_cvr = np.random.uniform(0.005, 0.08)
        
        # 구매력 지표 반영
        if context.get('income_level') == 'high':
            base_cvr *= 1.5
        elif context.get('income_level') == 'low':
            base_cvr *= 0.7
        
        return round(base_cvr, 4)
    
    def _compute_user_ltv(self, user_id: str, context: Dict[str, Any]) -> float:
        """사용자 생애가치 계산"""
        np.random.seed(hash(user_id + "ltv") % 2**32)
        base_ltv = np.random.uniform(50, 2000)
        
        # 사용자 행동 패턴 반영
        engagement_score = context.get('computed_user_engagement_score', 0.5)
        base_ltv *= (1 + engagement_score)
        
        return round(base_ltv, 2)
    
    def _compute_user_engagement(self, user_id: str, context: Dict[str, Any]) -> float:
        """사용자 참여도 점수 계산"""
        np.random.seed(hash(user_id + "engagement") % 2**32)
        
        # 다양한 참여 지표 종합
        factors = {
            'session_duration': np.random.uniform(0, 1),
            'page_views': np.random.uniform(0, 1),  
            'interaction_rate': np.random.uniform(0, 1),
            'return_frequency': np.random.uniform(0, 1)
        }
        
        engagement_score = sum(factors.values()) / len(factors)
        return round(engagement_score, 3)
    
    def _compute_user_recency(self, user_id: str, context: Dict[str, Any]) -> int:
        """사용자 최근성 (마지막 활동 이후 일수)"""
        np.random.seed(hash(user_id + "recency") % 2**32)
        return np.random.randint(0, 365)  # 0-365일
    
    def _compute_user_frequency(self, user_id: str, context: Dict[str, Any]) -> int:
        """사용자 빈도 (30일간 활동 일수)"""
        np.random.seed(hash(user_id + "frequency") % 2**32)
        return np.random.randint(1, 31)  # 1-30일
    
    def _compute_user_monetary(self, user_id: str, context: Dict[str, Any]) -> float:
        """사용자 구매력 (30일간 구매 금액)"""
        np.random.seed(hash(user_id + "monetary") % 2**32)
        return round(np.random.uniform(0, 5000), 2)
    
    def _compute_campaign_performance(self, campaign_id: str, context: Dict[str, Any]) -> Dict[str, float]:
        """캠페인 성과 지표"""
        np.random.seed(hash(campaign_id) % 2**32)
        return {
            'ctr': round(np.random.uniform(0.01, 0.1), 4),
            'cvr': round(np.random.uniform(0.01, 0.05), 4),
            'roas': round(np.random.uniform(1.0, 8.0), 2),
            'quality_score': round(np.random.uniform(1, 10), 1)
        }
    
    def _compute_ad_quality_score(self, ad_id: str, context: Dict[str, Any]) -> float:
        """광고 품질 점수"""
        np.random.seed(hash(ad_id) % 2**32)
        return round(np.random.uniform(1, 10), 1)
    
    def _compute_audience_similarity(self, user_id: str, context: Dict[str, Any]) -> float:
        """오디언스 유사도"""
        target_audience = context.get('target_audience', {})
        user_profile = context.get('user_profile', {})
        
        # 간단한 유사도 계산
        similarity_score = 0.5  # 기본값
        
        if target_audience.get('age_group') == user_profile.get('age_group'):
            similarity_score += 0.2
        if target_audience.get('gender') == user_profile.get('gender'):
            similarity_score += 0.1
        if any(interest in user_profile.get('interests', []) 
               for interest in target_audience.get('interests', [])):
            similarity_score += 0.2
        
        return round(min(similarity_score, 1.0), 3)
    
    def _compute_seasonal_factor(self, entity_id: str, context: Dict[str, Any]) -> float:
        """계절성 요인"""
        current_month = datetime.now().month
        
        # 월별 계절성 팩터 (예: 11-12월 높음)
        seasonal_factors = {
            1: 0.8, 2: 0.7, 3: 0.9, 4: 1.0, 5: 1.1, 6: 1.2,
            7: 1.1, 8: 1.0, 9: 0.9, 10: 1.0, 11: 1.3, 12: 1.4
        }
        
        return seasonal_factors.get(current_month, 1.0)
    
    def _compute_device_preference(self, user_id: str, context: Dict[str, Any]) -> str:
        """디바이스 선호도"""
        np.random.seed(hash(user_id + "device") % 2**32)
        return np.random.choice(['mobile', 'desktop', 'tablet'], p=[0.6, 0.3, 0.1])
    
    def _compute_time_factor(self, entity_id: str, context: Dict[str, Any]) -> float:
        """시간대별 요인"""
        current_hour = datetime.now().hour
        
        # 시간대별 활동 팩터
        if 9 <= current_hour <= 12:  # 오전
            return 1.1
        elif 13 <= current_hour <= 18:  # 오후
            return 1.2
        elif 19 <= current_hour <= 22:  # 저녁
            return 1.3
        else:  # 새벽/밤
            return 0.8
    
    def _compute_keyword_relevance(self, entity_id: str, context: Dict[str, Any]) -> float:
        """키워드 관련성"""
        keywords = context.get('keywords', [])
        user_interests = context.get('user_interests', [])
        
        if not keywords or not user_interests:
            return 0.5
        
        # 키워드와 관심사 매칭
        matches = sum(1 for keyword in keywords if keyword in user_interests)
        relevance = matches / len(keywords)
        
        return round(relevance, 3)
    
    def _compute_competitor_pressure(self, entity_id: str, context: Dict[str, Any]) -> float:
        """경쟁 압박도"""
        # 카테고리별 경쟁 압박도 시뮬레이션
        category = context.get('category', 'general')
        
        pressure_map = {
            'electronics': 0.8,
            'fashion': 0.7,
            'automotive': 0.6,
            'finance': 0.9,
            'general': 0.5
        }
        
        return pressure_map.get(category, 0.5)

class RealTimeFeatureServer:
    """실시간 피처 서빙 서버"""
    
    def __init__(self, feature_store: FeatureStore, feature_computer: AdFeatureComputer):
        self.feature_store = feature_store
        self.feature_computer = feature_computer
        self.cache_ttl = 3600  # 1시간 캐시
    
    def get_features(self, entity_id: str, feature_names: List[str],
                    context: Dict[str, Any] = None) -> Dict[str, Any]:
        """피처 조회 (캐시 우선)"""
        results = {}
        missing_features = []
        
        # Redis 캐시에서 조회
        if self.feature_store.redis_client:
            for feature_name in feature_names:
                cache_key = f"feature:{entity_id}:{feature_name}"
                cached_value = self.feature_store.redis_client.get(cache_key)
                
                if cached_value:
                    try:
                        feature_value = pickle.loads(cached_value.encode('latin1'))
                        results[feature_name] = feature_value
                    except Exception as e:
                        logger.warning(f"캐시 디시리얼라이제이션 실패 {cache_key}: {e}")
                        missing_features.append(feature_name)
                else:
                    missing_features.append(feature_name)
        else:
            missing_features = feature_names
        
        # 캐시에 없는 피처들 계산
        if missing_features:
            computed_features = self.feature_computer.compute_feature_set(
                missing_features, entity_id, context
            )
            
            # 결과 병합 및 캐시 저장
            for feature_name, feature_value in computed_features.items():
                results[feature_name] = feature_value
                
                # Redis에 캐시
                if self.feature_store.redis_client:
                    cache_key = f"feature:{entity_id}:{feature_name}"
                    try:
                        serialized_value = pickle.dumps(feature_value).decode('latin1')
                        self.feature_store.redis_client.setex(
                            cache_key, self.cache_ttl, serialized_value
                        )
                    except Exception as e:
                        logger.warning(f"캐시 저장 실패 {cache_key}: {e}")
        
        return results
    
    async def get_features_async(self, entity_id: str, feature_names: List[str],
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """비동기 피처 조회"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.feature_store.executor,
            self.get_features,
            entity_id,
            feature_names,
            context
        )
    
    def batch_get_features(self, entity_ids: List[str], feature_names: List[str],
                          contexts: List[Dict[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
        """배치 피처 조회"""
        if contexts is None:
            contexts = [{}] * len(entity_ids)
        
        results = {}
        
        # 병렬 처리
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_entity = {
                executor.submit(self.get_features, entity_id, feature_names, context): entity_id
                for entity_id, context in zip(entity_ids, contexts)
            }
            
            for future in as_completed(future_to_entity):
                entity_id = future_to_entity[future]
                try:
                    entity_features = future.result()
                    results[entity_id] = entity_features
                except Exception as e:
                    logger.error(f"배치 피처 조회 실패 {entity_id}: {e}")
                    results[entity_id] = {}
        
        return results

class FeatureValidator:
    """피처 검증기"""
    
    def __init__(self):
        self.validation_rules = {
            'range': self._validate_range,
            'type': self._validate_type,
            'not_null': self._validate_not_null,
            'enum': self._validate_enum,
            'regex': self._validate_regex,
            'custom': self._validate_custom
        }
    
    def validate_feature(self, feature_value: FeatureValue,
                        validation_rules: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """피처 값 검증"""
        errors = []
        
        for rule_type, rule_config in validation_rules.items():
            if rule_type not in self.validation_rules:
                continue
            
            validator = self.validation_rules[rule_type]
            is_valid, error_msg = validator(feature_value.value, rule_config)
            
            if not is_valid:
                errors.append(f"{feature_value.feature_name}: {error_msg}")
        
        return len(errors) == 0, errors
    
    def _validate_range(self, value, config) -> Tuple[bool, str]:
        """범위 검증"""
        if not isinstance(value, (int, float)):
            return False, f"숫자가 아닙니다: {value}"
        
        min_val = config.get('min')
        max_val = config.get('max')
        
        if min_val is not None and value < min_val:
            return False, f"최솟값 {min_val}보다 작습니다: {value}"
        
        if max_val is not None and value > max_val:
            return False, f"최댓값 {max_val}보다 큽니다: {value}"
        
        return True, ""
    
    def _validate_type(self, value, config) -> Tuple[bool, str]:
        """타입 검증"""
        expected_type = config.get('expected_type')
        
        if expected_type == 'string' and not isinstance(value, str):
            return False, f"문자열이 아닙니다: {type(value)}"
        elif expected_type == 'number' and not isinstance(value, (int, float)):
            return False, f"숫자가 아닙니다: {type(value)}"
        elif expected_type == 'list' and not isinstance(value, list):
            return False, f"리스트가 아닙니다: {type(value)}"
        
        return True, ""
    
    def _validate_not_null(self, value, config) -> Tuple[bool, str]:
        """Not Null 검증"""
        if value is None or (isinstance(value, str) and len(value.strip()) == 0):
            return False, "값이 없습니다"
        return True, ""
    
    def _validate_enum(self, value, config) -> Tuple[bool, str]:
        """열거형 검증"""
        allowed_values = config.get('allowed_values', [])
        if value not in allowed_values:
            return False, f"허용되지 않는 값입니다. 허용값: {allowed_values}"
        return True, ""
    
    def _validate_regex(self, value, config) -> Tuple[bool, str]:
        """정규식 검증"""
        import re
        pattern = config.get('pattern')
        if pattern and not re.match(pattern, str(value)):
            return False, f"패턴과 일치하지 않습니다: {pattern}"
        return True, ""
    
    def _validate_custom(self, value, config) -> Tuple[bool, str]:
        """커스텀 검증"""
        # 커스텀 검증 로직 실행
        validation_function = config.get('function')
        if validation_function and callable(validation_function):
            try:
                is_valid = validation_function(value)
                if not is_valid:
                    return False, "커스텀 검증 실패"
            except Exception as e:
                return False, f"커스텀 검증 오류: {e}"
        
        return True, ""

class FeatureMonitor:
    """피처 모니터링"""
    
    def __init__(self, feature_store: FeatureStore):
        self.feature_store = feature_store
        self.drift_thresholds = {
            'statistical': 0.05,  # p-value 임계값
            'distribution': 0.1,   # KL divergence 임계값
            'mean_shift': 0.2      # 평균 변화 임계값
        }
    
    def detect_feature_drift(self, feature_name: str, 
                           baseline_period_days: int = 30,
                           current_period_days: int = 7) -> Dict[str, Any]:
        """피처 드리프트 탐지"""
        # 실제 구현에서는 데이터베이스에서 히스토리컬 데이터를 조회
        # 여기서는 시뮬레이션 데이터 생성
        
        np.random.seed(42)
        
        # 베이스라인 데이터 (과거 30일)
        baseline_data = np.random.normal(0.5, 0.1, 1000)
        
        # 현재 데이터 (최근 7일) - 약간의 드리프트 포함
        current_data = np.random.normal(0.55, 0.12, 200)  # 평균이 증가
        
        # 통계적 검정
        from scipy import stats
        statistic, p_value = stats.ks_2samp(baseline_data, current_data)
        
        # 분포 변화 계산
        mean_baseline = np.mean(baseline_data)
        mean_current = np.mean(current_data)
        mean_shift = abs(mean_current - mean_baseline) / mean_baseline
        
        std_baseline = np.std(baseline_data)
        std_current = np.std(current_data)
        std_shift = abs(std_current - std_baseline) / std_baseline
        
        # 드리프트 판정
        drift_detected = (
            p_value < self.drift_thresholds['statistical'] or
            mean_shift > self.drift_thresholds['mean_shift']
        )
        
        return {
            'feature_name': feature_name,
            'drift_detected': drift_detected,
            'statistical_test': {
                'ks_statistic': statistic,
                'p_value': p_value,
                'significant': p_value < self.drift_thresholds['statistical']
            },
            'distribution_changes': {
                'mean_baseline': mean_baseline,
                'mean_current': mean_current,
                'mean_shift_ratio': mean_shift,
                'std_baseline': std_baseline,
                'std_current': std_current,
                'std_shift_ratio': std_shift
            },
            'drift_severity': self._calculate_drift_severity(mean_shift, std_shift, p_value),
            'recommendations': self._generate_drift_recommendations(drift_detected, mean_shift, p_value)
        }
    
    def _calculate_drift_severity(self, mean_shift: float, std_shift: float, p_value: float) -> str:
        """드리프트 심각도 계산"""
        if mean_shift > 0.5 or std_shift > 0.5 or p_value < 0.001:
            return 'high'
        elif mean_shift > 0.2 or std_shift > 0.2 or p_value < 0.01:
            return 'medium'
        elif mean_shift > 0.1 or std_shift > 0.1 or p_value < 0.05:
            return 'low'
        else:
            return 'none'
    
    def _generate_drift_recommendations(self, drift_detected: bool, 
                                      mean_shift: float, p_value: float) -> List[str]:
        """드리프트 대응 추천사항"""
        recommendations = []
        
        if not drift_detected:
            recommendations.append("현재 피처는 안정적입니다.")
        else:
            recommendations.append("피처 드리프트가 감지되었습니다.")
            
            if mean_shift > 0.3:
                recommendations.append("피처 재계산 로직을 검토하세요.")
                recommendations.append("데이터 소스에 변화가 있는지 확인하세요.")
            
            if p_value < 0.001:
                recommendations.append("모델 재학습을 고려하세요.")
                recommendations.append("피처 엔지니어링을 재검토하세요.")
            
            recommendations.append("알림 설정을 통해 지속적인 모니터링을 수행하세요.")
        
        return recommendations
    
    def monitor_feature_freshness(self) -> Dict[str, Any]:
        """피처 신선도 모니터링"""
        freshness_report = {}
        
        for feature_name, feature_def in self.feature_store.feature_definitions.items():
            expected_update_freq = feature_def.update_frequency
            
            # 마지막 업데이트 시간 시뮬레이션
            np.random.seed(hash(feature_name) % 2**32)
            hours_since_update = np.random.randint(0, 48)
            last_update = datetime.now() - timedelta(hours=hours_since_update)
            
            # 신선도 판정
            freshness_status = self._evaluate_freshness(expected_update_freq, hours_since_update)
            
            freshness_report[feature_name] = {
                'last_update': last_update.isoformat(),
                'hours_since_update': hours_since_update,
                'expected_frequency': expected_update_freq,
                'freshness_status': freshness_status,
                'is_stale': freshness_status in ['stale', 'very_stale']
            }
        
        return freshness_report
    
    def _evaluate_freshness(self, expected_freq: str, hours_since_update: int) -> str:
        """신선도 평가"""
        thresholds = {
            'real_time': {'fresh': 1, 'stale': 6, 'very_stale': 24},
            'hourly': {'fresh': 2, 'stale': 12, 'very_stale': 48},
            'daily': {'fresh': 25, 'stale': 72, 'very_stale': 168},
            'weekly': {'fresh': 168, 'stale': 336, 'very_stale': 672}
        }
        
        threshold = thresholds.get(expected_freq, thresholds['daily'])
        
        if hours_since_update <= threshold['fresh']:
            return 'fresh'
        elif hours_since_update <= threshold['stale']:
            return 'stale'
        else:
            return 'very_stale'

# 사용 예시 및 통합 시스템
def setup_ad_feature_store():
    """광고 피처 스토어 설정"""
    print("=== 광고 피처 스토어 설정 ===")
    
    # 피처 스토어 초기화
    feature_store = FeatureStore()
    
    # 광고 관련 피처 정의들
    ad_features = [
        FeatureDefinition(
            name="user_ctr",
            description="사용자 클릭률",
            feature_type="numerical",
            data_source="ad_interactions",
            computation_logic="clicks / impressions for user",
            update_frequency="hourly",
            version="1.0",
            tags=["user", "performance", "ctr"],
            validation_rules={
                "range": {"min": 0, "max": 1},
                "type": {"expected_type": "number"}
            }
        ),
        FeatureDefinition(
            name="user_cvr",
            description="사용자 전환율",
            feature_type="numerical",
            data_source="ad_interactions",
            computation_logic="conversions / clicks for user",
            update_frequency="hourly",
            version="1.0",
            tags=["user", "performance", "conversion"],
            validation_rules={
                "range": {"min": 0, "max": 1},
                "type": {"expected_type": "number"}
            }
        ),
        FeatureDefinition(
            name="user_ltv",
            description="사용자 생애가치",
            feature_type="numerical",
            data_source="transactions",
            computation_logic="sum of user transactions with time decay",
            update_frequency="daily",
            version="1.0",
            tags=["user", "value", "ltv"],
            dependencies=["user_engagement_score"],
            validation_rules={
                "range": {"min": 0, "max": 50000},
                "type": {"expected_type": "number"}
            }
        ),
        FeatureDefinition(
            name="user_engagement_score",
            description="사용자 참여도 점수",
            feature_type="numerical",
            data_source="user_activities",
            computation_logic="weighted combination of user activities",
            update_frequency="hourly",
            version="1.0",
            tags=["user", "engagement", "behavior"],
            validation_rules={
                "range": {"min": 0, "max": 1},
                "type": {"expected_type": "number"}
            }
        ),
        FeatureDefinition(
            name="seasonal_factor",
            description="계절성 요인",
            feature_type="numerical",
            data_source="calendar",
            computation_logic="seasonal adjustment based on month/week",
            update_frequency="daily",
            version="1.0",
            tags=["temporal", "seasonal", "external"],
            validation_rules={
                "range": {"min": 0.1, "max": 2.0},
                "type": {"expected_type": "number"}
            }
        )
    ]
    
    # 피처 등록
    for feature_def in ad_features:
        success = feature_store.register_feature(feature_def)
        if success:
            print(f"✅ 피처 등록 성공: {feature_def.name}")
        else:
            print(f"❌ 피처 등록 실패: {feature_def.name}")
    
    return feature_store

def example_feature_store_system():
    """피처 스토어 시스템 예시"""
    print("=== 광고 피처 스토어 시스템 ===")
    
    # 1. 피처 스토어 설정
    feature_store = setup_ad_feature_store()
    
    # 2. 피처 계산기 초기화
    feature_computer = AdFeatureComputer(feature_store)
    
    # 3. 실시간 피처 서버 초기화
    feature_server = RealTimeFeatureServer(feature_store, feature_computer)
    
    # 4. 피처 검증기 및 모니터링
    validator = FeatureValidator()
    monitor = FeatureMonitor(feature_store)
    
    # 5. 샘플 사용자에 대한 피처 계산
    print("\n=== 피처 계산 테스트 ===")
    sample_user_id = "user_12345"
    feature_names = ["user_ctr", "user_cvr", "user_ltv", "user_engagement_score", "seasonal_factor"]
    
    context = {
        'device_type': 'mobile',
        'time_of_day': 20,
        'income_level': 'high',
        'user_interests': ['technology', 'gaming'],
        'keywords': ['smartphone', 'gaming'],
        'category': 'electronics'
    }
    
    # 피처 조회
    features = feature_server.get_features(sample_user_id, feature_names, context)
    
    print(f"사용자 {sample_user_id}의 피처:")
    for feature_name, feature_value in features.items():
        print(f"  {feature_name}: {feature_value.value}")
    
    # 6. 배치 피처 조회 테스트
    print("\n=== 배치 피처 조회 테스트 ===")
    user_ids = [f"user_{i:05d}" for i in range(10)]
    contexts = [context] * len(user_ids)
    
    batch_features = feature_server.batch_get_features(user_ids, ["user_ctr", "user_cvr"], contexts)
    print(f"배치 조회 완료: {len(batch_features)}명의 사용자")
    
    # 7. 피처 검증 테스트
    print("\n=== 피처 검증 테스트 ===")
    if features:
        sample_feature = list(features.values())[0]
        feature_def = feature_store.get_feature_definition(sample_feature.feature_name)
        
        is_valid, errors = validator.validate_feature(sample_feature, feature_def.validation_rules)
        print(f"피처 검증 결과: {'✅ 통과' if is_valid else '❌ 실패'}")
        if errors:
            for error in errors:
                print(f"  오류: {error}")
    
    # 8. 드리프트 모니터링 테스트
    print("\n=== 드리프트 모니터링 테스트 ===")
    drift_report = monitor.detect_feature_drift("user_ctr")
    print(f"드리프트 감지: {'🚨 있음' if drift_report['drift_detected'] else '✅ 없음'}")
    print(f"심각도: {drift_report['drift_severity']}")
    
    # 9. 신선도 모니터링 테스트
    print("\n=== 신선도 모니터링 테스트 ===")
    freshness_report = monitor.monitor_feature_freshness()
    stale_features = [name for name, info in freshness_report.items() if info['is_stale']]
    print(f"신선하지 않은 피처: {len(stale_features)}개")
    
    # 10. 피처 목록 조회
    print("\n=== 등록된 피처 목록 ===")
    all_features = feature_store.list_features()
    print(f"총 {len(all_features)}개 피처 등록됨:")
    for feature_def in all_features:
        print(f"  - {feature_def.name} ({feature_def.feature_type}, {feature_def.update_frequency})")
    
    # 성능 통계
    performance_stats = {
        'total_features': len(all_features),
        'users_processed': len(batch_features),
        'features_computed': len(features),
        'drift_detected_features': sum(1 for report in [drift_report] if report['drift_detected']),
        'stale_features': len(stale_features)
    }
    
    return performance_stats

if __name__ == "__main__":
    results = example_feature_store_system()
    print(f"\n=== 피처 스토어 시스템 완료 ===")
    print(f"총 피처 수: {results['total_features']}")
    print(f"처리된 사용자: {results['users_processed']}명")
    print(f"계산된 피처: {results['features_computed']}개")
    print(f"드리프트 감지 피처: {results['drift_detected_features']}개")
    print(f"신선하지 않은 피처: {results['stale_features']}개")
```

## 🚀 프로젝트
1. **실시간 피처 서빙 플랫폼**
2. **피처 드리프트 모니터링 시스템**
3. **MLOps 피처 파이프라인**
4. **A/B 테스트 피처 관리 도구**