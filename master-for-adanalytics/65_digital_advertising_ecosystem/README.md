# 65. Digital Advertising Ecosystem - 디지털 광고 생태계

## 📚 과정 소개
디지털 광고 생태계의 모든 구성 요소를 마스터합니다. 프로그래매틱 거래부터 브랜드 세이프티까지 현대 디지털 광고의 핵심 메커니즘을 학습합니다.

## 🎯 학습 목표
- 프로그래매틱 광고 생태계와 RTB 메커니즘 이해
- DSP/SSP/DMP/CDP 플랫폼 운영 전략
- 쿠키리스 환경 대응과 프라이버시 보호 광고
- 브랜드 세이프티와 광고 사기 탐지 시스템

## 📖 주요 내용

### 디지털 광고 생태계 분석 시스템
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import requests
import hashlib
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DigitalAdvertisingEcosystem:
    """디지털 광고 생태계 분석을 위한 종합 클래스"""
    
    def __init__(self):
        self.rtb_simulator = RTBSimulator()
        self.fraud_detector = AdFraudDetector()
        self.brand_safety = BrandSafetyMonitor()
        self.privacy_manager = PrivacyComplianceManager()
        
    def programmatic_ecosystem_analysis(self, bid_data, inventory_data):
        """프로그래매틱 생태계 분석"""
        
        # 공급 경로 최적화 (Supply Path Optimization)
        def analyze_supply_path(bid_requests):
            """공급 경로 효율성 분석"""
            supply_chains = {}
            
            for _, bid in bid_requests.iterrows():
                # 공급 체인 추적 (Publisher -> SSP -> Exchange -> DSP)
                chain_key = f"{bid['publisher_id']}->{bid['ssp_id']}->{bid['exchange_id']}"
                
                if chain_key not in supply_chains:
                    supply_chains[chain_key] = {
                        'bid_requests': 0,
                        'win_rate': 0,
                        'avg_cpm': 0,
                        'total_wins': 0,
                        'total_spend': 0
                    }
                
                supply_chains[chain_key]['bid_requests'] += 1
                if bid['won'] == 1:
                    supply_chains[chain_key]['total_wins'] += 1
                    supply_chains[chain_key]['total_spend'] += bid['winning_price']
            
            # 효율성 메트릭 계산
            for chain in supply_chains.values():
                if chain['bid_requests'] > 0:
                    chain['win_rate'] = chain['total_wins'] / chain['bid_requests']
                if chain['total_wins'] > 0:
                    chain['avg_cpm'] = chain['total_spend'] / chain['total_wins']
            
            return supply_chains
        
        # 인벤토리 품질 분석
        def analyze_inventory_quality(inventory):
            """인벤토리 품질 점수 계산"""
            quality_scores = {}
            
            for _, inv in inventory.iterrows():
                domain_score = self._calculate_domain_authority(inv['domain'])
                viewability_score = inv['viewability_rate']
                brand_safety_score = inv['brand_safety_score']
                fraud_score = 1 - inv['fraud_probability']  # 사기 확률이 낮을수록 좋음
                
                # 가중 평균으로 종합 품질 점수 계산
                quality_score = (
                    domain_score * 0.3 +
                    viewability_score * 0.3 +
                    brand_safety_score * 0.2 +
                    fraud_score * 0.2
                )
                
                quality_scores[inv['inventory_id']] = {
                    'domain_authority': domain_score,
                    'viewability': viewability_score,
                    'brand_safety': brand_safety_score,
                    'fraud_risk': 1 - fraud_score,
                    'overall_quality': quality_score
                }
            
            return quality_scores
        
        # 공급 체인 분석
        supply_path_analysis = analyze_supply_path(bid_data)
        
        # 인벤토리 품질 분석
        inventory_quality = analyze_inventory_quality(inventory_data)
        
        # 비딩 효율성 분석
        bidding_efficiency = self._analyze_bidding_efficiency(bid_data)
        
        # 생태계 맵 생성
        ecosystem_map = self._create_ecosystem_network(bid_data, inventory_data)
        
        return {
            'supply_path_analysis': supply_path_analysis,
            'inventory_quality': inventory_quality,
            'bidding_efficiency': bidding_efficiency,
            'ecosystem_network': ecosystem_map
        }
    
    def rtb_auction_simulation(self, bid_requests, advertiser_profiles):
        """RTB 경매 시뮬레이션"""
        
        auction_results = []
        
        for _, bid_request in bid_requests.iterrows():
            # 각 광고주의 입찰 결정
            bids = []
            
            for advertiser_id, profile in advertiser_profiles.items():
                # 타겟팅 매칭 점수 계산
                targeting_score = self._calculate_targeting_match(
                    bid_request, profile['targeting_criteria']
                )
                
                if targeting_score > profile['min_targeting_threshold']:
                    # 입찰가 계산 (가치 기반)
                    base_bid = profile['base_cpm']
                    bid_modifier = targeting_score * profile['targeting_multiplier']
                    
                    # 예산 제약 확인
                    if profile['remaining_budget'] > base_bid * bid_modifier:
                        final_bid = base_bid * bid_modifier
                        
                        bids.append({
                            'advertiser_id': advertiser_id,
                            'bid_amount': final_bid,
                            'targeting_score': targeting_score,
                            'creative_id': profile['creative_id']
                        })
            
            # 경매 실행 (2차 가격 경매)
            if len(bids) > 0:
                # 입찰가 순으로 정렬
                bids_sorted = sorted(bids, key=lambda x: x['bid_amount'], reverse=True)
                
                winner = bids_sorted[0]
                
                # 2차 가격 (두 번째로 높은 입찰가 + 0.01)
                if len(bids_sorted) > 1:
                    clearing_price = bids_sorted[1]['bid_amount'] + 0.01
                else:
                    clearing_price = winner['bid_amount']  # 단일 입찰자
                
                # 광고주 예산 차감
                advertiser_profiles[winner['advertiser_id']]['remaining_budget'] -= clearing_price
                
                auction_result = {
                    'bid_request_id': bid_request['bid_request_id'],
                    'winner_id': winner['advertiser_id'],
                    'winning_bid': winner['bid_amount'],
                    'clearing_price': clearing_price,
                    'targeting_score': winner['targeting_score'],
                    'total_bidders': len(bids),
                    'auction_time': bid_request['timestamp']
                }
            else:
                # 입찰자 없음
                auction_result = {
                    'bid_request_id': bid_request['bid_request_id'],
                    'winner_id': None,
                    'winning_bid': 0,
                    'clearing_price': 0,
                    'targeting_score': 0,
                    'total_bidders': 0,
                    'auction_time': bid_request['timestamp']
                }
            
            auction_results.append(auction_result)
        
        # 경매 성과 분석
        auction_analytics = self._analyze_auction_performance(auction_results, advertiser_profiles)
        
        return {
            'auction_results': pd.DataFrame(auction_results),
            'final_advertiser_budgets': advertiser_profiles,
            'auction_analytics': auction_analytics
        }
    
    def cookieless_advertising_strategy(self, user_data, contextual_data, first_party_data):
        """쿠키리스 광고 전략"""
        
        # 1. 컨텍스추얼 타겟팅
        contextual_targeting = self._build_contextual_targeting_model(contextual_data)
        
        # 2. 코호트 기반 타겟팅 (Topics API 시뮬레이션)
        cohort_targeting = self._create_privacy_preserving_cohorts(user_data)
        
        # 3. 퍼스트파티 데이터 활용
        first_party_insights = self._analyze_first_party_data(first_party_data)
        
        # 4. 확률적 매칭 (probabilistic matching)
        identity_resolution = self._probabilistic_identity_matching(user_data, first_party_data)
        
        # 5. 연합 학습 시뮬레이션
        federated_model = self._simulate_federated_learning(user_data)
        
        # 성과 예측 모델
        cookieless_performance = self._predict_cookieless_performance(
            contextual_targeting, cohort_targeting, first_party_insights
        )
        
        return {
            'contextual_targeting': contextual_targeting,
            'cohort_targeting': cohort_targeting,
            'first_party_insights': first_party_insights,
            'identity_resolution': identity_resolution,
            'federated_learning': federated_model,
            'performance_prediction': cookieless_performance
        }
    
    def brand_safety_monitoring(self, content_data, ad_placements):
        """브랜드 세이프티 모니터링"""
        
        # 컨텐츠 안전성 분석
        content_safety_scores = {}
        
        for _, content in content_data.iterrows():
            # 키워드 기반 위험도 분석
            risk_keywords = self._detect_risk_keywords(content['content_text'])
            
            # 감정 분석
            sentiment_score = self._analyze_content_sentiment(content['content_text'])
            
            # 카테고리 분류
            content_category = self._classify_content_category(content['content_text'])
            
            # 종합 안전성 점수
            safety_score = self._calculate_brand_safety_score(
                risk_keywords, sentiment_score, content_category
            )
            
            content_safety_scores[content['content_id']] = {
                'risk_keywords': risk_keywords,
                'sentiment_score': sentiment_score,
                'content_category': content_category,
                'safety_score': safety_score,
                'safe_for_advertising': safety_score > 0.7
            }
        
        # 광고 배치 위험도 분석
        placement_risks = self._analyze_placement_risks(ad_placements, content_safety_scores)
        
        # 브랜드별 맞춤 안전성 기준
        brand_specific_safety = self._create_brand_safety_profiles(ad_placements)
        
        # 실시간 모니터링 알럿
        safety_alerts = self._generate_safety_alerts(placement_risks, brand_specific_safety)
        
        return {
            'content_safety_scores': content_safety_scores,
            'placement_risks': placement_risks,
            'brand_safety_profiles': brand_specific_safety,
            'safety_alerts': safety_alerts,
            'safety_dashboard_data': self._prepare_safety_dashboard(content_safety_scores, placement_risks)
        }
    
    def ad_fraud_detection(self, traffic_data, click_data, conversion_data):
        """광고 사기 탐지"""
        
        # 다양한 사기 패턴 탐지
        fraud_indicators = {
            'click_fraud': self._detect_click_fraud(click_data),
            'impression_fraud': self._detect_impression_fraud(traffic_data),
            'conversion_fraud': self._detect_conversion_fraud(conversion_data),
            'bot_traffic': self._detect_bot_traffic(traffic_data),
            'domain_spoofing': self._detect_domain_spoofing(traffic_data)
        }
        
        # 머신러닝 기반 이상 탐지
        ml_fraud_detection = self._ml_fraud_detection(traffic_data, click_data)
        
        # 사기 위험도 점수 계산
        fraud_risk_scores = self._calculate_fraud_risk_scores(fraud_indicators, ml_fraud_detection)
        
        # 사기 방지 권고사항
        fraud_prevention_recommendations = self._generate_fraud_prevention_recommendations(
            fraud_risk_scores, fraud_indicators
        )
        
        return {
            'fraud_indicators': fraud_indicators,
            'ml_detection_results': ml_fraud_detection,
            'fraud_risk_scores': fraud_risk_scores,
            'prevention_recommendations': fraud_prevention_recommendations,
            'fraud_monitoring_dashboard': self._create_fraud_dashboard(fraud_indicators, fraud_risk_scores)
        }
    
    def data_clean_room_simulation(self, advertiser_data, publisher_data, privacy_budget=1.0):
        """데이터 클린룸 시뮬레이션"""
        
        # 차등 프라이버시 적용
        def add_differential_privacy_noise(data, epsilon=1.0):
            """차등 프라이버시 노이즈 추가"""
            sensitivity = 1.0  # 데이터 민감도
            noise_scale = sensitivity / epsilon
            
            noise = np.random.laplace(0, noise_scale, data.shape)
            return data + noise
        
        # 안전한 집계 쿼리 시뮬레이션
        clean_room_queries = {
            'audience_overlap': self._calculate_safe_audience_overlap(
                advertiser_data, publisher_data, privacy_budget * 0.3
            ),
            'conversion_attribution': self._safe_attribution_analysis(
                advertiser_data, publisher_data, privacy_budget * 0.3
            ),
            'lookalike_modeling': self._privacy_preserving_lookalike(
                advertiser_data, publisher_data, privacy_budget * 0.4
            )
        }
        
        # 프라이버시 예산 추적
        remaining_budget = privacy_budget - sum([0.3, 0.3, 0.4])
        
        # 쿼리 결과 검증
        query_validation = self._validate_clean_room_queries(clean_room_queries)
        
        return {
            'clean_room_queries': clean_room_queries,
            'remaining_privacy_budget': remaining_budget,
            'query_validation': query_validation,
            'privacy_audit_log': self._create_privacy_audit_log(clean_room_queries)
        }

class RTBSimulator:
    """RTB 시뮬레이션 클래스"""
    
    def __init__(self):
        self.auction_history = []
    
    def simulate_bid_request(self, user_profile, inventory_info):
        """입찰 요청 시뮬레이션"""
        bid_request = {
            'id': self._generate_request_id(),
            'timestamp': datetime.now(),
            'user_profile': user_profile,
            'inventory': inventory_info,
            'floor_price': inventory_info.get('floor_price', 0.5),
            'auction_type': 2  # 2차 가격 경매
        }
        
        return bid_request
    
    def _generate_request_id(self):
        """고유 요청 ID 생성"""
        return hashlib.md5(str(datetime.now()).encode()).hexdigest()[:16]

class AdFraudDetector:
    """광고 사기 탐지 클래스"""
    
    def __init__(self):
        self.fraud_patterns = {
            'click_fraud_threshold': 0.1,  # 10% 이상 클릭율은 의심
            'bot_traffic_indicators': ['unusual_user_agent', 'datacenter_ip', 'high_frequency_clicks'],
            'domain_spoofing_patterns': ['similar_domains', 'typosquatting']
        }
    
    def detect_anomalies(self, traffic_data):
        """이상 패턴 탐지"""
        anomalies = []
        
        # 클릭 패턴 분석
        click_rates = traffic_data.groupby('source_id')['clicks'].sum() / traffic_data.groupby('source_id')['impressions'].sum()
        suspicious_sources = click_rates[click_rates > self.fraud_patterns['click_fraud_threshold']].index
        
        for source in suspicious_sources:
            anomalies.append({
                'type': 'suspicious_click_rate',
                'source_id': source,
                'click_rate': click_rates[source],
                'risk_level': 'high' if click_rates[source] > 0.2 else 'medium'
            })
        
        return anomalies

class BrandSafetyMonitor:
    """브랜드 세이프티 모니터링 클래스"""
    
    def __init__(self):
        self.risk_categories = {
            'adult_content': ['adult', 'explicit', 'mature'],
            'violence': ['violence', 'weapon', 'crime'],
            'hate_speech': ['hate', 'discrimination', 'offensive'],
            'fake_news': ['misinformation', 'conspiracy', 'fake']
        }
    
    def assess_content_safety(self, content_text):
        """컨텐츠 안전성 평가"""
        risk_score = 0
        detected_risks = []
        
        content_lower = content_text.lower()
        
        for category, keywords in self.risk_categories.items():
            for keyword in keywords:
                if keyword in content_lower:
                    risk_score += 0.2
                    detected_risks.append(category)
        
        safety_score = max(0, 1 - risk_score)
        
        return {
            'safety_score': safety_score,
            'detected_risks': list(set(detected_risks)),
            'safe_for_advertising': safety_score > 0.7
        }

class PrivacyComplianceManager:
    """프라이버시 컴플라이언스 관리 클래스"""
    
    def __init__(self):
        self.compliance_frameworks = ['GDPR', 'CCPA', 'COPPA']
        self.consent_requirements = {
            'GDPR': ['explicit_consent', 'data_minimization', 'right_to_deletion'],
            'CCPA': ['opt_out_rights', 'data_disclosure', 'non_discrimination'],
            'COPPA': ['parental_consent', 'limited_data_collection', 'safe_harbor']
        }
    
    def check_compliance(self, data_processing_activity):
        """컴플라이언스 체크"""
        compliance_status = {}
        
        for framework in self.compliance_frameworks:
            requirements = self.consent_requirements[framework]
            met_requirements = []
            
            for requirement in requirements:
                if self._check_requirement(data_processing_activity, requirement):
                    met_requirements.append(requirement)
            
            compliance_status[framework] = {
                'compliant': len(met_requirements) == len(requirements),
                'met_requirements': met_requirements,
                'missing_requirements': list(set(requirements) - set(met_requirements))
            }
        
        return compliance_status
    
    def _check_requirement(self, activity, requirement):
        """개별 요구사항 체크"""
        # 실제 구현에서는 더 정교한 로직 필요
        return requirement in activity.get('compliance_measures', [])

# 보조 메서드들
def _calculate_domain_authority(domain):
    """도메인 권위도 계산 (시뮬레이션)"""
    # 실제로는 외부 API 또는 데이터베이스 조회
    domain_scores = {
        'google.com': 0.95,
        'facebook.com': 0.90,
        'nytimes.com': 0.85,
        'unknown.com': 0.3
    }
    return domain_scores.get(domain, np.random.uniform(0.2, 0.8))

def _analyze_bidding_efficiency(bid_data):
    """비딩 효율성 분석"""
    efficiency_metrics = {
        'win_rate': (bid_data['won'] == 1).mean(),
        'avg_winning_price': bid_data[bid_data['won'] == 1]['winning_price'].mean(),
        'bid_to_win_ratio': bid_data['bid_amount'].mean() / bid_data[bid_data['won'] == 1]['winning_price'].mean(),
        'budget_utilization': bid_data[bid_data['won'] == 1]['winning_price'].sum() / bid_data['budget_allocated'].sum()
    }
    
    return efficiency_metrics

# 실습 예제: 종합 디지털 광고 생태계 분석
def comprehensive_digital_ecosystem_analysis():
    """종합적인 디지털 광고 생태계 분석"""
    
    # 샘플 데이터 생성
    np.random.seed(42)
    
    # RTB 입찰 데이터
    bid_data = pd.DataFrame({
        'bid_request_id': [f'br_{i}' for i in range(10000)],
        'publisher_id': np.random.choice(['pub_1', 'pub_2', 'pub_3', 'pub_4'], 10000),
        'ssp_id': np.random.choice(['ssp_1', 'ssp_2', 'ssp_3'], 10000),
        'exchange_id': np.random.choice(['ex_1', 'ex_2'], 10000),
        'bid_amount': np.random.uniform(0.5, 10.0, 10000),
        'winning_price': np.random.uniform(0.1, 8.0, 10000),
        'won': np.random.choice([0, 1], 10000, p=[0.8, 0.2]),
        'budget_allocated': np.random.uniform(1000, 50000, 10000),
        'timestamp': pd.date_range('2024-01-01', periods=10000, freq='1min')
    })
    
    # 인벤토리 데이터
    inventory_data = pd.DataFrame({
        'inventory_id': [f'inv_{i}' for i in range(1000)],
        'domain': np.random.choice(['google.com', 'facebook.com', 'nytimes.com', 'unknown.com'], 1000),
        'viewability_rate': np.random.uniform(0.3, 0.95, 1000),
        'brand_safety_score': np.random.uniform(0.5, 1.0, 1000),
        'fraud_probability': np.random.uniform(0.0, 0.3, 1000)
    })
    
    # 트래픽 데이터 (사기 탐지용)
    traffic_data = pd.DataFrame({
        'source_id': [f'src_{i}' for i in range(500)],
        'impressions': np.random.poisson(1000, 500),
        'clicks': np.random.poisson(50, 500),
        'user_agent': np.random.choice(['normal', 'suspicious', 'bot'], 500, p=[0.8, 0.15, 0.05]),
        'ip_type': np.random.choice(['residential', 'datacenter', 'mobile'], 500, p=[0.7, 0.2, 0.1]),
        'click_pattern': np.random.choice(['normal', 'burst', 'regular'], 500, p=[0.7, 0.2, 0.1])
    })
    
    # 컨텐츠 데이터 (브랜드 세이프티용)
    content_samples = [
        "Breaking news about technology trends",
        "Sports match results and highlights", 
        "Cooking recipes and food reviews",
        "Adult content warning mature themes",
        "Violence in latest action movie",
        "Political debate and opinions"
    ]
    
    content_data = pd.DataFrame({
        'content_id': [f'content_{i}' for i in range(100)],
        'content_text': np.random.choice(content_samples, 100),
        'domain': np.random.choice(['news.com', 'sports.com', 'food.com', 'adult.com'], 100)
    })
    
    # 광고 배치 데이터
    ad_placements = pd.DataFrame({
        'placement_id': [f'pl_{i}' for i in range(200)],
        'content_id': [f'content_{i}' for i in np.random.randint(0, 100, 200)],
        'brand_id': np.random.choice(['brand_A', 'brand_B', 'brand_C'], 200),
        'campaign_type': np.random.choice(['awareness', 'conversion', 'retargeting'], 200)
    })
    
    # 생태계 분석 도구 초기화
    ecosystem = DigitalAdvertisingEcosystem()
    
    # 1. 프로그래매틱 생태계 분석
    programmatic_analysis = ecosystem.programmatic_ecosystem_analysis(bid_data, inventory_data)
    
    # 2. 브랜드 세이프티 분석
    brand_safety_results = ecosystem.brand_safety_monitoring(content_data, ad_placements)
    
    # 3. 광고 사기 탐지
    fraud_detection_results = ecosystem.ad_fraud_detection(traffic_data, traffic_data, traffic_data)
    
    # 결과 출력
    print("=== 디지털 광고 생태계 분석 결과 ===")
    
    print("\n프로그래매틱 분석:")
    print(f"- 공급 체인 수: {len(programmatic_analysis['supply_path_analysis'])}개")
    print(f"- 평균 인벤토리 품질: {np.mean([q['overall_quality'] for q in programmatic_analysis['inventory_quality'].values()]):.3f}")
    
    print("\n브랜드 세이프티:")
    safe_content = sum(1 for score in brand_safety_results['content_safety_scores'].values() if score['safe_for_advertising'])
    print(f"- 안전한 컨텐츠 비율: {safe_content/len(brand_safety_results['content_safety_scores'])*100:.1f}%")
    print(f"- 안전성 알럿 수: {len(brand_safety_results['safety_alerts'])}개")
    
    print("\n사기 탐지:")
    high_risk_sources = sum(1 for score in fraud_detection_results['fraud_risk_scores'].values() if score > 0.7)
    print(f"- 고위험 소스: {high_risk_sources}개")
    print(f"- 탐지된 사기 패턴: {len([p for patterns in fraud_detection_results['fraud_indicators'].values() for p in patterns])}개")
    
    # 시각화
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. 입찰 성과 분포
    axes[0, 0].hist(bid_data[bid_data['won'] == 1]['winning_price'], bins=30, alpha=0.7, label='Winning Prices')
    axes[0, 0].hist(bid_data['bid_amount'], bins=30, alpha=0.5, label='Bid Amounts')
    axes[0, 0].set_xlabel('Price (CPM)')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('Bid vs Winning Price Distribution')
    axes[0, 0].legend()
    
    # 2. 인벤토리 품질 분포
    quality_scores = [q['overall_quality'] for q in programmatic_analysis['inventory_quality'].values()]
    axes[0, 1].hist(quality_scores, bins=20, alpha=0.7, color='green')
    axes[0, 1].set_xlabel('Quality Score')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Inventory Quality Distribution')
    
    # 3. 브랜드 세이프티 점수
    safety_scores = [score['safety_score'] for score in brand_safety_results['content_safety_scores'].values()]
    axes[1, 0].hist(safety_scores, bins=20, alpha=0.7, color='orange')
    axes[1, 0].axvline(x=0.7, color='red', linestyle='--', label='Safety Threshold')
    axes[1, 0].set_xlabel('Safety Score')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('Brand Safety Score Distribution')
    axes[1, 0].legend()
    
    # 4. 사기 위험도 vs 클릭율
    click_rates = traffic_data['clicks'] / traffic_data['impressions']
    fraud_scores = np.random.uniform(0, 1, len(traffic_data))  # 시뮬레이션
    
    axes[1, 1].scatter(click_rates, fraud_scores, alpha=0.6)
    axes[1, 1].set_xlabel('Click Rate')
    axes[1, 1].set_ylabel('Fraud Risk Score')
    axes[1, 1].set_title('Click Rate vs Fraud Risk')
    
    plt.tight_layout()
    plt.show()
    
    return {
        'programmatic_analysis': programmatic_analysis,
        'brand_safety_results': brand_safety_results,
        'fraud_detection_results': fraud_detection_results,
        'ecosystem_health_score': np.mean([
            np.mean(quality_scores),
            np.mean(safety_scores),
            1 - np.mean(fraud_scores)  # 낮은 사기 위험이 좋음
        ])
    }

# 메인 실행
if __name__ == "__main__":
    print("=== 디지털 광고 생태계 실습 ===")
    print("프로그래매틱 광고와 브랜드 세이프티 분석")
    
    results = comprehensive_digital_ecosystem_analysis()
    
    print(f"\n생태계 분석 완료:")
    print(f"- 전체 생태계 건강도: {results['ecosystem_health_score']:.3f}")
    print(f"- 프로그래매틱 효율성: 분석 완료")
    print(f"- 브랜드 세이프티: 모니터링 활성화")
    print(f"- 사기 탐지: 시스템 가동 중")
```

## 🚀 프로젝트
1. **실시간 RTB 최적화 엔진** - 입찰 전략 자동 조정 시스템
2. **브랜드 세이프티 AI 모니터** - 컨텐츠 위험도 실시간 분석
3. **광고 사기 탐지 플랫폼** - ML 기반 이상 패턴 탐지
4. **프라이버시 컴플라이언스 도구** - 쿠키리스 환경 대응 시스템