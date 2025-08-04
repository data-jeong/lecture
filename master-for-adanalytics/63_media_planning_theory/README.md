# 63. Media Planning Theory - 미디어 플래닝 이론

## 📚 과정 소개
데이터 기반 미디어 플래닝의 핵심 이론을 마스터합니다. 도달률-빈도 최적화부터 크로스 미디어 효과까지 과학적 미디어 전략 수립 방법을 학습합니다.

## 🎯 학습 목표
- 도달률-빈도 이론과 효과적 빈도 모델링
- 미디어 믹스 최적화와 예산 배분 전략
- 크로스 미디어 시너지 효과 분석
- 실시간 미디어 성과 모니터링과 최적화

## 📖 주요 내용

### 미디어 플래닝 최적화 시스템
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats, optimize
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class MediaPlanningOptimizer:
    """미디어 플래닝 최적화를 위한 종합 클래스"""
    
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.media_efficiency_curves = {}
        
    def reach_frequency_optimization(self, media_data, budget_constraint, target_audience):
        """도달률-빈도 최적화"""
        
        # 도달률 곡선 모델링 (중복 제거)
        def reach_curve(impressions, a=1.0, b=0.8, c=0.1):
            """도달률 = 1 - e^(-a * (impressions/target_audience)^b) - c"""
            exposure_rate = impressions / target_audience
            return (1 - np.exp(-a * (exposure_rate ** b))) * (1 - c)
        
        # 빈도 분포 모델링
        def frequency_distribution(impressions, reach):
            """평균 빈도 = 노출 / 도달률"""
            if reach > 0:
                return impressions / (reach * target_audience)
            return 0
        
        # 효과적 빈도 모델 (S-curve)
        def effective_frequency_curve(frequency, threshold=3.0, saturation=10.0):
            """효과적 빈도 곡선"""
            if frequency < threshold:
                return 0.3 * (frequency / threshold)
            elif frequency <= saturation:
                return 0.3 + 0.7 * ((frequency - threshold) / (saturation - threshold))
            else:
                return 1.0 - 0.2 * (1 - np.exp(-(frequency - saturation)))
        
        # 미디어별 최적화
        optimized_allocation = {}
        total_effectiveness = 0
        
        for media_type in media_data['media_type'].unique():
            media_subset = media_data[media_data['media_type'] == media_type]
            
            # 비용 효율성 계산
            cost_per_impression = media_subset['cost'] / media_subset['impressions']
            
            # 품질 가중치 적용
            quality_weight = (
                media_subset['viewability'] * 0.3 +
                media_subset['brand_safety'] * 0.2 +
                media_subset['audience_quality'] * 0.5
            )
            
            # 최적 임프레션 수 계산
            def objective_function(impressions):
                reach = reach_curve(impressions)
                frequency = frequency_distribution(impressions, reach)
                effectiveness = effective_frequency_curve(frequency)
                return -(reach * effectiveness * quality_weight.mean())
            
            # 예산 제약 하에서 최적화
            max_impressions = budget_constraint / cost_per_impression.min()
            
            result = optimize.minimize_scalar(
                objective_function,
                bounds=(0, max_impressions),
                method='bounded'
            )
            
            optimal_impressions = result.x
            optimal_reach = reach_curve(optimal_impressions)
            optimal_frequency = frequency_distribution(optimal_impressions, optimal_reach)
            optimal_cost = optimal_impressions * cost_per_impression.mean()
            
            optimized_allocation[media_type] = {
                'impressions': optimal_impressions,
                'reach': optimal_reach,
                'frequency': optimal_frequency,
                'cost': optimal_cost,
                'effectiveness': -result.fun
            }
            
            total_effectiveness += -result.fun
        
        return {
            'allocation': optimized_allocation,
            'total_effectiveness': total_effectiveness,
            'reach_frequency_curves': self._generate_rf_curves(optimized_allocation)
        }
    
    def media_mix_modeling(self, media_spend_data, sales_data, external_factors=None):
        """미디어 믹스 모델링 (MMM)"""
        
        # 미디어 채널별 광고스톡(Adstock) 적용
        def apply_adstock(media_series, decay_rate=0.5, max_lag=4):
            """광고스톡 변환 (지연 효과)"""
            adstock_series = media_series.copy()
            
            for lag in range(1, max_lag + 1):
                lagged_effect = media_series.shift(lag) * (decay_rate ** lag)
                adstock_series += lagged_effect.fillna(0)
            
            return adstock_series
        
        # 포화 곡선 적용 (수확 체감)
        def apply_saturation(adstock_series, saturation_point=0.8):
            """포화 곡선 변환"""
            normalized = adstock_series / adstock_series.max()
            saturated = saturation_point * normalized / (saturation_point - normalized + 1)
            return saturated * adstock_series.max()
        
        # 각 미디어 채널에 변환 적용
        transformed_media = pd.DataFrame(index=media_spend_data.index)
        
        for channel in media_spend_data.columns:
            # 1단계: 광고스톡 적용
            adstock = apply_adstock(media_spend_data[channel])
            
            # 2단계: 포화 곡선 적용
            saturated = apply_saturation(adstock)
            
            transformed_media[f'{channel}_transformed'] = saturated
        
        # 베이스라인 효과 계산 (유기적 성장)
        baseline_trend = np.arange(len(sales_data)) * (sales_data.mean() * 0.001)
        seasonal_effect = np.sin(2 * np.pi * np.arange(len(sales_data)) / 52) * (sales_data.std() * 0.1)
        baseline = sales_data.mean() + baseline_trend + seasonal_effect
        
        # 외부 요인 통합
        if external_factors is not None:
            transformed_media = pd.concat([transformed_media, external_factors], axis=1)
        
        # 미디어 기여도 모델 훈련
        X = transformed_media.fillna(0)
        y = sales_data - baseline  # 베이스라인 제거
        
        # 랜덤 포레스트 모델 사용 (비선형 관계 포착)
        rf_model = RandomForestRegressor(n_estimators=200, random_state=42)
        rf_model.fit(X, y)
        
        # 채널별 기여도 계산
        feature_importance = dict(zip(X.columns, rf_model.feature_importances_))
        
        # ROAS (Return on Ad Spend) 계산
        channel_roas = {}
        for channel in media_spend_data.columns:
            if f'{channel}_transformed' in feature_importance:
                contribution = feature_importance[f'{channel}_transformed'] * y.sum()
                spend = media_spend_data[channel].sum()
                if spend > 0:
                    channel_roas[channel] = contribution / spend
                else:
                    channel_roas[channel] = 0
        
        # 예측 및 검증
        y_pred = rf_model.predict(X) + baseline
        model_accuracy = 1 - np.mean(np.abs(y_pred - sales_data) / sales_data)
        
        return {
            'model': rf_model,
            'transformed_features': transformed_media,
            'feature_importance': feature_importance,
            'channel_roas': channel_roas,
            'baseline_effect': baseline,
            'model_accuracy': model_accuracy,
            'predictions': y_pred
        }
    
    def cross_media_synergy_analysis(self, media_interactions, performance_data):
        """크로스 미디어 시너지 분석"""
        
        # 미디어 조합별 시너지 효과 측정
        synergy_matrix = pd.DataFrame(
            index=media_interactions.columns,
            columns=media_interactions.columns
        )
        
        # 페어와이즈 시너지 계산
        for media1 in media_interactions.columns:
            for media2 in media_interactions.columns:
                if media1 != media2:
                    # 개별 효과
                    solo_effect1 = self._calculate_solo_effect(media1, media_interactions, performance_data)
                    solo_effect2 = self._calculate_solo_effect(media2, media_interactions, performance_data)
                    
                    # 결합 효과
                    combined_effect = self._calculate_combined_effect(
                        [media1, media2], media_interactions, performance_data
                    )
                    
                    # 시너지 = 결합 효과 - 개별 효과 합
                    synergy = combined_effect - (solo_effect1 + solo_effect2)
                    synergy_matrix.loc[media1, media2] = synergy
                else:
                    synergy_matrix.loc[media1, media2] = 0
        
        # 최적 미디어 조합 식별
        best_combinations = self._find_optimal_combinations(synergy_matrix, top_n=5)
        
        # 시너지 타이밍 분석
        timing_analysis = self._analyze_synergy_timing(media_interactions, performance_data)
        
        # 시너지 히트맵 생성
        plt.figure(figsize=(10, 8))
        sns.heatmap(synergy_matrix.astype(float), annot=True, cmap='RdYlBu_r', center=0)
        plt.title('Cross-Media Synergy Matrix')
        plt.tight_layout()
        
        return {
            'synergy_matrix': synergy_matrix,
            'best_combinations': best_combinations,
            'timing_analysis': timing_analysis,
            'synergy_score': synergy_matrix.values.sum()
        }
    
    def frequency_capping_optimization(self, exposure_data, conversion_data):
        """빈도 캐핑 최적화"""
        
        # 빈도별 전환율 분석
        frequency_performance = exposure_data.groupby('frequency').agg({
            'conversions': 'sum',
            'impressions': 'sum',
            'cost': 'sum'
        }).reset_index()
        
        frequency_performance['conversion_rate'] = (
            frequency_performance['conversions'] / frequency_performance['impressions']
        )
        frequency_performance['cost_per_conversion'] = (
            frequency_performance['cost'] / frequency_performance['conversions']
        )
        
        # 한계 효과 분석
        frequency_performance['marginal_conversion_rate'] = (
            frequency_performance['conversion_rate'].diff().fillna(0)
        )
        frequency_performance['marginal_cost_efficiency'] = (
            frequency_performance['cost_per_conversion'].diff().fillna(0)
        )
        
        # 최적 빈도 캐핑 점 찾기
        # 한계 전환율이 음수가 되기 시작하는 지점
        optimal_frequency = self._find_optimal_frequency_cap(frequency_performance)
        
        # 빈도 캐핑 시뮬레이션
        capping_simulation = self._simulate_frequency_capping(
            exposure_data, range(1, 21), conversion_data
        )
        
        # 시각화
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 빈도별 전환율
        axes[0, 0].plot(frequency_performance['frequency'], 
                       frequency_performance['conversion_rate'], 'bo-')
        axes[0, 0].axvline(x=optimal_frequency, color='red', linestyle='--', 
                          label=f'Optimal Cap: {optimal_frequency}')
        axes[0, 0].set_xlabel('Frequency')
        axes[0, 0].set_ylabel('Conversion Rate')
        axes[0, 0].set_title('Conversion Rate by Frequency')
        axes[0, 0].legend()
        
        # 한계 전환율
        axes[0, 1].plot(frequency_performance['frequency'], 
                       frequency_performance['marginal_conversion_rate'], 'ro-')
        axes[0, 1].axhline(y=0, color='gray', linestyle='--')
        axes[0, 1].set_xlabel('Frequency')
        axes[0, 1].set_ylabel('Marginal Conversion Rate')
        axes[0, 1].set_title('Marginal Conversion Rate')
        
        # 비용 효율성
        axes[1, 0].plot(frequency_performance['frequency'], 
                       frequency_performance['cost_per_conversion'], 'go-')
        axes[1, 0].set_xlabel('Frequency')
        axes[1, 0].set_ylabel('Cost per Conversion')
        axes[1, 0].set_title('Cost Efficiency by Frequency')
        
        # 캐핑 시뮬레이션 결과
        caps = list(capping_simulation.keys())
        rois = [sim['roi'] for sim in capping_simulation.values()]
        axes[1, 1].plot(caps, rois, 'mo-')
        axes[1, 1].axvline(x=optimal_frequency, color='red', linestyle='--')
        axes[1, 1].set_xlabel('Frequency Cap')
        axes[1, 1].set_ylabel('ROI')
        axes[1, 1].set_title('ROI by Frequency Cap')
        
        plt.tight_layout()
        plt.show()
        
        return {
            'frequency_performance': frequency_performance,
            'optimal_frequency': optimal_frequency,
            'capping_simulation': capping_simulation,
            'efficiency_gain': self._calculate_efficiency_gain(capping_simulation, optimal_frequency)
        }
    
    def dayparting_optimization(self, hourly_performance_data, audience_data):
        """데이파팅 최적화"""
        
        # 시간대별 성과 분석
        hourly_analysis = hourly_performance_data.groupby('hour').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum',
            'cost': 'sum'
        }).reset_index()
        
        hourly_analysis['ctr'] = hourly_analysis['clicks'] / hourly_analysis['impressions']
        hourly_analysis['conversion_rate'] = hourly_analysis['conversions'] / hourly_analysis['clicks']
        hourly_analysis['cpc'] = hourly_analysis['cost'] / hourly_analysis['clicks']
        hourly_analysis['roas'] = hourly_analysis['conversions'] / hourly_analysis['cost']
        
        # 오디언스 활동 패턴 분석
        audience_activity = audience_data.groupby('hour')['active_users'].sum().reset_index()
        
        # 효율성 점수 계산 (ROAS × 오디언스 활동도)
        merged_data = hourly_analysis.merge(audience_activity, on='hour')
        merged_data['efficiency_score'] = (
            merged_data['roas'] * merged_data['active_users'] / merged_data['active_users'].max()
        )
        
        # 최적 시간대 식별
        optimal_hours = merged_data.nlargest(8, 'efficiency_score')['hour'].tolist()
        
        # 예산 재배분 시뮬레이션
        current_allocation = hourly_analysis.set_index('hour')['cost'].to_dict()
        optimized_allocation = self._optimize_hourly_budget(merged_data, current_allocation)
        
        # 시각화
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 시간대별 ROAS
        axes[0, 0].bar(merged_data['hour'], merged_data['roas'], alpha=0.7)
        axes[0, 0].set_xlabel('Hour of Day')
        axes[0, 0].set_ylabel('ROAS')
        axes[0, 0].set_title('ROAS by Hour')
        
        # 오디언스 활동도
        axes[0, 1].plot(merged_data['hour'], merged_data['active_users'], 'o-', color='orange')
        axes[0, 1].set_xlabel('Hour of Day')
        axes[0, 1].set_ylabel('Active Users')
        axes[0, 1].set_title('Audience Activity Pattern')
        
        # 효율성 점수
        axes[1, 0].bar(merged_data['hour'], merged_data['efficiency_score'], 
                      color=['red' if h in optimal_hours else 'lightblue' for h in merged_data['hour']])
        axes[1, 0].set_xlabel('Hour of Day')
        axes[1, 0].set_ylabel('Efficiency Score')
        axes[1, 0].set_title('Efficiency Score by Hour (Red = Optimal)')
        
        # 예산 재배분 비교
        hours = list(current_allocation.keys())
        current_budgets = list(current_allocation.values())
        optimized_budgets = [optimized_allocation.get(h, 0) for h in hours]
        
        x = np.arange(len(hours))
        width = 0.35
        
        axes[1, 1].bar(x - width/2, current_budgets, width, label='Current', alpha=0.7)
        axes[1, 1].bar(x + width/2, optimized_budgets, width, label='Optimized', alpha=0.7)
        axes[1, 1].set_xlabel('Hour of Day')
        axes[1, 1].set_ylabel('Budget Allocation')
        axes[1, 1].set_title('Budget Allocation Comparison')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(hours)
        axes[1, 1].legend()
        
        plt.tight_layout()
        plt.show()
        
        return {
            'hourly_performance': merged_data,
            'optimal_hours': optimal_hours,
            'current_allocation': current_allocation,
            'optimized_allocation': optimized_allocation,
            'efficiency_improvement': self._calculate_dayparting_improvement(
                current_allocation, optimized_allocation, merged_data
            )
        }
    
    def media_attribution_modeling(self, touchpoint_data, conversion_data):
        """미디어 어트리뷰션 모델링"""
        
        # 다양한 어트리뷰션 모델 구현
        attribution_models = {
            'first_touch': self._first_touch_attribution,
            'last_touch': self._last_touch_attribution,
            'linear': self._linear_attribution,
            'time_decay': self._time_decay_attribution,
            'position_based': self._position_based_attribution,
            'data_driven': self._data_driven_attribution
        }
        
        # 각 모델별 어트리뷰션 결과
        attribution_results = {}
        
        for model_name, model_func in attribution_models.items():
            attribution_results[model_name] = model_func(touchpoint_data, conversion_data)
        
        # 모델 비교 및 검증
        model_comparison = self._compare_attribution_models(attribution_results, conversion_data)
        
        # 최적 모델 선택
        best_model = max(model_comparison.items(), key=lambda x: x[1]['accuracy'])[0]
        
        # 어트리뷰션 시각화
        self._visualize_attribution_results(attribution_results, model_comparison)
        
        return {
            'attribution_results': attribution_results,
            'model_comparison': model_comparison,
            'best_model': best_model,
            'recommended_attribution': attribution_results[best_model]
        }

# 보조 메서드들
    def _calculate_solo_effect(self, media, interactions, performance):
        """개별 미디어 효과 계산"""
        solo_periods = interactions[interactions[media] > 0]
        other_media = [col for col in interactions.columns if col != media]
        solo_periods = solo_periods[solo_periods[other_media].sum(axis=1) == 0]
        
        if len(solo_periods) > 0:
            return performance.loc[solo_periods.index].mean()
        return 0
    
    def _calculate_combined_effect(self, media_list, interactions, performance):
        """결합 미디어 효과 계산"""
        combined_periods = interactions[
            (interactions[media_list].sum(axis=1) == len(media_list)) &
            (interactions.drop(columns=media_list).sum(axis=1) == 0)
        ]
        
        if len(combined_periods) > 0:
            return performance.loc[combined_periods.index].mean()
        return 0
    
    def _find_optimal_frequency_cap(self, frequency_performance):
        """최적 빈도 캐핑 점 찾기"""
        # 한계 전환율이 처음으로 음수가 되는 지점
        negative_marginal = frequency_performance[
            frequency_performance['marginal_conversion_rate'] < 0
        ]
        
        if len(negative_marginal) > 0:
            return negative_marginal.iloc[0]['frequency'] - 1
        else:
            return frequency_performance['frequency'].max()

# 실습 예제: 종합 미디어 플래닝
def comprehensive_media_planning():
    """종합적인 미디어 플래닝 최적화"""
    
    # 샘플 데이터 생성
    np.random.seed(42)
    
    # 미디어 성과 데이터
    media_data = pd.DataFrame({
        'media_type': ['TV', 'Digital', 'Radio', 'Print', 'OOH'] * 20,
        'impressions': np.random.uniform(100000, 1000000, 100),
        'cost': np.random.uniform(10000, 100000, 100),
        'viewability': np.random.uniform(0.6, 0.95, 100),
        'brand_safety': np.random.uniform(0.7, 1.0, 100),
        'audience_quality': np.random.uniform(0.5, 0.9, 100)
    })
    
    # 빈도 노출 데이터
    exposure_data = pd.DataFrame({
        'frequency': np.random.randint(1, 15, 1000),
        'impressions': np.random.uniform(1000, 10000, 1000),
        'conversions': np.random.poisson(5, 1000),
        'cost': np.random.uniform(100, 1000, 1000)
    })
    
    # 시간대별 성과 데이터
    hourly_data = pd.DataFrame({
        'hour': list(range(24)) * 30,
        'impressions': np.random.uniform(1000, 10000, 720),
        'clicks': np.random.uniform(50, 500, 720),
        'conversions': np.random.uniform(5, 50, 720),
        'cost': np.random.uniform(100, 1000, 720)
    })
    
    # 오디언스 활동 데이터
    audience_data = pd.DataFrame({
        'hour': range(24),
        'active_users': [
            500, 300, 200, 150, 100, 200, 400, 800, 1200, 1000,
            900, 950, 1100, 1200, 1300, 1400, 1500, 1600, 1400, 1200, 1000, 800, 700, 600
        ]
    })
    
    # 최적화 도구 초기화
    optimizer = MediaPlanningOptimizer()
    
    # 1. 도달률-빈도 최적화
    rf_results = optimizer.reach_frequency_optimization(
        media_data, budget_constraint=500000, target_audience=1000000
    )
    
    # 2. 빈도 캐핑 최적화
    frequency_results = optimizer.frequency_capping_optimization(
        exposure_data, exposure_data
    )
    
    # 3. 데이파팅 최적화
    daypart_results = optimizer.dayparting_optimization(
        hourly_data, audience_data
    )
    
    # 결과 요약
    print("=== 미디어 플래닝 최적화 결과 ===")
    print(f"최적 빈도 캐핑: {frequency_results['optimal_frequency']}회")
    print(f"최적 시간대: {len(daypart_results['optimal_hours'])}개 시간대")
    print(f"총 효과성 점수: {rf_results['total_effectiveness']:.3f}")
    
    return {
        'rf_results': rf_results,
        'frequency_results': frequency_results,
        'daypart_results': daypart_results
    }

# 메인 실행
if __name__ == "__main__":
    print("=== 미디어 플래닝 이론 실습 ===")
    print("도달률-빈도 최적화와 미디어 믹스 모델링")
    
    results = comprehensive_media_planning()
    
    print(f"\n최적화 완료:")
    print(f"- 빈도 캐핑 효율성 개선: {results['frequency_results']['efficiency_gain']:.2%}")
    print(f"- 데이파팅 개선 효과: {results['daypart_results']['efficiency_improvement']:.2%}")
```

## 🚀 프로젝트
1. **미디어 믹스 모델링 플랫폼** - MMM 기반 예산 최적화 시스템
2. **실시간 빈도 캐핑 엔진** - 동적 노출 빈도 제어 시스템  
3. **크로스 미디어 시너지 분석** - 채널 간 상호작용 효과 측정
4. **어트리뷰션 모델링 대시보드** - 다중 터치포인트 기여도 분석