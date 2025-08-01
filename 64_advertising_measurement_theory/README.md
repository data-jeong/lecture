# 64. Advertising Measurement Theory - 광고 측정 이론

## 📚 과정 소개
광고 효과 측정의 과학적 접근법을 마스터합니다. Adstock 모델부터 브랜드 리프트까지 정확한 광고 ROI 측정과 최적화 방법을 학습합니다.

## 🎯 학습 목표
- Adstock과 광고 지연 효과 모델링
- 브랜드 인지도와 광고 마모 이론 적용
- 장단기 광고 효과 분해와 측정
- 멀티 터치 어트리뷰션과 증분 리프트 분석

## 📖 주요 내용

### 광고 효과 측정 시스템
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats, optimize
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')

class AdvertisingMeasurementSystem:
    """광고 효과 측정을 위한 종합 클래스"""
    
    def __init__(self):
        self.models = {}
        self.adstock_parameters = {}
        self.saturation_curves = {}
        
    def adstock_modeling(self, media_data, sales_data, max_lag=12):
        """Adstock 모델링 - 광고의 지연 및 누적 효과"""
        
        def geometric_adstock(media_series, decay_rate):
            """기하급수적 감소 Adstock"""
            adstock_series = media_series.copy()
            
            for i in range(1, len(media_series)):
                adstock_series.iloc[i] += adstock_series.iloc[i-1] * decay_rate
            
            return adstock_series
        
        def convoluted_adstock(media_series, decay_params):
            """합성곱 Adstock (더 유연한 감소 패턴)"""
            adstock_series = np.zeros(len(media_series))
            
            for i in range(len(media_series)):
                for lag in range(min(i+1, len(decay_params))):
                    adstock_series[i] += media_series.iloc[i-lag] * decay_params[lag]
            
            return pd.Series(adstock_series, index=media_series.index)
        
        # 각 미디어 채널별 최적 Adstock 파라미터 찾기
        optimal_adstock = {}
        
        for channel in media_data.columns:
            # 격자 탐색으로 최적 decay rate 찾기
            best_r2 = -np.inf
            best_params = {}
            
            for decay_rate in np.arange(0.1, 0.9, 0.1):
                # Adstock 적용
                adstock_media = geometric_adstock(media_data[channel], decay_rate)
                
                # 간단한 회귀 모델로 성과 예측
                X = adstock_media.values.reshape(-1, 1)
                y = sales_data.values
                
                model = LinearRegression()
                model.fit(X, y)
                
                r2 = model.score(X, y)
                
                if r2 > best_r2:
                    best_r2 = r2
                    best_params = {
                        'decay_rate': decay_rate,
                        'r2_score': r2,
                        'adstock_series': adstock_media
                    }
            
            optimal_adstock[channel] = best_params
            self.adstock_parameters[channel] = best_params['decay_rate']
        
        # 고급 합성곱 Adstock 모델링
        advanced_adstock = {}
        for channel in media_data.columns:
            # 더 정교한 지연 효과 패턴 학습
            decay_params = self._optimize_convoluted_adstock(
                media_data[channel], sales_data, max_lag
            )
            
            advanced_adstock[channel] = {
                'decay_params': decay_params,
                'adstock_series': convoluted_adstock(media_data[channel], decay_params)
            }
        
        return {
            'geometric_adstock': optimal_adstock,
            'convoluted_adstock': advanced_adstock,
            'adstock_visualization': self._visualize_adstock_effects(optimal_adstock)
        }
    
    def saturation_curve_modeling(self, media_spend, response_data):
        """포화 곡선 모델링 - 수확 체감 법칙"""
        
        def hill_saturation(x, alpha, gamma):
            """Hill 변환 (S-curve)"""
            return alpha * (x ** gamma) / (x ** gamma + 1)
        
        def michaelis_menten(x, vmax, km):
            """Michaelis-Menten 포화 곡선"""
            return (vmax * x) / (km + x)
        
        def exponential_saturation(x, a, b):
            """지수적 포화 곡선"""
            return a * (1 - np.exp(-b * x))
        
        saturation_models = {}
        
        for channel in media_spend.columns:
            x_data = media_spend[channel].values
            y_data = response_data.values
            
            # 각 포화 모델 피팅
            models = {
                'hill': (hill_saturation, [1.0, 1.0]),
                'michaelis_menten': (michaelis_menten, [max(y_data), np.median(x_data)]),
                'exponential': (exponential_saturation, [max(y_data), 0.001])
            }
            
            best_model = None
            best_r2 = -np.inf
            
            for model_name, (func, initial_params) in models.items():
                try:
                    # 곡선 피팅
                    popt, _ = optimize.curve_fit(func, x_data, y_data, p0=initial_params)
                    
                    # 예측 및 평가
                    y_pred = func(x_data, *popt)
                    r2 = r2_score(y_data, y_pred)
                    
                    if r2 > best_r2:
                        best_r2 = r2
                        best_model = {
                            'name': model_name,
                            'function': func,
                            'parameters': popt,
                            'r2_score': r2,
                            'predictions': y_pred
                        }
                
                except Exception as e:
                    continue
            
            saturation_models[channel] = best_model
            self.saturation_curves[channel] = best_model
        
        # 최적 예산 포인트 계산
        optimal_spend_points = self._calculate_optimal_spend_points(saturation_models)
        
        return {
            'saturation_models': saturation_models,
            'optimal_spend_points': optimal_spend_points,
            'saturation_visualization': self._visualize_saturation_curves(saturation_models, media_spend)
        }
    
    def brand_lift_measurement(self, exposed_group, control_group, pre_metrics, post_metrics):
        """브랜드 리프트 측정"""
        
        # 사전-사후 비교 분석
        def calculate_lift(exposed_pre, exposed_post, control_pre, control_post):
            """리프트 계산 공식"""
            exposed_change = (exposed_post - exposed_pre) / exposed_pre
            control_change = (control_post - control_pre) / control_pre
            
            return exposed_change - control_change
        
        lift_metrics = {}
        
        # 각 브랜드 메트릭별 리프트 계산
        for metric in pre_metrics.columns:
            # 노출 그룹 리프트
            exposed_lift = calculate_lift(
                pre_metrics[pre_metrics['group'] == 'exposed'][metric].mean(),
                post_metrics[post_metrics['group'] == 'exposed'][metric].mean(),
                pre_metrics[pre_metrics['group'] == 'control'][metric].mean(),
                post_metrics[post_metrics['group'] == 'control'][metric].mean()
            )
            
            # 통계적 유의성 검정
            exposed_post_values = post_metrics[post_metrics['group'] == 'exposed'][metric]
            control_post_values = post_metrics[post_metrics['group'] == 'control'][metric]
            
            t_stat, p_value = stats.ttest_ind(exposed_post_values, control_post_values)
            
            # 효과 크기 (Cohen's d)
            pooled_std = np.sqrt(((len(exposed_post_values)-1) * exposed_post_values.std()**2 + 
                                 (len(control_post_values)-1) * control_post_values.std()**2) / 
                                (len(exposed_post_values) + len(control_post_values) - 2))
            
            cohens_d = (exposed_post_values.mean() - control_post_values.mean()) / pooled_std
            
            lift_metrics[metric] = {
                'lift_percentage': exposed_lift * 100,
                't_statistic': t_stat,
                'p_value': p_value,
                'cohens_d': cohens_d,
                'significance': 'Significant' if p_value < 0.05 else 'Not Significant',
                'effect_size': self._interpret_effect_size(abs(cohens_d))
            }
        
        # 종합 브랜드 건강도 점수
        brand_health_score = self._calculate_brand_health_score(lift_metrics)
        
        # 시각화
        self._visualize_brand_lift(lift_metrics, pre_metrics, post_metrics)
        
        return {
            'lift_metrics': lift_metrics,
            'brand_health_score': brand_health_score,
            'statistical_power': self._calculate_statistical_power(exposed_group, control_group)
        }
    
    def incrementality_testing(self, test_data, control_data, experiment_period):
        """증분 효과 테스트"""
        
        # Difference-in-Differences 분석
        def did_analysis(test_before, test_after, control_before, control_after):
            """이중차분법 분석"""
            test_change = test_after - test_before
            control_change = control_after - control_before
            
            incremental_effect = test_change - control_change
            
            # 표준 오차 계산
            test_se = np.sqrt(test_before.var() + test_after.var())
            control_se = np.sqrt(control_before.var() + control_after.var())
            combined_se = np.sqrt(test_se**2 + control_se**2)
            
            # t-통계량과 p-값
            t_stat = incremental_effect / combined_se
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=len(test_before)+len(control_before)-2))
            
            return {
                'incremental_effect': incremental_effect,
                'standard_error': combined_se,
                't_statistic': t_stat,
                'p_value': p_value
            }
        
        # 실험 기간 전후 데이터 분리
        pre_period = experiment_period['start'] - pd.Timedelta(days=30)
        
        test_before = test_data[test_data['date'] < experiment_period['start']]['metric']
        test_after = test_data[test_data['date'] >= experiment_period['start']]['metric']
        control_before = control_data[control_data['date'] < experiment_period['start']]['metric']
        control_after = control_data[control_data['date'] >= experiment_period['start']]['metric']
        
        # DID 분석 실행
        did_results = did_analysis(test_before, test_after, control_before, control_after)
        
        # 합성 대조군 방법 (Synthetic Control)
        synthetic_control = self._create_synthetic_control(test_data, control_data, experiment_period)
        
        # 인과 추론 모델
        causal_impact = self._causal_impact_analysis(test_data, control_data, experiment_period)
        
        return {
            'did_results': did_results,
            'synthetic_control': synthetic_control,
            'causal_impact': causal_impact,
            'incremental_roi': self._calculate_incremental_roi(did_results, experiment_period)
        }
    
    def attribution_decay_modeling(self, touchpoint_data, conversion_data):
        """어트리뷰션 감쇠 모델링"""
        
        # 시간 기반 감쇠 함수들
        def linear_decay(days_since_touch, max_days=30):
            """선형 감쇠"""
            return max(0, 1 - days_since_touch / max_days)
        
        def exponential_decay(days_since_touch, decay_rate=0.1):
            """지수 감쇠"""
            return np.exp(-decay_rate * days_since_touch)
        
        def u_shaped_decay(days_since_touch, max_days=30):
            """U자형 감쇠 (최근성 + 첫인상 효과)"""
            normalized_days = days_since_touch / max_days
            return 0.5 * (1 - normalized_days) + 0.5 * np.exp(-5 * normalized_days)
        
        # 터치포인트별 기여도 계산
        attribution_weights = {}
        
        for conversion_id in conversion_data['conversion_id'].unique():
            # 해당 전환의 터치포인트들
            touchpoints = touchpoint_data[
                touchpoint_data['conversion_id'] == conversion_id
            ].sort_values('timestamp')
            
            if len(touchpoints) == 0:
                continue
            
            # 전환 시점부터의 경과 일수 계산
            conversion_time = conversion_data[
                conversion_data['conversion_id'] == conversion_id
            ]['conversion_time'].iloc[0]
            
            touchpoints['days_since'] = (
                conversion_time - touchpoints['timestamp']
            ).dt.days
            
            # 각 감쇠 모델 적용
            decay_models = {
                'linear': linear_decay,
                'exponential': exponential_decay,
                'u_shaped': u_shaped_decay
            }
            
            for model_name, decay_func in decay_models.items():
                weights = touchpoints['days_since'].apply(decay_func)
                normalized_weights = weights / weights.sum()
                
                if conversion_id not in attribution_weights:
                    attribution_weights[conversion_id] = {}
                
                attribution_weights[conversion_id][model_name] = dict(
                    zip(touchpoints['touchpoint_id'], normalized_weights)
                )
        
        # 채널별 총 기여도 집계
        channel_attribution = self._aggregate_channel_attribution(
            attribution_weights, touchpoint_data
        )
        
        # 모델 성능 비교
        model_performance = self._compare_attribution_models(
            channel_attribution, conversion_data
        )
        
        return {
            'attribution_weights': attribution_weights,
            'channel_attribution': channel_attribution,
            'model_performance': model_performance,
            'recommended_model': max(model_performance.items(), key=lambda x: x[1]['auc'])[0]
        }
    
    def advertising_wearout_analysis(self, creative_data, performance_data):
        """광고 마모 분석"""
        
        # 광고별 성과 추이 분석
        wearout_patterns = {}
        
        for creative_id in creative_data['creative_id'].unique():
            # 해당 광고의 시계열 성과 데이터
            creative_performance = performance_data[
                performance_data['creative_id'] == creative_id
            ].sort_values('date')
            
            if len(creative_performance) < 10:  # 최소 데이터 포인트
                continue
            
            # 성과 지표별 마모 패턴 분석
            metrics = ['ctr', 'conversion_rate', 'cpm']
            
            for metric in metrics:
                if metric not in creative_performance.columns:
                    continue
                
                # 트렌드 분석
                x = np.arange(len(creative_performance))
                y = creative_performance[metric].values
                
                # 선형 회귀로 전반적 트렌드 파악
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                
                # 변곡점 탐지 (성과 급락 시점)
                change_points = self._detect_change_points(y)
                
                # 마모율 계산
                wearout_rate = -slope if slope < 0 else 0
                
                wearout_patterns[creative_id] = {
                    'metric': metric,
                    'slope': slope,
                    'r_squared': r_value**2,
                    'p_value': p_value,
                    'wearout_rate': wearout_rate,
                    'change_points': change_points,
                    'days_to_wearout': self._estimate_days_to_wearout(slope, y),
                    'performance_data': creative_performance
                }
        
        # 광고 교체 권고사항
        replacement_recommendations = self._generate_replacement_recommendations(wearout_patterns)
        
        # 마모 패턴 시각화
        self._visualize_wearout_patterns(wearout_patterns)
        
        return {
            'wearout_patterns': wearout_patterns,
            'replacement_recommendations': replacement_recommendations,
            'average_wearout_days': np.mean([
                p['days_to_wearout'] for p in wearout_patterns.values() 
                if p['days_to_wearout'] is not None
            ])
        }

# 보조 메서드들
    def _optimize_convoluted_adstock(self, media_series, sales_series, max_lag):
        """합성곱 Adstock 최적화"""
        best_params = None
        best_r2 = -np.inf
        
        # 베이지안 최적화 또는 격자 탐색으로 최적 감쇠 패턴 찾기
        for _ in range(50):  # 랜덤 서치
            decay_params = np.random.exponential(0.5, max_lag)
            decay_params = decay_params / decay_params.sum()  # 정규화
            
            # Adstock 적용
            adstock_series = np.zeros(len(media_series))
            for i in range(len(media_series)):
                for lag in range(min(i+1, len(decay_params))):
                    adstock_series[i] += media_series.iloc[i-lag] * decay_params[lag]
            
            # 성과 예측
            X = adstock_series.reshape(-1, 1)
            y = sales_series.values
            
            model = LinearRegression()
            model.fit(X, y)
            r2 = model.score(X, y)
            
            if r2 > best_r2:
                best_r2 = r2
                best_params = decay_params
        
        return best_params
    
    def _calculate_optimal_spend_points(self, saturation_models):
        """최적 지출 포인트 계산"""
        optimal_points = {}
        
        for channel, model in saturation_models.items():
            if model is None:
                continue
            
            func = model['function']
            params = model['parameters']
            
            # 한계 효율성이 특정 임계값 이하로 떨어지는 지점 찾기
            spend_range = np.linspace(0, 1000000, 10000)
            responses = func(spend_range, *params)
            
            # 1차 미분 (한계 효율성)
            marginal_efficiency = np.gradient(responses, spend_range)
            
            # 한계 효율성이 초기값의 50% 이하로 떨어지는 지점
            threshold = marginal_efficiency[1] * 0.5
            optimal_idx = np.where(marginal_efficiency < threshold)[0]
            
            if len(optimal_idx) > 0:
                optimal_points[channel] = {
                    'optimal_spend': spend_range[optimal_idx[0]],
                    'expected_response': responses[optimal_idx[0]],
                    'marginal_efficiency': marginal_efficiency[optimal_idx[0]]
                }
        
        return optimal_points
    
    def _visualize_adstock_effects(self, adstock_results):
        """Adstock 효과 시각화"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.ravel()
        
        for i, (channel, result) in enumerate(adstock_results.items()):
            if i >= 4:  # 최대 4개 채널만 표시
                break
            
            # 원본 vs Adstock 적용 데이터
            axes[i].plot(result['adstock_series'].index, 
                        result['adstock_series'].values, 
                        label='With Adstock', alpha=0.7)
            axes[i].set_title(f'{channel} - Decay Rate: {result["decay_rate"]:.2f}')
            axes[i].set_xlabel('Time Period')
            axes[i].set_ylabel('Media Effect')
            axes[i].legend()
        
        plt.tight_layout()
        return fig

# 실습 예제: 종합 광고 효과 측정
def comprehensive_advertising_measurement():
    """종합적인 광고 효과 측정 분석"""
    
    # 샘플 데이터 생성
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=365, freq='D')
    
    # 미디어 지출 데이터
    media_spend = pd.DataFrame({
        'TV': np.random.uniform(10000, 50000, 365),
        'Digital': np.random.uniform(5000, 30000, 365),
        'Radio': np.random.uniform(2000, 15000, 365),
        'Print': np.random.uniform(1000, 10000, 365)
    }, index=dates)
    
    # 매출 데이터 (미디어 효과 + 노이즈)
    base_sales = 100000
    media_effect = (
        media_spend['TV'] * 0.3 + 
        media_spend['Digital'] * 0.5 + 
        media_spend['Radio'] * 0.2 + 
        media_spend['Print'] * 0.1
    )
    
    sales_data = pd.Series(
        base_sales + media_effect + np.random.normal(0, 5000, 365),
        index=dates
    )
    
    # 브랜드 리프트 테스트 데이터
    pre_metrics = pd.DataFrame({
        'group': ['exposed'] * 500 + ['control'] * 500,
        'brand_awareness': np.concatenate([
            np.random.normal(0.3, 0.1, 500),  # 노출 그룹
            np.random.normal(0.25, 0.1, 500)  # 대조 그룹
        ]),
        'purchase_intent': np.concatenate([
            np.random.normal(0.2, 0.08, 500),
            np.random.normal(0.18, 0.08, 500)
        ])
    })
    
    post_metrics = pd.DataFrame({
        'group': ['exposed'] * 500 + ['control'] * 500,
        'brand_awareness': np.concatenate([
            np.random.normal(0.45, 0.12, 500),  # 리프트 적용
            np.random.normal(0.27, 0.1, 500)
        ]),
        'purchase_intent': np.concatenate([
            np.random.normal(0.32, 0.1, 500),
            np.random.normal(0.19, 0.08, 500)
        ])
    })
    
    # 측정 시스템 초기화
    measurement_system = AdvertisingMeasurementSystem()
    
    # 1. Adstock 모델링
    adstock_results = measurement_system.adstock_modeling(media_spend, sales_data)
    
    # 2. 포화 곡선 모델링
    saturation_results = measurement_system.saturation_curve_modeling(
        media_spend, sales_data
    )
    
    # 3. 브랜드 리프트 측정
    brand_lift_results = measurement_system.brand_lift_measurement(
        pre_metrics[pre_metrics['group'] == 'exposed'],
        pre_metrics[pre_metrics['group'] == 'control'],
        pre_metrics,
        post_metrics
    )
    
    # 결과 출력
    print("=== 광고 효과 측정 결과 ===")
    print("Adstock 파라미터:")
    for channel, params in adstock_results['geometric_adstock'].items():
        print(f"  {channel}: {params['decay_rate']:.3f} (R² = {params['r2_score']:.3f})")
    
    print("\n브랜드 리프트:")
    for metric, lift in brand_lift_results['lift_metrics'].items():
        print(f"  {metric}: {lift['lift_percentage']:.1f}% ({lift['significance']})")
    
    # 시각화
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Adstock 효과 예시 (첫 번째 채널)
    first_channel = list(adstock_results['geometric_adstock'].keys())[0]
    adstock_data = adstock_results['geometric_adstock'][first_channel]['adstock_series']
    
    axes[0, 0].plot(media_spend.index, media_spend[first_channel], 
                   label='Original Spend', alpha=0.7)
    axes[0, 0].plot(media_spend.index, adstock_data, 
                   label='With Adstock', alpha=0.7)
    axes[0, 0].set_title(f'{first_channel} - Adstock Effect')
    axes[0, 0].legend()
    
    # 포화 곡선 예시
    if first_channel in saturation_results['saturation_models']:
        model = saturation_results['saturation_models'][first_channel]
        if model:
            x_range = np.linspace(0, media_spend[first_channel].max(), 100)
            y_pred = model['function'](x_range, *model['parameters'])
            
            axes[0, 1].scatter(media_spend[first_channel], sales_data, alpha=0.5)
            axes[0, 1].plot(x_range, y_pred, 'r-', label=f'{model["name"]} fit')
            axes[0, 1].set_xlabel(f'{first_channel} Spend')
            axes[0, 1].set_ylabel('Sales')
            axes[0, 1].set_title('Saturation Curve')
            axes[0, 1].legend()
    
    # 브랜드 리프트 시각화
    metrics = ['brand_awareness', 'purchase_intent']
    x_pos = np.arange(len(metrics))
    
    pre_exposed = [pre_metrics[pre_metrics['group'] == 'exposed'][m].mean() for m in metrics]
    post_exposed = [post_metrics[post_metrics['group'] == 'exposed'][m].mean() for m in metrics]
    pre_control = [pre_metrics[pre_metrics['group'] == 'control'][m].mean() for m in metrics]
    post_control = [post_metrics[post_metrics['group'] == 'control'][m].mean() for m in metrics]
    
    width = 0.2
    axes[1, 0].bar(x_pos - width*1.5, pre_exposed, width, label='Pre-Exposed', alpha=0.7)
    axes[1, 0].bar(x_pos - width*0.5, post_exposed, width, label='Post-Exposed', alpha=0.7)
    axes[1, 0].bar(x_pos + width*0.5, pre_control, width, label='Pre-Control', alpha=0.7)
    axes[1, 0].bar(x_pos + width*1.5, post_control, width, label='Post-Control', alpha=0.7)
    
    axes[1, 0].set_xlabel('Metrics')
    axes[1, 0].set_ylabel('Score')
    axes[1, 0].set_title('Brand Lift Analysis')
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels(metrics)
    axes[1, 0].legend()
    
    # 매출 vs 예측 비교
    # 간단한 Adstock 적용 후 예측
    adstock_media = pd.DataFrame()
    for channel in media_spend.columns:
        decay_rate = adstock_results['geometric_adstock'][channel]['decay_rate']
        adstock_series = media_spend[channel].copy()
        for i in range(1, len(adstock_series)):
            adstock_series.iloc[i] += adstock_series.iloc[i-1] * decay_rate
        adstock_media[channel] = adstock_series
    
    # 간단한 선형 모델로 예측
    X = adstock_media.values
    y = sales_data.values
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    
    axes[1, 1].scatter(sales_data, y_pred, alpha=0.5)
    axes[1, 1].plot([sales_data.min(), sales_data.max()], 
                   [sales_data.min(), sales_data.max()], 'r--')
    axes[1, 1].set_xlabel('Actual Sales')
    axes[1, 1].set_ylabel('Predicted Sales')
    axes[1, 1].set_title(f'Model Performance (R² = {model.score(X, y):.3f})')
    
    plt.tight_layout()
    plt.show()
    
    return {
        'adstock_results': adstock_results,
        'saturation_results': saturation_results,
        'brand_lift_results': brand_lift_results,
        'model_performance': model.score(X, y)
    }

# 메인 실행
if __name__ == "__main__":
    print("=== 광고 측정 이론 실습 ===")
    print("Adstock 모델링과 브랜드 리프트 측정")
    
    results = comprehensive_advertising_measurement()
    
    print(f"\n측정 완료:")
    print(f"- 모델 성능 (R²): {results['model_performance']:.3f}")
    print(f"- 브랜드 건강도: {results['brand_lift_results']['brand_health_score']:.3f}")
```

## 🚀 프로젝트
1. **MMM 자동화 플랫폼** - Adstock과 포화곡선 자동 최적화
2. **브랜드 리프트 측정 도구** - 실시간 A/B 테스트 분석
3. **증분 효과 대시보드** - 인과 추론 기반 ROI 측정
4. **광고 마모 예측 시스템** - 크리에이티브 교체 시점 알림