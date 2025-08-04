# 61. Advertising Theory Fundamentals - 광고 이론 기초

## 📚 과정 소개
광고 효과를 극대화하기 위한 핵심 이론을 마스터합니다. 소비자 심리학, 설득 이론, 브랜드 포지셔닝 등 광고의 과학적 기반을 데이터와 함께 학습합니다.

## 🎯 학습 목표
- 광고 심리학과 소비자 행동 이론 이해
- 설득 이론과 인지 처리 모델 적용
- 브랜드 포지셔닝과 광고 효과성 측정
- 주의-기억 모델 기반 크리에이티브 최적화

## 📖 주요 내용

### 광고 심리학과 소비자 행동 이론
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

class ConsumerBehaviorAnalyzer:
    """소비자 행동 분석을 위한 클래스"""
    
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        
    def elaboration_likelihood_model(self, user_data, ad_data):
        """정교화 가능성 모델(ELM) 적용"""
        # 중앙 경로 vs 주변 경로 처리 예측
        
        # 사용자 관여도 계산
        involvement_score = (
            user_data['product_knowledge'] * 0.3 +
            user_data['purchase_importance'] * 0.4 +
            user_data['time_available'] * 0.3
        )
        
        # 광고 메시지 강도 계산
        message_strength = (
            ad_data['argument_quality'] * 0.5 +
            ad_data['evidence_strength'] * 0.3 +
            ad_data['source_credibility'] * 0.2
        )
        
        # 처리 경로 결정
        processing_route = np.where(
            involvement_score > 0.6,
            'central',  # 중앙 경로 (논리적 처리)
            'peripheral'  # 주변 경로 (휴리스틱 처리)
        )
        
        # 태도 변화 예측
        attitude_change = np.where(
            processing_route == 'central',
            message_strength * involvement_score * 0.8,
            ad_data['peripheral_cues'] * (1 - involvement_score) * 0.6
        )
        
        return {
            'processing_route': processing_route,
            'attitude_change': attitude_change,
            'involvement_score': involvement_score
        }
    
    def hierarchy_of_effects_model(self, campaign_data):
        """효과 계층 모델 적용"""
        stages = ['awareness', 'knowledge', 'liking', 'preference', 'conviction', 'purchase']
        
        # 각 단계별 전환율 계산
        conversion_rates = {}
        funnel_data = pd.DataFrame()
        
        for i, stage in enumerate(stages):
            if i == 0:
                conversion_rates[stage] = 1.0
                funnel_data[stage] = campaign_data['impressions']
            else:
                prev_stage = stages[i-1]
                # 단계별 전환율 모델링
                base_rate = 0.8 - (i * 0.1)  # 기본 전환율
                
                # 캠페인 품질 요소 적용
                quality_factor = (
                    campaign_data['creative_quality'] * 0.3 +
                    campaign_data['targeting_accuracy'] * 0.3 +
                    campaign_data['message_relevance'] * 0.4
                )
                
                conversion_rates[stage] = base_rate * quality_factor
                funnel_data[stage] = funnel_data[prev_stage] * conversion_rates[stage]
        
        return {
            'conversion_rates': conversion_rates,
            'funnel_data': funnel_data,
            'total_conversion': funnel_data['purchase'] / funnel_data['awareness']
        }
    
    def cognitive_response_model(self, ad_exposure_data):
        """인지적 반응 모델"""
        # 광고에 대한 인지적 반응 분석
        
        # 반응 유형별 가중치
        response_weights = {
            'support_arguments': 0.4,  # 지지 논증
            'counter_arguments': -0.3,  # 반박 논증
            'source_derogations': -0.2,  # 출처 비하
            'execution_thoughts': 0.1   # 실행 관련 생각
        }
        
        # 각 반응 유형의 강도 계산
        cognitive_responses = {}
        for response_type, weight in response_weights.items():
            cognitive_responses[response_type] = (
                ad_exposure_data[f'{response_type}_count'] * 
                ad_exposure_data[f'{response_type}_intensity'] *
                weight
            )
        
        # 총 인지적 반응 점수
        total_cognitive_response = sum(cognitive_responses.values())
        
        # 태도 형성 예측
        attitude_formation = np.tanh(total_cognitive_response)  # -1 to 1 범위로 정규화
        
        return {
            'cognitive_responses': cognitive_responses,
            'total_response': total_cognitive_response,
            'predicted_attitude': attitude_formation
        }
    
    def means_end_chain_analysis(self, product_attributes, consumer_values):
        """수단-목적 사슬 분석"""
        # 제품 속성 -> 기능적 혜택 -> 심리적 혜택 -> 개인 가치
        
        # 속성-혜택 연결 매트릭스
        attribute_benefit_matrix = np.array([
            [0.8, 0.2, 0.1, 0.3],  # 품질 -> 성능, 신뢰성, 편의성, 사회적 인정
            [0.3, 0.1, 0.9, 0.2],  # 편의성 -> 성능, 신뢰성, 편의성, 사회적 인정
            [0.2, 0.3, 0.2, 0.8],  # 브랜드 -> 성능, 신뢰성, 편의성, 사회적 인정
            [0.6, 0.4, 0.3, 0.1]   # 가격 -> 성능, 신뢰성, 편의성, 사회적 인정
        ])
        
        # 혜택-가치 연결 매트릭스  
        benefit_value_matrix = np.array([
            [0.7, 0.2, 0.3, 0.1, 0.2],  # 성능 -> 성취, 안전, 즐거움, 사회적 소속, 자아실현
            [0.2, 0.8, 0.1, 0.3, 0.1],  # 신뢰성 -> 성취, 안전, 즐거움, 사회적 소속, 자아실현
            [0.1, 0.3, 0.8, 0.2, 0.4],  # 편의성 -> 성취, 안전, 즐거움, 사회적 소속, 자아실현
            [0.3, 0.1, 0.2, 0.9, 0.3]   # 사회적 인정 -> 성취, 안전, 즐거움, 사회적 소속, 자아실현
        ])
        
        # 제품 속성에서 개인 가치까지의 연결 강도 계산
        functional_benefits = np.dot(product_attributes, attribute_benefit_matrix)
        personal_values = np.dot(functional_benefits, benefit_value_matrix)
        
        # 가치 일치도 계산
        value_congruence = np.corrcoef(personal_values, consumer_values)[0, 1]
        
        return {
            'functional_benefits': functional_benefits,
            'personal_values': personal_values,
            'value_congruence': value_congruence,
            'chain_strength': np.sum(personal_values * consumer_values)
        }
    
    def dual_process_theory_model(self, ad_data, user_state):
        """이중 처리 이론 모델"""
        # System 1 (자동적, 직관적) vs System 2 (통제적, 분석적) 처리
        
        # 처리 시스템 결정 요인
        system1_triggers = (
            user_state['cognitive_load'] * 0.4 +
            user_state['time_pressure'] * 0.3 +
            ad_data['emotional_appeal'] * 0.3
        )
        
        system2_triggers = (
            user_state['motivation'] * 0.4 +
            ad_data['information_complexity'] * 0.3 +
            user_state['analytical_thinking'] * 0.3
        )
        
        # 처리 시스템 선택 (0: System 1, 1: System 2)
        processing_system = np.where(system2_triggers > system1_triggers, 1, 0)
        
        # 시스템별 광고 효과 예측
        system1_effect = (
            ad_data['visual_appeal'] * 0.4 +
            ad_data['emotional_intensity'] * 0.4 +
            ad_data['familiarity'] * 0.2
        )
        
        system2_effect = (
            ad_data['argument_strength'] * 0.5 +
            ad_data['evidence_quality'] * 0.3 +
            ad_data['logical_structure'] * 0.2
        )
        
        # 최종 광고 효과
        ad_effectiveness = np.where(
            processing_system == 0,
            system1_effect,
            system2_effect
        )
        
        return {
            'processing_system': processing_system,
            'system1_effect': system1_effect,
            'system2_effect': system2_effect,
            'ad_effectiveness': ad_effectiveness
        }
    
    def brand_positioning_map(self, brand_data, competitor_data):
        """브랜드 포지셔닝 맵 생성"""
        # 주요 속성 차원에서 브랜드 위치 분석
        
        attributes = ['quality', 'price', 'innovation', 'reliability', 'prestige']
        
        # 전체 브랜드 데이터 결합
        all_brands = pd.concat([brand_data, competitor_data])
        
        # 표준화
        scaled_data = self.scaler.fit_transform(all_brands[attributes])
        
        # PCA를 통한 차원 축소
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        brand_positions = pca.fit_transform(scaled_data)
        
        # 클러스터링을 통한 경쟁 그룹 식별
        kmeans = KMeans(n_clusters=3, random_state=42)
        competitive_groups = kmeans.fit_predict(brand_positions)
        
        # 포지셔닝 맵 시각화
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(brand_positions[:, 0], brand_positions[:, 1], 
                           c=competitive_groups, cmap='viridis', s=100, alpha=0.7)
        
        # 브랜드명 라벨링
        for i, brand in enumerate(all_brands['brand_name']):
            plt.annotate(brand, (brand_positions[i, 0], brand_positions[i, 1]), 
                        xytext=(5, 5), textcoords='offset points')
        
        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
        plt.title('Brand Positioning Map')
        plt.colorbar(scatter, label='Competitive Group')
        plt.grid(True, alpha=0.3)
        
        return {
            'positions': brand_positions,
            'competitive_groups': competitive_groups,
            'pca_components': pca.components_,
            'explained_variance': pca.explained_variance_ratio_
        }
    
    def attitude_behavior_gap_analysis(self, attitude_data, behavior_data):
        """태도-행동 격차 분석"""
        # 태도와 실제 행동 간의 불일치 원인 분석
        
        # 태도 점수 계산
        attitude_score = (
            attitude_data['cognitive_component'] * 0.4 +
            attitude_data['affective_component'] * 0.3 +
            attitude_data['conative_component'] * 0.3
        )
        
        # 행동 점수 계산 (구매, 추천, 재구매 등)
        behavior_score = (
            behavior_data['purchase_behavior'] * 0.4 +
            behavior_data['recommendation_behavior'] * 0.3 +
            behavior_data['loyalty_behavior'] * 0.3
        )
        
        # 태도-행동 격차 계산
        attitude_behavior_gap = attitude_score - behavior_score
        
        # 격차 원인 분석
        barrier_factors = {
            'situational_constraints': attitude_data['situational_barriers'],
            'social_pressure': attitude_data['social_influence'],
            'resource_limitations': attitude_data['resource_constraints'],
            'habit_strength': behavior_data['existing_habits']
        }
        
        # 격차 설명 변수 중요도 분석
        from sklearn.ensemble import RandomForestRegressor
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        X = pd.DataFrame(barrier_factors)
        y = attitude_behavior_gap
        
        rf_model.fit(X, y)
        feature_importance = dict(zip(X.columns, rf_model.feature_importances_))
        
        return {
            'attitude_score': attitude_score,
            'behavior_score': behavior_score,
            'gap': attitude_behavior_gap,
            'barrier_importance': feature_importance,
            'gap_segments': pd.qcut(attitude_behavior_gap, q=3, labels=['Low', 'Medium', 'High'])
        }

# 실습 예제: 종합 광고 효과 분석
def comprehensive_ad_effectiveness_analysis():
    """종합적인 광고 효과성 분석"""
    
    # 샘플 데이터 생성
    np.random.seed(42)
    n_users = 1000
    
    # 사용자 데이터
    user_data = pd.DataFrame({
        'user_id': range(n_users),
        'product_knowledge': np.random.beta(2, 5, n_users),
        'purchase_importance': np.random.beta(3, 3, n_users),
        'time_available': np.random.beta(2, 3, n_users),
        'cognitive_load': np.random.beta(2, 3, n_users),
        'motivation': np.random.beta(3, 2, n_users),
        'analytical_thinking': np.random.beta(3, 3, n_users)
    })
    
    # 광고 데이터
    ad_data = pd.DataFrame({
        'campaign_id': range(n_users),
        'argument_quality': np.random.beta(3, 2, n_users),
        'evidence_strength': np.random.beta(3, 3, n_users),
        'source_credibility': np.random.beta(4, 2, n_users),
        'peripheral_cues': np.random.beta(2, 3, n_users),
        'creative_quality': np.random.beta(3, 2, n_users),
        'targeting_accuracy': np.random.beta(4, 3, n_users),
        'message_relevance': np.random.beta(3, 2, n_users),
        'emotional_appeal': np.random.beta(3, 3, n_users),
        'visual_appeal': np.random.beta(3, 2, n_users),
        'information_complexity': np.random.beta(2, 3, n_users)
    })
    
    # 분석기 초기화
    analyzer = ConsumerBehaviorAnalyzer()
    
    # 1. 정교화 가능성 모델 분석
    elm_results = analyzer.elaboration_likelihood_model(user_data, ad_data)
    
    # 2. 이중 처리 이론 분석
    user_state = user_data[['cognitive_load', 'time_pressure', 'motivation', 'analytical_thinking']].copy()
    user_state['time_pressure'] = np.random.beta(2, 3, n_users)  # 시간 압박 추가
    
    dual_process_results = analyzer.dual_process_theory_model(ad_data, user_state)
    
    # 결과 시각화
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # ELM 결과 시각화
    processing_counts = pd.Series(elm_results['processing_route']).value_counts()
    axes[0, 0].pie(processing_counts.values, labels=processing_counts.index, autopct='%1.1f%%')
    axes[0, 0].set_title('Processing Route Distribution (ELM)')
    
    # 관여도별 태도 변화
    axes[0, 1].scatter(elm_results['involvement_score'], elm_results['attitude_change'], alpha=0.6)
    axes[0, 1].set_xlabel('Involvement Score')
    axes[0, 1].set_ylabel('Attitude Change')
    axes[0, 1].set_title('Involvement vs Attitude Change')
    
    # 처리 시스템 분포
    system_counts = pd.Series(dual_process_results['processing_system']).value_counts()
    system_labels = ['System 1 (Intuitive)', 'System 2 (Analytical)']
    axes[1, 0].bar(system_labels, [system_counts.get(0, 0), system_counts.get(1, 0)])
    axes[1, 0].set_title('Processing System Usage')
    
    # 광고 효과성 분포
    axes[1, 1].hist(dual_process_results['ad_effectiveness'], bins=30, alpha=0.7)
    axes[1, 1].set_xlabel('Ad Effectiveness Score')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_title('Ad Effectiveness Distribution')
    
    plt.tight_layout()
    plt.show()
    
    return {
        'elm_results': elm_results,
        'dual_process_results': dual_process_results,
        'user_data': user_data,
        'ad_data': ad_data
    }

# 메인 실행
if __name__ == "__main__":
    print("=== 광고 이론 기초 실습 ===")
    print("정교화 가능성 모델과 이중 처리 이론을 활용한 광고 효과 분석")
    
    results = comprehensive_ad_effectiveness_analysis()
    
    print(f"\n분석 완료:")
    print(f"- 중앙 경로 처리 사용자: {sum(results['elm_results']['processing_route'] == 'central')}명")
    print(f"- 주변 경로 처리 사용자: {sum(results['elm_results']['processing_route'] == 'peripheral')}명")
    print(f"- System 2 사용자: {sum(results['dual_process_results']['processing_system'] == 1)}명")
    print(f"- 평균 광고 효과성: {np.mean(results['dual_process_results']['ad_effectiveness']):.3f}")
```

## 🚀 프로젝트
1. **소비자 심리 분석 대시보드** - ELM 모델 기반 실시간 분석
2. **브랜드 포지셔닝 맵** - 경쟁사 대비 위치 분석
3. **태도-행동 격차 예측** - 구매 전환 장벽 식별
4. **광고 메시지 최적화** - 인지 처리 모델 기반 크리에이티브 개선