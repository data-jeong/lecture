# 62. Marketing Strategy Theory - 마케팅 전략 이론

## 📚 과정 소개
데이터 기반 마케팅 전략 수립을 위한 핵심 이론을 마스터합니다. 4P/7P 믹스부터 포터의 5 Force까지 전략적 프레임워크를 실무에 적용하는 방법을 학습합니다.

## 🎯 학습 목표
- 마케팅 믹스 4P/7P 최적화 전략
- 포트폴리오 매트릭스를 활용한 자원 배분
- 경쟁 우위 분석과 포지셔닝 전략
- 가치 제안 캔버스와 비즈니스 모델 설계

## 📖 주요 내용

### 마케팅 믹스와 전략적 프레임워크
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class MarketingStrategyAnalyzer:
    """마케팅 전략 분석을 위한 종합 클래스"""
    
    def __init__(self):
        self.strategies = {}
        self.scaler = StandardScaler()
        
    def marketing_mix_optimization(self, product_data, market_data):
        """4P/7P 마케팅 믹스 최적화"""
        
        # 4P 분석
        four_p_analysis = {
            'Product': self._analyze_product_strategy(product_data),
            'Price': self._analyze_pricing_strategy(product_data, market_data),
            'Place': self._analyze_distribution_strategy(market_data),
            'Promotion': self._analyze_promotion_strategy(product_data, market_data)
        }
        
        # 서비스 기업을 위한 추가 3P
        additional_3p = {
            'People': self._analyze_people_strategy(market_data),
            'Process': self._analyze_process_strategy(product_data),
            'Physical_Evidence': self._analyze_physical_evidence(product_data)
        }
        
        # 믹스 최적화
        mix_effectiveness = self._calculate_mix_effectiveness(four_p_analysis, additional_3p)
        
        return {
            '4P_analysis': four_p_analysis,
            '3P_additional': additional_3p,
            'mix_effectiveness': mix_effectiveness,
            'optimization_recommendations': self._generate_mix_recommendations(mix_effectiveness)
        }
    
    def _analyze_product_strategy(self, product_data):
        """제품 전략 분석"""
        # 제품 생명주기 분석
        lifecycle_stage = self._determine_lifecycle_stage(product_data)
        
        # 제품 포트폴리오 분석
        portfolio_analysis = {
            'core_products': product_data[product_data['revenue_contribution'] > 0.6],
            'growth_products': product_data[
                (product_data['growth_rate'] > 0.2) & 
                (product_data['market_share'] < 0.3)
            ],
            'cash_cows': product_data[
                (product_data['market_share'] > 0.3) & 
                (product_data['growth_rate'] < 0.1)
            ]
        }
        
        # 제품 차별화 분석
        differentiation_score = (
            product_data['innovation_index'] * 0.3 +
            product_data['quality_score'] * 0.3 +
            product_data['brand_strength'] * 0.4
        )
        
        return {
            'lifecycle_stage': lifecycle_stage,
            'portfolio_analysis': portfolio_analysis,
            'differentiation_score': differentiation_score,
            'canniblization_risk': self._calculate_cannibalization_risk(product_data)
        }
    
    def _analyze_pricing_strategy(self, product_data, market_data):
        """가격 전략 분석"""
        # 가격 탄력성 분석
        price_elasticity = self._calculate_price_elasticity(product_data, market_data)
        
        # 경쟁사 가격 포지셔닝
        competitive_pricing = self._analyze_competitive_pricing(product_data, market_data)
        
        # 가치 기반 가격 분석
        value_based_pricing = self._calculate_value_based_price(product_data, market_data)
        
        # 동적 가격 최적화
        dynamic_pricing_model = self._build_dynamic_pricing_model(product_data, market_data)
        
        return {
            'price_elasticity': price_elasticity,
            'competitive_positioning': competitive_pricing,
            'value_based_price': value_based_pricing,
            'dynamic_pricing': dynamic_pricing_model,
            'optimal_price_range': self._determine_optimal_price_range(price_elasticity, competitive_pricing)
        }
    
    def bcg_growth_share_matrix(self, business_units):
        """BCG 성장-점유율 매트릭스"""
        
        # 매트릭스 사분면 분류
        def classify_business_unit(row):
            if row['market_growth'] > 0.1 and row['relative_market_share'] > 1.0:
                return 'Stars'
            elif row['market_growth'] > 0.1 and row['relative_market_share'] <= 1.0:
                return 'Question Marks'
            elif row['market_growth'] <= 0.1 and row['relative_market_share'] > 1.0:
                return 'Cash Cows'
            else:
                return 'Dogs'
        
        business_units['bcg_category'] = business_units.apply(classify_business_unit, axis=1)
        
        # 자원 배분 전략 수립
        resource_allocation = {
            'Stars': 'Invest to maintain leadership',
            'Question Marks': 'Selective investment or divestiture',
            'Cash Cows': 'Harvest for cash generation',
            'Dogs': 'Divest or reposition'
        }
        
        # 포트폴리오 균형 분석
        portfolio_balance = business_units['bcg_category'].value_counts(normalize=True)
        
        # 시각화
        fig = px.scatter(business_units, 
                        x='relative_market_share', 
                        y='market_growth',
                        size='revenue',
                        color='bcg_category',
                        hover_name='business_unit',
                        title='BCG Growth-Share Matrix')
        
        fig.add_hline(y=0.1, line_dash="dash", line_color="gray")
        fig.add_vline(x=1.0, line_dash="dash", line_color="gray")
        fig.update_xaxis(title="Relative Market Share")
        fig.update_yaxis(title="Market Growth Rate")
        
        return {
            'classified_units': business_units,
            'resource_allocation': resource_allocation,
            'portfolio_balance': portfolio_balance,
            'visualization': fig
        }
    
    def ansoff_growth_matrix(self, growth_opportunities):
        """안소프 성장 매트릭스"""
        
        # 성장 전략 분류
        def classify_growth_strategy(row):
            if row['market_newness'] == 'existing' and row['product_newness'] == 'existing':
                return 'Market Penetration'
            elif row['market_newness'] == 'new' and row['product_newness'] == 'existing':
                return 'Market Development'
            elif row['market_newness'] == 'existing' and row['product_newness'] == 'new':
                return 'Product Development'
            else:
                return 'Diversification'
        
        growth_opportunities['growth_strategy'] = growth_opportunities.apply(classify_growth_strategy, axis=1)
        
        # 위험도 및 자원 요구도 분석
        risk_resource_matrix = {
            'Market Penetration': {'risk': 'Low', 'resources': 'Low', 'timeline': 'Short'},
            'Market Development': {'risk': 'Medium', 'resources': 'Medium', 'timeline': 'Medium'},
            'Product Development': {'risk': 'Medium', 'resources': 'High', 'timeline': 'Medium'},
            'Diversification': {'risk': 'High', 'resources': 'High', 'timeline': 'Long'}
        }
        
        # 성장 전략별 ROI 예측
        strategy_roi = self._calculate_strategy_roi(growth_opportunities)
        
        # 포트폴리오 최적화
        optimal_portfolio = self._optimize_growth_portfolio(growth_opportunities, strategy_roi)
        
        return {
            'classified_opportunities': growth_opportunities,
            'risk_resource_analysis': risk_resource_matrix,
            'strategy_roi': strategy_roi,
            'optimal_portfolio': optimal_portfolio
        }
    
    def porter_five_forces_analysis(self, market_data):
        """포터의 5 Force 분석"""
        
        forces_scores = {}
        
        # 1. 기존 경쟁자 간의 경쟁
        competitive_rivalry = (
            market_data['competitor_count'] * 0.3 +
            market_data['market_growth_rate'] * (-0.2) +  # 역상관
            market_data['product_differentiation'] * (-0.2) +  # 역상관
            market_data['switching_costs'] * (-0.3)  # 역상관
        )
        forces_scores['Competitive Rivalry'] = np.clip(competitive_rivalry, 0, 1)
        
        # 2. 신규 진입자의 위협
        threat_of_new_entrants = (
            market_data['entry_barriers'] * (-0.4) +  # 역상관
            market_data['capital_requirements'] * (-0.2) +  # 역상관
            market_data['economies_of_scale'] * (-0.2) +  # 역상관
            market_data['government_regulation'] * (-0.2)  # 역상관
        )
        forces_scores['Threat of New Entrants'] = np.clip(threat_of_new_entrants, 0, 1)
        
        # 3. 대체재의 위협
        threat_of_substitutes = (
            market_data['substitute_availability'] * 0.4 +
            market_data['substitute_price_performance'] * 0.3 +
            market_data['switching_propensity'] * 0.3
        )
        forces_scores['Threat of Substitutes'] = np.clip(threat_of_substitutes, 0, 1)
        
        # 4. 구매자의 교섭력
        buyer_power = (
            market_data['buyer_concentration'] * 0.3 +
            market_data['price_sensitivity'] * 0.3 +
            market_data['backward_integration_threat'] * 0.2 +
            market_data['product_importance'] * (-0.2)  # 역상관
        )
        forces_scores['Buyer Power'] = np.clip(buyer_power, 0, 1)
        
        # 5. 공급자의 교섭력
        supplier_power = (
            market_data['supplier_concentration'] * 0.3 +
            market_data['input_uniqueness'] * 0.3 +
            market_data['forward_integration_threat'] * 0.2 +
            market_data['supplier_switching_cost'] * 0.2
        )
        forces_scores['Supplier Power'] = np.clip(supplier_power, 0, 1)
        
        # 전체 산업 매력도 계산
        industry_attractiveness = 1 - np.mean(list(forces_scores.values()))
        
        # 전략적 권고사항
        strategic_recommendations = self._generate_porter_recommendations(forces_scores)
        
        # 시각화
        fig = go.Figure()
        
        forces = list(forces_scores.keys())
        scores = list(forces_scores.values())
        
        fig.add_trace(go.Scatterpolar(
            r=scores,
            theta=forces,
            fill='toself',
            name='Industry Forces'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title="Porter's Five Forces Analysis"
        )
        
        return {
            'forces_scores': forces_scores,
            'industry_attractiveness': industry_attractiveness,
            'strategic_recommendations': strategic_recommendations,
            'visualization': fig
        }
    
    def swot_pestle_analysis(self, internal_data, external_data):
        """SWOT & PESTLE 통합 분석"""
        
        # SWOT 분석
        swot_matrix = {
            'Strengths': self._identify_strengths(internal_data),
            'Weaknesses': self._identify_weaknesses(internal_data),
            'Opportunities': self._identify_opportunities(external_data),
            'Threats': self._identify_threats(external_data)
        }
        
        # PESTLE 분석  
        pestle_factors = {
            'Political': external_data['political_stability'] * external_data['regulatory_support'],
            'Economic': external_data['economic_growth'] * external_data['inflation_rate'] * (-1),
            'Social': external_data['demographic_trends'] * external_data['cultural_acceptance'],
            'Technological': external_data['tech_advancement'] * external_data['digital_adoption'],
            'Legal': external_data['legal_compliance'] * external_data['intellectual_property'],
            'Environmental': external_data['sustainability_trends'] * external_data['environmental_regulations']
        }
        
        # SWOT-PESTLE 교차 분석
        strategic_options = self._cross_analyze_swot_pestle(swot_matrix, pestle_factors)
        
        # 전략 우선순위 매트릭스
        priority_matrix = self._create_strategy_priority_matrix(strategic_options)
        
        return {
            'swot_analysis': swot_matrix,
            'pestle_analysis': pestle_factors,
            'strategic_options': strategic_options,
            'priority_matrix': priority_matrix
        }
    
    def value_proposition_canvas(self, customer_jobs, pains, gains, products_services):
        """가치 제안 캔버스"""
        
        # 고객 프로필 분석
        customer_profile = {
            'jobs_to_be_done': self._analyze_customer_jobs(customer_jobs),
            'customer_pains': self._analyze_customer_pains(pains),
            'customer_gains': self._analyze_customer_gains(gains)
        }
        
        # 가치 맵 분석
        value_map = {
            'pain_relievers': self._identify_pain_relievers(products_services, pains),
            'gain_creators': self._identify_gain_creators(products_services, gains),
            'products_services': self._analyze_product_services(products_services)
        }
        
        # 제품-시장 적합성 점수
        product_market_fit_score = self._calculate_pmf_score(customer_profile, value_map)
        
        # 가치 제안 최적화
        optimized_value_proposition = self._optimize_value_proposition(customer_profile, value_map)
        
        # 경쟁 우위 분석
        competitive_advantage = self._analyze_competitive_advantage(value_map)
        
        return {
            'customer_profile': customer_profile,
            'value_map': value_map,
            'pmf_score': product_market_fit_score,
            'optimized_proposition': optimized_value_proposition,
            'competitive_advantage': competitive_advantage
        }
    
    def competitive_positioning_analysis(self, company_data, competitor_data):
        """경쟁적 포지셔닝 분석"""
        
        # 경쟁사 벤치마킹
        competitive_benchmarks = self._benchmark_competitors(company_data, competitor_data)
        
        # 포지셔닝 맵 생성
        positioning_dimensions = ['price', 'quality', 'innovation', 'service', 'brand_strength']
        positioning_map = self._create_positioning_map(company_data, competitor_data, positioning_dimensions)
        
        # 화이트스페이스 분석 (시장 기회 영역)
        white_space_opportunities = self._identify_white_spaces(positioning_map)
        
        # 경쟁 우위 전략
        competitive_strategies = {
            'cost_leadership': self._analyze_cost_leadership_potential(company_data, competitor_data),
            'differentiation': self._analyze_differentiation_potential(company_data, competitor_data),
            'focus_strategy': self._analyze_focus_strategy_potential(company_data, competitor_data)
        }
        
        # 전략 권고사항
        strategic_recommendations = self._recommend_competitive_strategy(competitive_strategies, positioning_map)
        
        return {
            'competitive_benchmarks': competitive_benchmarks,
            'positioning_map': positioning_map,
            'white_space_opportunities': white_space_opportunities,
            'competitive_strategies': competitive_strategies,
            'recommendations': strategic_recommendations
        }
    
    def marketing_roi_optimization(self, campaign_data, channel_data):
        """마케팅 ROI 최적화"""
        
        # 채널별 효율성 분석
        channel_efficiency = self._analyze_channel_efficiency(channel_data)
        
        # 마케팅 믹스 모델링
        mmm_results = self._build_marketing_mix_model(campaign_data, channel_data)
        
        # 예산 배분 최적화
        optimal_budget_allocation = self._optimize_budget_allocation(channel_efficiency, mmm_results)
        
        # 시너지 효과 분석
        synergy_analysis = self._analyze_channel_synergies(channel_data)
        
        # ROI 예측 모델
        roi_prediction_model = self._build_roi_prediction_model(campaign_data, channel_data)
        
        return {
            'channel_efficiency': channel_efficiency,
            'mmm_results': mmm_results,
            'optimal_allocation': optimal_budget_allocation,
            'synergy_effects': synergy_analysis,
            'roi_prediction': roi_prediction_model
        }

# 보조 메서드들 (일부 구현)
    def _determine_lifecycle_stage(self, product_data):
        """제품 생명주기 단계 결정"""
        growth_rate = product_data['growth_rate'].mean()
        market_share = product_data['market_share'].mean()
        profit_margin = product_data['profit_margin'].mean()
        
        if growth_rate > 0.3 and market_share < 0.2:
            return 'Introduction'
        elif growth_rate > 0.2 and profit_margin > 0.15:
            return 'Growth'
        elif growth_rate < 0.1 and market_share > 0.3:
            return 'Maturity'
        else:
            return 'Decline'
    
    def _calculate_price_elasticity(self, product_data, market_data):
        """가격 탄력성 계산"""
        price_changes = product_data['price'].pct_change().dropna()
        demand_changes = product_data['demand'].pct_change().dropna()
        
        if len(price_changes) > 1 and len(demand_changes) > 1:
            elasticity = np.corrcoef(price_changes, demand_changes)[0, 1]
            return elasticity
        return -1.0  # 기본값
    
    def _generate_porter_recommendations(self, forces_scores):
        """포터 분석 기반 전략 권고"""
        recommendations = {}
        
        for force, score in forces_scores.items():
            if score > 0.7:
                if force == 'Competitive Rivalry':
                    recommendations[force] = "Focus on differentiation and niche markets"
                elif force == 'Threat of New Entrants':
                    recommendations[force] = "Strengthen barriers to entry"
                elif force == 'Threat of Substitutes':
                    recommendations[force] = "Enhance value proposition and customer loyalty"
                elif force == 'Buyer Power':
                    recommendations[force] = "Reduce buyer concentration dependency"
                elif force == 'Supplier Power':
                    recommendations[force] = "Diversify supplier base"
        
        return recommendations

# 실습 예제: 종합 전략 분석
def comprehensive_strategy_analysis():
    """종합적인 마케팅 전략 분석"""
    
    # 샘플 데이터 생성
    np.random.seed(42)
    
    # 비즈니스 유닛 데이터 (BCG 매트릭스용)
    business_units = pd.DataFrame({
        'business_unit': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
        'market_growth': [0.15, 0.08, 0.25, 0.05, 0.18],
        'relative_market_share': [1.5, 2.1, 0.8, 0.3, 1.2],
        'revenue': [100, 150, 80, 40, 90]
    })
    
    # 시장 데이터 (포터 5 Force용)
    market_data = pd.DataFrame({
        'competitor_count': [0.7],
        'market_growth_rate': [0.6],
        'product_differentiation': [0.4],
        'switching_costs': [0.3],
        'entry_barriers': [0.6],
        'capital_requirements': [0.8],
        'economies_of_scale': [0.7],
        'government_regulation': [0.5],
        'substitute_availability': [0.4],
        'substitute_price_performance': [0.3],
        'switching_propensity': [0.2],
        'buyer_concentration': [0.6],
        'price_sensitivity': [0.7],
        'backward_integration_threat': [0.2],
        'product_importance': [0.8],
        'supplier_concentration': [0.5],
        'input_uniqueness': [0.4],
        'forward_integration_threat': [0.1],
        'supplier_switching_cost': [0.3]
    })
    
    # 분석기 초기화
    analyzer = MarketingStrategyAnalyzer()
    
    # 1. BCG 매트릭스 분석
    bcg_results = analyzer.bcg_growth_share_matrix(business_units)
    
    # 2. 포터 5 Force 분석
    porter_results = analyzer.porter_five_forces_analysis(market_data.iloc[0])
    
    # 결과 출력
    print("=== BCG Growth-Share Matrix Results ===")
    print(bcg_results['portfolio_balance'])
    print(f"\nIndustry Attractiveness Score: {porter_results['industry_attractiveness']:.3f}")
    
    # 시각화
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # BCG 매트릭스 시각화
    colors = {'Stars': 'gold', 'Cash Cows': 'green', 'Question Marks': 'orange', 'Dogs': 'red'}
    for category in business_units['bcg_category'].unique():
        data = business_units[business_units['bcg_category'] == category]
        axes[0].scatter(data['relative_market_share'], data['market_growth'], 
                       s=data['revenue']*2, c=colors[category], label=category, alpha=0.7)
    
    axes[0].axhline(y=0.1, color='gray', linestyle='--', alpha=0.5)
    axes[0].axvline(x=1.0, color='gray', linestyle='--', alpha=0.5)
    axes[0].set_xlabel('Relative Market Share')
    axes[0].set_ylabel('Market Growth Rate')
    axes[0].set_title('BCG Growth-Share Matrix')
    axes[0].legend()
    
    # 포터 5 Force 시각화
    forces = list(porter_results['forces_scores'].keys())
    scores = list(porter_results['forces_scores'].values())
    
    axes[1].bar(range(len(forces)), scores, color='skyblue', alpha=0.7)
    axes[1].set_xticks(range(len(forces)))
    axes[1].set_xticklabels([f.replace(' ', '\n') for f in forces], rotation=0, ha='center')
    axes[1].set_ylabel('Force Intensity')
    axes[1].set_title("Porter's Five Forces Analysis")
    axes[1].set_ylim(0, 1)
    
    plt.tight_layout()
    plt.show()
    
    return {
        'bcg_results': bcg_results,
        'porter_results': porter_results,
        'business_units': business_units,
        'market_data': market_data
    }

# 메인 실행
if __name__ == "__main__":
    print("=== 마케팅 전략 이론 실습 ===")
    print("BCG 매트릭스와 포터 5 Force를 활용한 전략 분석")
    
    results = comprehensive_strategy_analysis()
    
    print(f"\n전략 분석 완료:")
    print(f"- 포트폴리오 균형도: {results['bcg_results']['portfolio_balance'].to_dict()}")
    print(f"- 산업 매력도: {results['porter_results']['industry_attractiveness']:.3f}")
    print(f"- 주요 전략 권고사항: {len(results['porter_results']['strategic_recommendations'])}개")
```

## 🚀 프로젝트
1. **전략 포트폴리오 대시보드** - BCG/안소프 매트릭스 통합 분석
2. **경쟁 인텔리전스 시스템** - 포터 5 Force 실시간 모니터링
3. **가치 제안 최적화 도구** - 고객 여정 기반 가치 캔버스
4. **마케팅 ROI 예측 모델** - 믹스 최적화와 예산 배분 시뮬레이션