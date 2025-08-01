# 30. A/B Testing - A/B 테스트

## 📚 과정 소개
과학적 광고 최적화를 위한 A/B 테스트 설계, 실행, 분석을 마스터합니다. 베이지안 A/B 테스트, 다변량 테스트, 순차적 테스트까지 포괄적으로 다룹니다.

## 🎯 학습 목표
- 과학적 실험 설계 방법론
- 통계적 유의성과 실용적 유의성
- 베이지안 A/B 테스트 구현
- 실시간 실험 모니터링 시스템

## 📖 주요 내용

### 실험 설계 프레임워크
```python
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib

@dataclass
class ExperimentConfig:
    """실험 설정 클래스"""
    name: str
    hypothesis: str
    primary_metric: str
    secondary_metrics: List[str]
    minimum_detectable_effect: float
    baseline_conversion_rate: float
    alpha: float = 0.05
    power: float = 0.80
    one_sided: bool = False
    
class ExperimentDesigner:
    """실험 설계자"""
    
    def __init__(self):
        self.experiment_registry = {}
        
    def design_experiment(self, config: ExperimentConfig) -> Dict:
        """실험 설계"""
        # 표본 크기 계산
        sample_size = self._calculate_sample_size(
            baseline_rate=config.baseline_conversion_rate,
            mde=config.minimum_detectable_effect,
            alpha=config.alpha,
            power=config.power,
            one_sided=config.one_sided
        )
        
        # 실험 기간 추정
        duration_info = self._estimate_duration(sample_size)
        
        # 무작위 배정 전략
        randomization_config = self._setup_randomization()
        
        # 실험 설정
        experiment_design = {
            'config': config,
            'sample_size_per_variant': sample_size,
            'total_sample_size': sample_size * 2,
            'duration_estimates': duration_info,
            'randomization': randomization_config,
            'success_criteria': self._define_success_criteria(config),
            'monitoring_plan': self._create_monitoring_plan(config),
            'statistical_plan': self._create_statistical_plan(config)
        }
        
        # 실험 등록
        self.experiment_registry[config.name] = experiment_design
        
        return experiment_design
    
    def _calculate_sample_size(self, baseline_rate: float, mde: float,
                              alpha: float, power: float, one_sided: bool) -> int:
        """표본 크기 계산"""
        from statsmodels.stats.power import tt_solve_power
        from statsmodels.stats.proportion import proportion_effectsize
        
        # 효과 크기 계산
        treatment_rate = baseline_rate * (1 + mde)
        effect_size = proportion_effectsize(treatment_rate, baseline_rate)
        
        # 단측/양측 검정 조정
        alpha_adjusted = alpha if one_sided else alpha / 2
        
        # 표본 크기 계산
        n = tt_solve_power(
            effect_size=effect_size,
            power=power,
            alpha=alpha_adjusted,
            alternative='larger' if one_sided else 'two-sided'
        )
        
        return int(np.ceil(n))
    
    def _estimate_duration(self, sample_size: int) -> Dict:
        """실험 기간 추정"""
        return {
            'sample_size_per_variant': sample_size,
            'total_needed': sample_size * 2,
            'duration_calculator': lambda daily_traffic: max(1, int(np.ceil(sample_size * 2 / daily_traffic))),
            'recommendations': {
                'min_duration_days': 7,  # 최소 1주일
                'max_duration_days': 30,  # 최대 1개월
                'weekday_effect_consideration': True
            }
        }
    
    def _setup_randomization(self) -> Dict:
        """무작위 배정 설정"""
        return {
            'method': 'hash_based',
            'traffic_split': 0.5,
            'hash_function': 'md5',
            'salt': f"experiment_{datetime.now().strftime('%Y%m%d')}",
            'consistency_check': True
        }
    
    def _define_success_criteria(self, config: ExperimentConfig) -> Dict:
        """성공 기준 정의"""
        return {
            'primary_metric': {
                'metric': config.primary_metric,
                'minimum_lift': config.minimum_detectable_effect,
                'significance_level': config.alpha,
                'decision_threshold': 'statistical_significance'
            },
            'secondary_metrics': [
                {
                    'metric': metric,
                    'monitoring_purpose': 'guardrail',
                    'alert_threshold': 0.05  # 5% 하락 시 경고
                }
                for metric in config.secondary_metrics
            ],
            'business_criteria': {
                'min_practical_significance': config.minimum_detectable_effect * 0.5,
                'cost_benefit_threshold': 1.2  # 최소 20% ROI
            }
        }

class ABTestRunner:
    """A/B 테스트 실행기"""
    
    def __init__(self):
        self.active_experiments = {}
        self.experiment_data = {}
        
    def start_experiment(self, experiment_design: Dict, 
                        traffic_allocation: float = 1.0) -> str:
        """실험 시작"""
        experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        experiment_runtime = {
            'id': experiment_id,
            'design': experiment_design,
            'start_time': datetime.now(),
            'traffic_allocation': traffic_allocation,
            'status': 'running',
            'participants': {'control': [], 'treatment': []},
            'metrics_data': {'control': {}, 'treatment': {}}
        }
        
        self.active_experiments[experiment_id] = experiment_runtime
        self.experiment_data[experiment_id] = pd.DataFrame()
        
        return experiment_id
    
    def assign_variant(self, experiment_id: str, user_id: str) -> str:
        """사용자 변형 배정"""
        if experiment_id not in self.active_experiments:
            return 'control'  # 기본값
        
        experiment = self.active_experiments[experiment_id]
        
        # 해시 기반 일관된 배정
        hash_input = f"{user_id}_{experiment['design']['randomization']['salt']}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # 0-1 사이 값으로 변환
        assignment_score = (hash_value % 10000) / 10000
        
        # 트래픽 할당 고려
        if assignment_score > experiment['traffic_allocation']:
            return 'control'  # 실험 대상 외
        
        # 변형 배정
        split_point = experiment['design']['randomization']['traffic_split']
        variant = 'treatment' if assignment_score < split_point else 'control'
        
        # 참가자 기록
        experiment['participants'][variant].append({
            'user_id': user_id,
            'assigned_at': datetime.now(),
            'assignment_score': assignment_score
        })
        
        return variant
    
    def record_event(self, experiment_id: str, user_id: str, 
                    event_type: str, value: float = 1.0, 
                    metadata: Dict = None) -> None:
        """이벤트 기록"""
        if experiment_id not in self.active_experiments:
            return
        
        # 사용자 변형 확인
        variant = self._get_user_variant(experiment_id, user_id)
        if not variant:
            return
        
        # 이벤트 데이터 구성
        event_data = {
            'experiment_id': experiment_id,
            'user_id': user_id,
            'variant': variant,
            'event_type': event_type,
            'value': value,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        }
        
        # 데이터 저장
        new_row = pd.DataFrame([event_data])
        self.experiment_data[experiment_id] = pd.concat([
            self.experiment_data[experiment_id], new_row
        ], ignore_index=True)
    
    def _get_user_variant(self, experiment_id: str, user_id: str) -> Optional[str]:
        """사용자 변형 조회"""
        experiment = self.active_experiments[experiment_id]
        
        for variant in ['control', 'treatment']:
            for participant in experiment['participants'][variant]:
                if participant['user_id'] == user_id:
                    return variant
        
        return None

class BayesianABTest:
    """베이지안 A/B 테스트"""
    
    def __init__(self, prior_alpha: float = 1, prior_beta: float = 1):
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        
    def analyze_experiment(self, control_conversions: int, control_visitors: int,
                          treatment_conversions: int, treatment_visitors: int,
                          credible_interval: float = 0.95) -> Dict:
        """베이지안 분석"""
        # 사후분포 계산
        control_posterior = self._calculate_posterior(control_conversions, 
                                                    control_visitors - control_conversions)
        treatment_posterior = self._calculate_posterior(treatment_conversions,
                                                       treatment_visitors - treatment_conversions)
        
        # 몬테카를로 시뮬레이션
        n_samples = 100000
        control_samples = control_posterior.rvs(n_samples)
        treatment_samples = treatment_posterior.rvs(n_samples)
        
        # 확률 계산
        prob_treatment_better = np.mean(treatment_samples > control_samples)
        
        # 리프트 분석
        lift_samples = (treatment_samples - control_samples) / control_samples
        lift_mean = np.mean(lift_samples)
        lift_credible_interval = np.percentile(lift_samples, 
                                             [50 * (1 - credible_interval), 
                                              50 * (1 + credible_interval)])
        
        # 기대 손실 계산
        expected_loss_control = np.mean(np.maximum(0, treatment_samples - control_samples))
        expected_loss_treatment = np.mean(np.maximum(0, control_samples - treatment_samples))
        
        return {
            'control': {
                'conversions': control_conversions,
                'visitors': control_visitors,
                'rate': control_conversions / control_visitors,
                'posterior_mean': control_posterior.mean(),
                'credible_interval': control_posterior.interval(credible_interval)
            },
            'treatment': {
                'conversions': treatment_conversions,
                'visitors': treatment_visitors, 
                'rate': treatment_conversions / treatment_visitors,
                'posterior_mean': treatment_posterior.mean(),
                'credible_interval': treatment_posterior.interval(credible_interval)
            },
            'probability_treatment_better': prob_treatment_better,
            'probability_control_better': 1 - prob_treatment_better,
            'expected_lift': lift_mean,
            'lift_credible_interval': lift_credible_interval,
            'expected_loss': {
                'control': expected_loss_control,
                'treatment': expected_loss_treatment
            },
            'decision_recommendation': self._make_bayesian_decision(
                prob_treatment_better, expected_loss_control, expected_loss_treatment
            )
        }
    
    def _calculate_posterior(self, successes: int, failures: int) -> stats.beta:
        """베타 사후분포 계산"""
        alpha_post = self.prior_alpha + successes
        beta_post = self.prior_beta + failures
        return stats.beta(alpha_post, beta_post)
    
    def _make_bayesian_decision(self, prob_better: float, 
                               loss_control: float, loss_treatment: float) -> Dict:
        """베이지안 의사결정"""
        if prob_better > 0.95 and loss_control < 0.01:
            decision = "treatment_winner"
            confidence = "high"
        elif prob_better < 0.05 and loss_treatment < 0.01:
            decision = "control_winner"
            confidence = "high"
        elif 0.8 <= prob_better <= 0.95:
            decision = "treatment_likely_better"
            confidence = "medium"
        elif 0.05 <= prob_better <= 0.2:
            decision = "control_likely_better"
            confidence = "medium"
        else:
            decision = "inconclusive"
            confidence = "low"
        
        return {
            'decision': decision,
            'confidence': confidence,
            'probability_better': prob_better,
            'recommendation': self._generate_recommendation(decision, confidence)
        }
    
    def _generate_recommendation(self, decision: str, confidence: str) -> str:
        """추천사항 생성"""
        recommendations = {
            'treatment_winner': "Treatment 변형을 전체 트래픽에 적용하세요.",
            'control_winner': "Control 변형을 유지하고 Treatment를 중단하세요.", 
            'treatment_likely_better': "더 많은 데이터를 수집하거나 Treatment 적용을 고려하세요.",
            'control_likely_better': "더 많은 데이터를 수집하거나 실험 중단을 고려하세요.",
            'inconclusive': "실험을 계속하거나 더 큰 효과를 가진 새로운 변형을 테스트하세요."
        }
        
        return recommendations.get(decision, "추가 분석이 필요합니다.")

class SequentialTesting:
    """순차적 테스트"""
    
    def __init__(self, alpha: float = 0.05, beta: float = 0.2):
        self.alpha = alpha
        self.beta = beta
        
    def setup_sprt(self, h0_rate: float, h1_rate: float) -> Dict:
        """Sequential Probability Ratio Test 설정"""
        # 가설 설정
        # H0: conversion_rate = h0_rate
        # H1: conversion_rate = h1_rate
        
        # 임계값 계산
        A = (1 - self.beta) / self.alpha  # 상한
        B = self.beta / (1 - self.alpha)  # 하한
        
        return {
            'h0_rate': h0_rate,
            'h1_rate': h1_rate,
            'upper_threshold': A,
            'lower_threshold': B,
            'alpha': self.alpha,
            'beta': self.beta,
            'decision_boundaries': self._calculate_decision_boundaries(h0_rate, h1_rate, A, B)
        }
    
    def analyze_sequential_data(self, sprt_config: Dict, 
                              conversions: int, visitors: int) -> Dict:
        """순차 데이터 분석"""
        h0_rate = sprt_config['h0_rate']
        h1_rate = sprt_config['h1_rate']
        
        # 우도비 계산
        if visitors == 0:
            likelihood_ratio = 1
        else:
            failures = visitors - conversions
            
            # 우도 계산
            likelihood_h1 = (h1_rate ** conversions) * ((1 - h1_rate) ** failures)
            likelihood_h0 = (h0_rate ** conversions) * ((1 - h0_rate) ** failures)
            
            likelihood_ratio = likelihood_h1 / likelihood_h0 if likelihood_h0 > 0 else float('inf')
        
        # 의사결정
        decision = self._make_sequential_decision(likelihood_ratio, sprt_config)
        
        return {
            'conversions': conversions,
            'visitors': visitors,
            'conversion_rate': conversions / visitors if visitors > 0 else 0,
            'likelihood_ratio': likelihood_ratio,
            'log_likelihood_ratio': np.log(likelihood_ratio) if likelihood_ratio > 0 else float('-inf'),
            'decision': decision,
            'continue_sampling': decision['action'] == 'continue'
        }
    
    def _make_sequential_decision(self, likelihood_ratio: float, 
                                sprt_config: Dict) -> Dict:
        """순차적 의사결정"""
        A = sprt_config['upper_threshold']
        B = sprt_config['lower_threshold']
        
        if likelihood_ratio >= A:
            return {
                'action': 'reject_h0',
                'conclusion': f'H1 채택: 전환율이 {sprt_config["h1_rate"]:.3f}',
                'confidence': 1 - sprt_config['alpha']
            }
        elif likelihood_ratio <= B:
            return {
                'action': 'accept_h0', 
                'conclusion': f'H0 채택: 전환율이 {sprt_config["h0_rate"]:.3f}',
                'confidence': 1 - sprt_config['beta']
            }
        else:
            return {
                'action': 'continue',
                'conclusion': '더 많은 데이터 필요',
                'confidence': None
            }

class MultiVariateTest:
    """다변량 테스트"""
    
    def __init__(self):
        self.factorial_designs = {}
        
    def setup_factorial_design(self, factors: Dict[str, List]) -> Dict:
        """팩토리얼 설계 설정"""
        import itertools
        
        # 모든 조합 생성
        factor_names = list(factors.keys())
        factor_levels = list(factors.values())
        
        combinations = list(itertools.product(*factor_levels))
        
        # 변형 생성
        variants = []
        for i, combo in enumerate(combinations):
            variant = {
                'id': f'variant_{i}',
                'factors': dict(zip(factor_names, combo))
            }
            variants.append(variant)
        
        design = {
            'factors': factors,
            'variants': variants,
            'total_variants': len(variants),
            'sample_size_adjustment': self._calculate_multivariate_sample_size(len(variants))
        }
        
        return design
    
    def _calculate_multivariate_sample_size(self, num_variants: int) -> Dict:
        """다변량 테스트 표본 크기 조정"""
        # Bonferroni 보정
        bonferroni_alpha = 0.05 / (num_variants - 1)  # 대조군 제외
        
        return {
            'bonferroni_corrected_alpha': bonferroni_alpha,
            'sample_size_multiplier': np.sqrt(num_variants),
            'recommendation': f'{num_variants}개 변형에 대해 표본 크기를 {np.sqrt(num_variants):.2f}배 증가 권장'
        }
    
    def analyze_factorial_results(self, results_data: pd.DataFrame,
                                 factors: List[str], outcome: str) -> Dict:
        """팩토리얼 결과 분석"""
        from sklearn.linear_model import LinearRegression
        from itertools import combinations
        
        # 주효과 분석
        main_effects = {}
        for factor in factors:
            factor_means = results_data.groupby(factor)[outcome].mean()
            main_effects[factor] = {
                'means_by_level': factor_means.to_dict(),
                'effect_size': factor_means.max() - factor_means.min()
            }
        
        # 교호작용 분석
        interaction_effects = {}
        for factor_pair in combinations(factors, 2):
            interaction_means = results_data.groupby(list(factor_pair))[outcome].mean()
            interaction_effects[f'{factor_pair[0]}_x_{factor_pair[1]}'] = {
                'means': interaction_means.to_dict(),
                'interaction_plot_data': interaction_means.reset_index()
            }
        
        # 회귀분석으로 효과 크기 추정
        X = pd.get_dummies(results_data[factors])
        y = results_data[outcome]
        
        model = LinearRegression()
        model.fit(X, y)
        
        return {
            'main_effects': main_effects,
            'interaction_effects': interaction_effects,
            'model_summary': {
                'r_squared': model.score(X, y),
                'coefficients': dict(zip(X.columns, model.coef_)),
                'intercept': model.intercept_
            },
            'recommendations': self._generate_factorial_recommendations(main_effects, interaction_effects)
        }
    
    def _generate_factorial_recommendations(self, main_effects: Dict, 
                                          interaction_effects: Dict) -> List[str]:
        """팩토리얼 추천사항"""
        recommendations = []
        
        # 가장 큰 주효과 찾기
        best_factor = max(main_effects.keys(), 
                         key=lambda x: main_effects[x]['effect_size'])
        recommendations.append(f"{best_factor} 요인이 가장 큰 효과를 보임")
        
        # 최적 수준 조합 찾기
        best_levels = {}
        for factor, effects in main_effects.items():
            best_level = max(effects['means_by_level'].keys(),
                           key=lambda x: effects['means_by_level'][x])
            best_levels[factor] = best_level
        
        recommendations.append(f"최적 조합: {best_levels}")
        
        return recommendations

# 실험 모니터링 대시보드
class ExperimentMonitor:
    """실험 모니터링"""
    
    def __init__(self):
        self.monitoring_alerts = []
        
    def create_monitoring_dashboard(self, experiment_data: pd.DataFrame) -> Dict:
        """모니터링 대시보드 생성"""
        # 실시간 지표 계산
        current_metrics = self._calculate_current_metrics(experiment_data)
        
        # 통계적 파워 모니터링
        power_analysis = self._monitor_statistical_power(experiment_data)
        
        # 품질 체크
        quality_checks = self._run_quality_checks(experiment_data)
        
        # 조기 중단 신호 체크
        early_stopping_signals = self._check_early_stopping(experiment_data)
        
        return {
            'current_metrics': current_metrics,
            'power_analysis': power_analysis,
            'quality_checks': quality_checks,
            'early_stopping': early_stopping_signals,
            'alerts': self.monitoring_alerts,
            'recommendations': self._generate_monitoring_recommendations(
                current_metrics, quality_checks, early_stopping_signals
            )
        }
    
    def _calculate_current_metrics(self, data: pd.DataFrame) -> Dict:
        """현재 지표 계산"""
        if data.empty:
            return {}
        
        metrics_by_variant = {}
        
        for variant in data['variant'].unique():
            variant_data = data[data['variant'] == variant]
            
            # 전환 관련 지표
            conversions = len(variant_data[variant_data['event_type'] == 'conversion'])
            visitors = variant_data['user_id'].nunique()
            
            metrics_by_variant[variant] = {
                'visitors': visitors,
                'conversions': conversions,
                'conversion_rate': conversions / visitors if visitors > 0 else 0,
                'daily_trend': self._calculate_daily_trend(variant_data)
            }
        
        return metrics_by_variant
    
    def _run_quality_checks(self, data: pd.DataFrame) -> Dict:
        """품질 체크"""
        checks = {}
        
        # 샘플 비율 체크 (SRM - Sample Ratio Mismatch)
        if not data.empty:
            variant_counts = data['variant'].value_counts()
            expected_ratio = 0.5  # 50:50 분할 가정
            
            if len(variant_counts) == 2:
                total = variant_counts.sum()
                observed_ratio = variant_counts.iloc[0] / total
                
                # 카이제곱 검정
                expected_counts = [total * expected_ratio, total * (1 - expected_ratio)]
                observed_counts = variant_counts.values
                
                chi2_stat, p_value = stats.chisquare(observed_counts, expected_counts)
                
                checks['sample_ratio_mismatch'] = {
                    'expected_ratio': expected_ratio,
                    'observed_ratio': observed_ratio,
                    'chi2_statistic': chi2_stat,
                    'p_value': p_value,
                    'is_significant': p_value < 0.01,  # 엄격한 기준
                    'status': 'FAIL' if p_value < 0.01 else 'PASS'
                }
        
        return checks
```

## 🚀 프로젝트
1. **완전 자동화 A/B 테스트 플랫폼**
2. **베이지안 실험 최적화 시스템**
3. **다변량 테스트 관리 도구**
4. **실시간 실험 모니터링 대시보드**