# 15. Statistics Fundamentals - 통계학 기초

## 📚 과정 소개
광고 성과 분석과 실험 설계에 필요한 핵심 통계학 개념을 마스터합니다. A/B 테스트, 신뢰구간, 가설검정, 베이지안 통계를 광고 도메인에 적용합니다.

## 🎯 학습 목표
- 광고 데이터 기술통계 분석
- A/B 테스트 설계 및 해석
- 통계적 추론과 의사결정
- 베이지안 광고 최적화

## 📖 주요 내용

### 광고 데이터 기술통계
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class AdStatisticsAnalyzer:
    """광고 통계 분석기"""
    
    def __init__(self):
        self.confidence_level = 0.95
        
    def descriptive_analysis(self, data: pd.DataFrame, metric: str) -> Dict:
        """기술통계 분석"""
        series = data[metric].dropna()
        
        # 기본 통계량
        basic_stats = {
            'count': len(series),
            'mean': series.mean(),
            'median': series.median(),
            'mode': series.mode().iloc[0] if not series.mode().empty else None,
            'std': series.std(),
            'variance': series.var(),
            'min': series.min(),
            'max': series.max(),
            'range': series.max() - series.min()
        }
        
        # 분위수
        quantiles = {
            'q25': series.quantile(0.25),
            'q50': series.quantile(0.50),  # median
            'q75': series.quantile(0.75),
            'iqr': series.quantile(0.75) - series.quantile(0.25)
        }
        
        # 분포 특성
        distribution_stats = {
            'skewness': stats.skew(series),
            'kurtosis': stats.kurtosis(series),
            'cv': series.std() / series.mean() if series.mean() != 0 else np.inf
        }
        
        # 이상치 탐지
        q1, q3 = quantiles['q25'], quantiles['q75']
        iqr = quantiles['iqr']
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        
        outlier_info = {
            'outlier_count': len(outliers),
            'outlier_percentage': len(outliers) / len(series) * 100,
            'outlier_values': outliers.tolist()[:10]  # 상위 10개만
        }
        
        return {
            'basic_stats': basic_stats,
            'quantiles': quantiles,
            'distribution': distribution_stats,
            'outliers': outlier_info,
            'normality_test': self._test_normality(series)
        }
    
    def _test_normality(self, series: pd.Series) -> Dict:
        """정규성 검정"""
        # Shapiro-Wilk test (n < 5000)
        if len(series) < 5000:
            shapiro_stat, shapiro_p = stats.shapiro(series)
            shapiro_result = {
                'statistic': shapiro_stat,
                'p_value': shapiro_p,
                'is_normal': shapiro_p > 0.05
            }
        else:
            shapiro_result = {'message': 'Sample too large for Shapiro-Wilk test'}
        
        # Kolmogorov-Smirnov test
        ks_stat, ks_p = stats.kstest(series, 'norm', 
                                     args=(series.mean(), series.std()))
        ks_result = {
            'statistic': ks_stat,
            'p_value': ks_p,
            'is_normal': ks_p > 0.05
        }
        
        return {
            'shapiro_wilk': shapiro_result,
            'kolmogorov_smirnov': ks_result
        }
    
    def compare_campaigns(self, data: pd.DataFrame, 
                         campaign_col: str, metric_col: str) -> Dict:
        """캠페인 간 비교 분석"""
        campaigns = data[campaign_col].unique()
        comparison_results = {}
        
        # 각 캠페인별 기술통계
        for campaign in campaigns:
            campaign_data = data[data[campaign_col] == campaign][metric_col]
            comparison_results[campaign] = self.descriptive_analysis(
                pd.DataFrame({metric_col: campaign_data}), metric_col
            )
        
        # 전체 ANOVA 테스트
        campaign_groups = [data[data[campaign_col] == camp][metric_col].dropna() 
                          for camp in campaigns]
        
        if len(campaign_groups) > 2:
            f_stat, p_value = stats.f_oneway(*campaign_groups)
            anova_result = {
                'f_statistic': f_stat,
                'p_value': p_value,
                'significant_difference': p_value < 0.05
            }
        else:
            anova_result = {'message': 'ANOVA requires at least 3 groups'}
        
        return {
            'campaign_stats': comparison_results,
            'anova_test': anova_result,
            'recommendations': self._generate_campaign_recommendations(comparison_results)
        }
    
    def _generate_campaign_recommendations(self, campaign_stats: Dict) -> List[str]:
        """캠페인 추천사항 생성"""
        recommendations = []
        
        # 성과가 가장 좋은 캠페인 찾기
        best_campaign = max(campaign_stats.keys(), 
                           key=lambda x: campaign_stats[x]['basic_stats']['mean'])
        worst_campaign = min(campaign_stats.keys(), 
                            key=lambda x: campaign_stats[x]['basic_stats']['mean'])
        
        recommendations.append(f"'{best_campaign}' 캠페인이 가장 높은 평균 성과를 보임")
        recommendations.append(f"'{worst_campaign}' 캠페인 최적화 필요")
        
        # 변동성 분석
        most_stable = min(campaign_stats.keys(), 
                         key=lambda x: campaign_stats[x]['distribution']['cv'])
        recommendations.append(f"'{most_stable}' 캠페인이 가장 안정적인 성과를 보임")
        
        return recommendations

class ABTestAnalyzer:
    """A/B 테스트 분석기"""
    
    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
        self.confidence_level = 1 - alpha
        
    def design_ab_test(self, baseline_rate: float, 
                      min_detectable_effect: float,
                      power: float = 0.8) -> Dict:
        """A/B 테스트 설계"""
        from statsmodels.stats.power import ttest_power
        from statsmodels.stats.proportion import proportion_effectsize
        
        # 효과 크기 계산
        control_rate = baseline_rate
        treatment_rate = baseline_rate * (1 + min_detectable_effect)
        
        effect_size = proportion_effectsize(treatment_rate, control_rate)
        
        # 표본 크기 계산
        from statsmodels.stats.power import tt_solve_power
        
        sample_size = tt_solve_power(
            effect_size=effect_size,
            power=power,
            alpha=self.alpha,
            alternative='two-sided'
        )
        
        # 실행 기간 추정 (일일 방문자 기준)
        def estimate_duration(daily_visitors: int) -> int:
            total_sample_needed = sample_size * 2  # 두 그룹
            return int(np.ceil(total_sample_needed / daily_visitors))
        
        return {
            'sample_size_per_group': int(np.ceil(sample_size)),
            'total_sample_size': int(np.ceil(sample_size * 2)),
            'effect_size': effect_size,
            'baseline_rate': control_rate,
            'target_rate': treatment_rate,
            'min_detectable_effect': min_detectable_effect,
            'power': power,
            'alpha': self.alpha,
            'duration_estimator': estimate_duration
        }
    
    def analyze_ab_test(self, control_data: Dict, 
                       treatment_data: Dict) -> Dict:
        """A/B 테스트 결과 분석"""
        # 데이터 추출
        control_conversions = control_data['conversions']
        control_visitors = control_data['visitors']
        treatment_conversions = treatment_data['conversions']
        treatment_visitors = treatment_data['visitors']
        
        # 전환율 계산
        control_rate = control_conversions / control_visitors
        treatment_rate = treatment_conversions / treatment_visitors
        
        # 통계적 검정
        test_result = self._proportion_test(
            control_conversions, control_visitors,
            treatment_conversions, treatment_visitors
        )
        
        # 신뢰구간
        control_ci = self._proportion_confidence_interval(control_conversions, control_visitors)
        treatment_ci = self._proportion_confidence_interval(treatment_conversions, treatment_visitors)
        
        # 효과 크기 및 실용적 유의성
        relative_lift = (treatment_rate - control_rate) / control_rate
        absolute_lift = treatment_rate - control_rate
        
        # 베이지안 분석
        bayesian_result = self._bayesian_ab_analysis(
            control_conversions, control_visitors,
            treatment_conversions, treatment_visitors
        )
        
        return {
            'control': {
                'visitors': control_visitors,
                'conversions': control_conversions,
                'rate': control_rate,
                'confidence_interval': control_ci
            },
            'treatment': {
                'visitors': treatment_visitors,
                'conversions': treatment_conversions,
                'rate': treatment_rate,
                'confidence_interval': treatment_ci
            },
            'test_results': test_result,
            'effect_size': {
                'absolute_lift': absolute_lift,
                'relative_lift': relative_lift,
                'lift_confidence_interval': self._lift_confidence_interval(
                    control_conversions, control_visitors,
                    treatment_conversions, treatment_visitors
                )
            },
            'bayesian_analysis': bayesian_result,
            'recommendation': self._generate_ab_recommendation(test_result, relative_lift)
        }
    
    def _proportion_test(self, x1: int, n1: int, x2: int, n2: int) -> Dict:
        """비율 검정"""
        from statsmodels.stats.proportion import proportions_ztest
        
        counts = np.array([x1, x2])
        nobs = np.array([n1, n2])
        
        z_stat, p_value = proportions_ztest(counts, nobs)
        
        return {
            'z_statistic': z_stat,
            'p_value': p_value,
            'is_significant': p_value < self.alpha,
            'confidence_level': self.confidence_level
        }
    
    def _proportion_confidence_interval(self, x: int, n: int) -> Tuple[float, float]:
        """비율 신뢰구간"""
        from statsmodels.stats.proportion import proportion_confint
        
        ci_lower, ci_upper = proportion_confint(x, n, alpha=self.alpha)
        return (ci_lower, ci_upper)
    
    def _lift_confidence_interval(self, x1: int, n1: int, x2: int, n2: int) -> Tuple[float, float]:
        """리프트 신뢰구간"""
        p1 = x1 / n1
        p2 = x2 / n2
        
        # 델타 방법 사용
        se_p1 = np.sqrt(p1 * (1 - p1) / n1)
        se_p2 = np.sqrt(p2 * (1 - p2) / n2)
        se_diff = np.sqrt(se_p1**2 + se_p2**2)
        
        diff = p2 - p1
        relative_lift = diff / p1 if p1 > 0 else 0
        
        # 근사 신뢰구간
        z_critical = stats.norm.ppf(1 - self.alpha/2)
        margin_error = z_critical * se_diff / p1 if p1 > 0 else 0
        
        return (relative_lift - margin_error, relative_lift + margin_error)
    
    def _bayesian_ab_analysis(self, x1: int, n1: int, x2: int, n2: int) -> Dict:
        """베이지안 A/B 테스트 분석"""
        # 베타 분포 사용 (베타-이항 켤레 사전분포)
        # 균등 사전분포: Beta(1, 1)
        
        # 사후분포: Beta(1 + x, 1 + n - x)
        control_posterior = stats.beta(1 + x1, 1 + n1 - x1)
        treatment_posterior = stats.beta(1 + x2, 1 + n2 - x2)
        
        # 몬테카를로 시뮬레이션
        n_samples = 100000
        control_samples = control_posterior.rvs(n_samples)
        treatment_samples = treatment_posterior.rvs(n_samples)
        
        # Treatment가 Control보다 좋을 확률
        prob_treatment_better = np.mean(treatment_samples > control_samples)
        
        # 리프트 분포
        lift_samples = (treatment_samples - control_samples) / control_samples
        lift_mean = np.mean(lift_samples)
        lift_credible_interval = np.percentile(lift_samples, [2.5, 97.5])
        
        return {
            'prob_treatment_better': prob_treatment_better,
            'prob_control_better': 1 - prob_treatment_better,
            'expected_lift': lift_mean,
            'lift_credible_interval': lift_credible_interval,
            'control_posterior_mean': control_posterior.mean(),
            'treatment_posterior_mean': treatment_posterior.mean()
        }
    
    def _generate_ab_recommendation(self, test_result: Dict, relative_lift: float) -> str:
        """A/B 테스트 추천사항"""
        if test_result['is_significant']:
            if relative_lift > 0:
                return f"Treatment 버전이 통계적으로 유의하게 더 좋음 (p={test_result['p_value']:.4f}). 적용 권장."
            else:
                return f"Control 버전이 통계적으로 유의하게 더 좋음 (p={test_result['p_value']:.4f}). Treatment 중단 권장."
        else:
            return f"통계적으로 유의한 차이 없음 (p={test_result['p_value']:.4f}). 더 많은 데이터 수집 또는 테스트 개선 필요."

class BayesianOptimization:
    """베이지안 광고 최적화"""
    
    def __init__(self):
        self.prior_params = {'alpha': 1, 'beta': 1}  # 베타 분포 사전분포
        
    def multi_armed_bandit_analysis(self, arm_data: Dict[str, Dict]) -> Dict:
        """다중 선택지 밴딧 분석"""
        results = {}
        
        for arm_name, data in arm_data.items():
            successes = data['conversions']
            trials = data['impressions']
            failures = trials - successes
            
            # 베타 분포 사후분포
            posterior_alpha = self.prior_params['alpha'] + successes
            posterior_beta = self.prior_params['beta'] + failures
            
            posterior = stats.beta(posterior_alpha, posterior_beta)
            
            results[arm_name] = {
                'posterior_mean': posterior.mean(),
                'posterior_std': posterior.std(),
                'credible_interval_95': posterior.interval(0.95),
                'probability_best': 0  # 나중에 계산
            }
        
        # 각 arm이 최고일 확률 계산
        n_samples = 100000
        samples = {}
        for arm in arm_data.keys():
            alpha = self.prior_params['alpha'] + arm_data[arm]['conversions']
            beta = self.prior_params['beta'] + (arm_data[arm]['impressions'] - arm_data[arm]['conversions'])
            samples[arm] = stats.beta(alpha, beta).rvs(n_samples)
        
        sample_df = pd.DataFrame(samples)
        for arm in arm_data.keys():
            results[arm]['probability_best'] = np.mean(
                sample_df[arm] == sample_df.max(axis=1)
            )
        
        # 추천사항
        best_arm = max(results.keys(), key=lambda x: results[x]['probability_best'])
        
        return {
            'arm_analysis': results,
            'recommended_arm': best_arm,
            'recommendation_confidence': results[best_arm]['probability_best'],
            'expected_regret': self._calculate_expected_regret(results)
        }
    
    def _calculate_expected_regret(self, results: Dict) -> float:
        """예상 후회 계산"""
        best_mean = max(arm['posterior_mean'] for arm in results.values())
        current_strategy_mean = np.mean([arm['posterior_mean'] for arm in results.values()])
        return best_mean - current_strategy_mean

class CausalInference:
    """인과추론 분석"""
    
    def __init__(self):
        pass
    
    def difference_in_differences(self, data: pd.DataFrame,
                                time_col: str, treatment_col: str,
                                outcome_col: str, pre_period: str) -> Dict:
        """이중차분법 분석"""
        # 전후 기간 구분
        data['post_treatment'] = (data[time_col] >= pre_period).astype(int)
        
        # 회귀분석
        from sklearn.linear_model import LinearRegression
        
        X = data[[treatment_col, 'post_treatment']].copy()
        X['interaction'] = X[treatment_col] * X['post_treatment']
        
        model = LinearRegression()
        model.fit(X, data[outcome_col])
        
        # 계수 해석
        treatment_effect = model.coef_[2]  # 상호작용 항
        
        return {
            'did_estimate': treatment_effect,
            'coefficients': {
                'treatment': model.coef_[0],
                'post_period': model.coef_[1],
                'did_effect': model.coef_[2]
            },
            'r_squared': model.score(X, data[outcome_col])
        }
    
    def instrumental_variables(self, data: pd.DataFrame,
                             treatment_col: str, instrument_col: str,
                             outcome_col: str, controls: List[str] = None) -> Dict:
        """도구변수 분석"""
        from sklearn.linear_model import LinearRegression
        
        # 1단계: 도구변수로 처치변수 예측
        X_first = data[[instrument_col]]
        if controls:
            X_first = pd.concat([X_first, data[controls]], axis=1)
        
        first_stage = LinearRegression()
        first_stage.fit(X_first, data[treatment_col])
        treatment_hat = first_stage.predict(X_first)
        
        # 2단계: 예측된 처치변수로 결과변수 예측
        X_second = pd.DataFrame({'treatment_hat': treatment_hat})
        if controls:
            X_second = pd.concat([X_second, data[controls]], axis=1)
        
        second_stage = LinearRegression()
        second_stage.fit(X_second, data[outcome_col])
        
        return {
            'iv_estimate': second_stage.coef_[0],
            'first_stage_r2': first_stage.score(X_first, data[treatment_col]),
            'second_stage_r2': second_stage.score(X_second, data[outcome_col])
        }
```

## 🚀 프로젝트
1. **A/B 테스트 자동화 플랫폼**
2. **베이지안 광고 최적화 시스템**
3. **통계적 광고 성과 대시보드**
4. **인과추론 기반 캠페인 효과 분석**