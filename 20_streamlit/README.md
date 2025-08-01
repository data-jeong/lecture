# 20. Streamlit - 스트림릿

## 📚 과정 소개
Streamlit으로 대화형 광고 분석 대시보드와 데이터 앱을 구축합니다. 실시간 성과 모니터링부터 ML 모델 배포까지 웹 기반 분석 도구를 개발합니다.

## 🎯 학습 목표
- 실시간 광고 성과 대시보드
- 인터랙티브 데이터 분석 도구
- ML 모델 배포 및 시연
- 광고 최적화 시뮬레이터

## 📖 주요 내용

### 광고 대시보드 앱
```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# 페이지 설정
st.set_page_config(
    page_title="광고 플랫폼 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AdDashboard:
    def __init__(self):
        self.load_data()
        
    @st.cache_data
    def load_data(self):
        """데이터 로드 (캐시됨)"""
        # 실제로는 데이터베이스에서 로드
        dates = pd.date_range('2024-01-01', periods=90, freq='D')
        
        self.campaign_data = pd.DataFrame({
            'date': np.repeat(dates, 5),
            'campaign': np.tile(['Campaign A', 'Campaign B', 'Campaign C', 'Campaign D', 'Campaign E'], len(dates)),
            'impressions': np.random.randint(1000, 10000, len(dates) * 5),
            'clicks': np.random.randint(50, 500, len(dates) * 5),
            'conversions': np.random.randint(1, 50, len(dates) * 5),
            'cost': np.random.uniform(100, 1000, len(dates) * 5),
            'revenue': np.random.uniform(200, 2000, len(dates) * 5)
        })
        
        # 파생 지표 계산
        self.campaign_data['ctr'] = self.campaign_data['clicks'] / self.campaign_data['impressions']
        self.campaign_data['cvr'] = self.campaign_data['conversions'] / self.campaign_data['clicks']
        self.campaign_data['cpc'] = self.campaign_data['cost'] / self.campaign_data['clicks']
        self.campaign_data['roas'] = self.campaign_data['revenue'] / self.campaign_data['cost']

def main():
    dashboard = AdDashboard()
    
    # 사이드바
    st.sidebar.title("🎯 필터")
    
    # 날짜 범위 선택
    date_range = st.sidebar.date_input(
        "날짜 범위",
        value=(dashboard.campaign_data['date'].min(), dashboard.campaign_data['date'].max()),
        min_value=dashboard.campaign_data['date'].min(),
        max_value=dashboard.campaign_data['date'].max()
    )
    
    # 캠페인 선택
    campaigns = st.sidebar.multiselect(
        "캠페인 선택",  
        dashboard.campaign_data['campaign'].unique(),
        default=dashboard.campaign_data['campaign'].unique()
    )
    
    # 데이터 필터링
    filtered_data = dashboard.campaign_data[
        (dashboard.campaign_data['date'] >= pd.Timestamp(date_range[0])) &
        (dashboard.campaign_data['date'] <= pd.Timestamp(date_range[1])) &
        (dashboard.campaign_data['campaign'].isin(campaigns))
    ]
    
    # 메인 대시보드
    st.title("📊 광고 플랫폼 실시간 대시보드")
    
    # KPI 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_impressions = filtered_data['impressions'].sum()
        st.metric("총 노출수", f"{total_impressions:,}", delta="12.5%")
    
    with col2:
        total_clicks = filtered_data['clicks'].sum()
        avg_ctr = filtered_data['ctr'].mean()
        st.metric("총 클릭수", f"{total_clicks:,}", delta=f"CTR: {avg_ctr:.2%}")
    
    with col3:
        total_cost = filtered_data['cost'].sum()
        st.metric("총 비용", f"₩{total_cost:,.0f}", delta="-5.2%")
    
    with col4:
        total_revenue = filtered_data['revenue'].sum()
        avg_roas = filtered_data['roas'].mean()
        st.metric("총 매출", f"₩{total_revenue:,.0f}", delta=f"ROAS: {avg_roas:.1f}")
    
    # 차트 섹션
    st.subheader("📈 성과 트렌드")
    
    tab1, tab2, tab3 = st.tabs(["일별 트렌드", "캠페인 비교", "상세 분석"])
    
    with tab1:
        # 일별 트렌드 차트
        daily_data = filtered_data.groupby('date').agg({
            'impressions': 'sum',
            'clicks': 'sum', 
            'cost': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_data['date'], y=daily_data['cost'], 
                                name='비용', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=daily_data['date'], y=daily_data['revenue'], 
                                name='매출', line=dict(color='green')))
        
        fig.update_layout(title="일별 비용 vs 매출", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # 캠페인별 성과 비교
        campaign_summary = filtered_data.groupby('campaign').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'cost': 'sum', 
            'revenue': 'sum'
        }).reset_index()
        
        campaign_summary['roas'] = campaign_summary['revenue'] / campaign_summary['cost']
        
        fig = px.bar(campaign_summary, x='campaign', y='roas', 
                    title="캠페인별 ROAS 비교")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # 상세 분석 테이블
        st.subheader("상세 성과 데이터")
        
        display_data = filtered_data.groupby(['campaign', 'date']).agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum', 
            'cost': 'sum',
            'revenue': 'sum',
            'ctr': 'mean',
            'cvr': 'mean',
            'roas': 'mean'
        }).round(3).reset_index()
        
        st.dataframe(display_data, use_container_width=True)
        
        # CSV 다운로드
        csv = display_data.to_csv(index=False)
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv,
            file_name=f"campaign_performance_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
```

### A/B 테스트 시뮬레이터
```python
import streamlit as st
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ABTestSimulator:
    def __init__(self):
        self.setup_ui()
    
    def setup_ui(self):
        st.title("🧪 A/B 테스트 시뮬레이터")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Control (A)")
            self.control_visitors = st.number_input("방문자 수 (A)", min_value=100, value=1000, step=100)
            self.control_rate = st.slider("전환율 (A)", 0.01, 0.20, 0.05, 0.001, format="%.3f")
            
        with col2:
            st.subheader("Variant (B)")  
            self.variant_visitors = st.number_input("방문자 수 (B)", min_value=100, value=1000, step=100)
            self.variant_rate = st.slider("전환율 (B)", 0.01, 0.20, 0.06, 0.001, format="%.3f")
        
        # 시뮬레이션 실행
        if st.button("🚀 시뮬레이션 실행"):
            self.run_simulation()
    
    def run_simulation(self):
        # 데이터 생성
        control_conversions = np.random.binomial(self.control_visitors, self.control_rate)
        variant_conversions = np.random.binomial(self.variant_visitors, self.variant_rate)
        
        # 통계 검정
        stat_result = self.statistical_test(
            control_conversions, self.control_visitors,
            variant_conversions, self.variant_visitors
        )
        
        # 결과 표시
        self.display_results(control_conversions, variant_conversions, stat_result)
    
    def statistical_test(self, control_conv, control_vis, variant_conv, variant_vis):
        """통계적 유의성 검정"""
        from statsmodels.stats.proportion import proportions_ztest
        
        counts = np.array([control_conv, variant_conv])
        nobs = np.array([control_vis, variant_vis])
        
        z_stat, p_value = proportions_ztest(counts, nobs)
        
        control_rate_actual = control_conv / control_vis
        variant_rate_actual = variant_conv / variant_vis
        lift = (variant_rate_actual - control_rate_actual) / control_rate_actual
        
        return {
            'z_stat': z_stat,
            'p_value': p_value,
            'control_rate': control_rate_actual,
            'variant_rate': variant_rate_actual,
            'lift': lift,
            'significant': p_value < 0.05
        }
    
    def display_results(self, control_conv, variant_conv, stat_result):
        """결과 표시"""
        st.subheader("📊 테스트 결과")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Control 전환율", f"{stat_result['control_rate']:.3f}")
            st.metric("Control 전환수", control_conv)
        
        with col2:
            st.metric("Variant 전환율", f"{stat_result['variant_rate']:.3f}")
            st.metric("Variant 전환수", variant_conv)
        
        with col3:
            st.metric("Lift", f"{stat_result['lift']:.1%}")
            st.metric("P-value", f"{stat_result['p_value']:.4f}")
        
        # 유의성 판정
        if stat_result['significant']:
            st.success("🎉 통계적으로 유의한 차이가 있습니다!")
        else:
            st.warning("⚠️ 통계적으로 유의한 차이가 없습니다.")
        
        # 신뢰구간 차트
        self.plot_confidence_intervals(stat_result)
    
    def plot_confidence_intervals(self, stat_result):
        """신뢰구간 시각화"""
        control_ci = self.calculate_ci(stat_result['control_rate'], self.control_visitors)
        variant_ci = self.calculate_ci(stat_result['variant_rate'], self.variant_visitors)
        
        fig = go.Figure()
        
        # Control
        fig.add_trace(go.Scatter(
            x=['Control'],
            y=[stat_result['control_rate']],
            error_y=dict(
                type='data',
                symmetric=False,
                array=[control_ci[1] - stat_result['control_rate']],
                arrayminus=[stat_result['control_rate'] - control_ci[0]]
            ),
            mode='markers',
            name='Control',
            marker_size=10
        ))
        
        # Variant
        fig.add_trace(go.Scatter(
            x=['Variant'],
            y=[stat_result['variant_rate']],
            error_y=dict(
                type='data', 
                symmetric=False,
                array=[variant_ci[1] - stat_result['variant_rate']],
                arrayminus=[stat_result['variant_rate'] - variant_ci[0]]
            ),
            mode='markers',
            name='Variant',
            marker_size=10
        ))
        
        fig.update_layout(
            title="95% 신뢰구간",
            yaxis_title="전환율",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def calculate_ci(self, rate, n, confidence=0.95):
        """신뢰구간 계산"""
        z = stats.norm.ppf(1 - (1 - confidence) / 2)
        se = np.sqrt(rate * (1 - rate) / n)
        return (rate - z * se, rate + z * se)

# A/B 테스트 시뮬레이터 실행
ab_simulator = ABTestSimulator()
```

### ML 모델 배포 앱
```python
import streamlit as st
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import plotly.express as px

class MLModelApp:
    def __init__(self):
        self.setup_sidebar()
        self.main_content()
    
    def setup_sidebar(self):
        st.sidebar.title("🤖 ML 모델 설정")
        
        self.model_type = st.sidebar.selectbox(
            "모델 선택",
            ["CTR 예측", "고객 세분화", "LTV 예측"]
        )
        
        if self.model_type == "CTR 예측":
            self.ctr_prediction_app()
        elif self.model_type == "고객 세분화":
            self.customer_segmentation_app()
        else:
            self.ltv_prediction_app()
    
    def main_content(self):
        st.title("🎯 ML 모델 데모")
        st.write("사이드바에서 원하는 모델을 선택하세요.")
    
    def ctr_prediction_app(self):
        st.subheader("📊 CTR 예측 모델")
        
        # 입력 파라미터
        st.sidebar.subheader("광고 파라미터")
        
        campaign_budget = st.sidebar.slider("캠페인 예산", 1000, 100000, 10000)
        target_age = st.sidebar.slider("타겟 연령", 18, 65, 35)
        ad_position = st.sidebar.selectbox("광고 위치", ["상단", "측면", "하단"])
        device_type = st.sidebar.selectbox("디바이스", ["모바일", "데스크톱", "태블릿"])
        time_of_day = st.sidebar.slider("시간대", 0, 23, 12)
        
        # 예측 실행
        if st.sidebar.button("CTR 예측"):
            predicted_ctr = self.predict_ctr(campaign_budget, target_age, ad_position, device_type, time_of_day)
            
            # 결과 표시
            col1, col2 = st.columns(2) 
            
            with col1:
                st.metric("예상 CTR", f"{predicted_ctr:.3%}")
                
                # CTR 범주 분류
                if predicted_ctr > 0.05:
                    category = "높음"
                    color = "green"
                elif predicted_ctr > 0.02:
                    category = "보통"  
                    color = "orange"
                else:
                    category = "낮음"
                    color = "red"
                
                st.markdown(f"**CTR 등급:** :{color}[{category}]")
            
            with col2:
                # 예상 성과 계산
                expected_impressions = campaign_budget * 10  # 가정
                expected_clicks = expected_impressions * predicted_ctr
                expected_cpc = campaign_budget / expected_clicks if expected_clicks > 0 else 0
                
                st.metric("예상 클릭수", f"{expected_clicks:.0f}")
                st.metric("예상 CPC", f"₩{expected_cpc:.0f}")
            
            # 시각화
            self.plot_ctr_factors(target_age, time_of_day, predicted_ctr)
    
    def predict_ctr(self, budget, age, position, device, hour):
        """CTR 예측 (간단한 휴리스틱 모델)"""
        base_ctr = 0.025
        
        # 예산 효과
        budget_factor = min(budget / 50000, 2)  # 최대 2배
        
        # 연령 효과 (25-35세가 최적)
        age_factor = 1.5 if 25 <= age <= 35 else 1.0
        
        # 위치 효과
        position_factors = {"상단": 1.5, "측면": 1.0, "하단": 0.7}
        position_factor = position_factors[position]
        
        # 디바이스 효과
        device_factors = {"모바일": 1.3, "데스크톱": 1.0, "태블릿": 0.9}
        device_factor = device_factors[device]
        
        # 시간대 효과 (저녁 시간이 좋음)
        time_factor = 1.4 if 19 <= hour <= 22 else 1.0
        
        predicted_ctr = base_ctr * budget_factor * age_factor * position_factor * device_factor * time_factor
        return min(predicted_ctr, 0.15)  # 최대 15%
    
    def plot_ctr_factors(self, age, hour, predicted_ctr):
        """CTR 영향 요인 시각화"""
        st.subheader("📈 CTR 영향 요인 분석")
        
        # 연령대별 CTR 트렌드
        ages = list(range(18, 66))
        ctrs = [self.predict_ctr(10000, a, "상단", "모바일", hour) for a in ages]
        
        fig = px.line(x=ages, y=ctrs, title="연령대별 예상 CTR")
        fig.add_vline(x=age, line_dash="dash", line_color="red", annotation_text="현재 타겟")
        fig.update_xaxis(title="연령")
        fig.update_yaxis(title="CTR", tickformat=".1%")
        
        st.plotly_chart(fig, use_container_width=True)
    
    def customer_segmentation_app(self):
        st.subheader("👥 고객 세분화")
        
        # 샘플 데이터 업로드
        uploaded_file = st.sidebar.file_uploader("고객 데이터 업로드", type=['csv'])
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("업로드된 데이터:")
            st.dataframe(df.head())
        else:
            # 샘플 데이터 생성
            df = self.generate_sample_customer_data()
            st.write("샘플 고객 데이터:")
            st.dataframe(df.head())
        
        # 세분화 실행
        if st.sidebar.button("세분화 실행"):
            segments = self.perform_segmentation(df)
            self.display_segmentation_results(df, segments)
    
    def generate_sample_customer_data(self):
        """샘플 고객 데이터 생성"""
        np.random.seed(42)
        n_customers = 1000
        
        return pd.DataFrame({
            'customer_id': [f'C{i:04d}' for i in range(n_customers)],
            'recency': np.random.exponential(30, n_customers),
            'frequency': np.random.poisson(5, n_customers) + 1,
            'monetary': np.random.lognormal(6, 1, n_customers),
            'age': np.random.normal(40, 12, n_customers),
            'tenure_months': np.random.randint(1, 60, n_customers)
        })
    
    def perform_segmentation(self, df):
        """RFM 세분화 수행"""
        # RFM 점수 계산
        df['r_score'] = pd.qcut(df['recency'].rank(method='first'), 5, labels=[5,4,3,2,1])
        df['f_score'] = pd.qcut(df['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])  
        df['m_score'] = pd.qcut(df['monetary'].rank(method='first'), 5, labels=[1,2,3,4,5])
        
        # 세그먼트 분류
        def classify_segment(row):
            r, f, m = int(row['r_score']), int(row['f_score']), int(row['m_score'])
            
            if r >= 4 and f >= 4 and m >= 4:
                return 'Champions'
            elif r >= 3 and f >= 3:
                return 'Loyal Customers'
            elif r >= 4 and f <= 2:
                return 'New Customers'
            elif r <= 2 and f >= 3:
                return 'At Risk'
            else:
                return 'Others'
        
        df['segment'] = df.apply(classify_segment, axis=1)
        return df['segment'].values
    
    def display_segmentation_results(self, df, segments):
        """세분화 결과 표시"""
        segment_counts = pd.Series(segments).value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 세그먼트 분포 파이차트
            fig = px.pie(values=segment_counts.values, names=segment_counts.index, 
                        title="고객 세그먼트 분포")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 세그먼트별 평균 지표
            df['segment'] = segments
            segment_summary = df.groupby('segment').agg({
                'recency': 'mean',
                'frequency': 'mean', 
                'monetary': 'mean'
            }).round(2)
            
            st.write("세그먼트별 평균 지표:")
            st.dataframe(segment_summary)
    
    def ltv_prediction_app(self):
        st.subheader("💰 고객 생애 가치 예측")
        
        st.sidebar.subheader("고객 정보")
        
        # 고객 특성 입력
        recency = st.sidebar.slider("최근 구매일 (일전)", 1, 365, 30)
        frequency = st.sidebar.slider("구매 횟수", 1, 50, 5) 
        monetary = st.sidebar.slider("총 구매금액", 1000, 1000000, 100000)
        tenure = st.sidebar.slider("가입 기간 (월)", 1, 60, 12)
        
        if st.sidebar.button("LTV 예측"):
            predicted_ltv = self.predict_ltv(recency, frequency, monetary, tenure)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("예상 LTV", f"₩{predicted_ltv:,.0f}")
                
                # LTV 등급
                if predicted_ltv > 500000:
                    grade = "A (높음)"
                    color = "green"
                elif predicted_ltv > 200000:
                    grade = "B (보통)"
                    color = "orange"  
                else:
                    grade = "C (낮음)"
                    color = "red"
                
                st.markdown(f"**LTV 등급:** :{color}[{grade}]")
            
            with col2:
                # 마케팅 추천
                self.recommend_marketing_strategy(predicted_ltv, recency, frequency)
    
    def predict_ltv(self, recency, frequency, monetary, tenure):
        """LTV 예측 (간단한 모델)"""
        # 기본 LTV = 과거 구매 패턴 기반 미래 예측
        avg_order_value = monetary / frequency
        purchase_frequency_yearly = frequency / (tenure / 12) if tenure > 0 else frequency
        
        # 이탈 확률 계산 (Recency 기반)
        churn_prob = min(recency / 365, 0.8)  # 최대 80%
        retention_prob = 1 - churn_prob
        
        # 예상 잔여 생애 (년)
        expected_lifetime = 2 * retention_prob  # 최대 2년
        
        # LTV 계산
        predicted_ltv = avg_order_value * purchase_frequency_yearly * expected_lifetime
        
        return max(predicted_ltv, 0)
    
    def recommend_marketing_strategy(self, ltv, recency, frequency):
        """마케팅 전략 추천"""
        st.subheader("🎯 추천 마케팅 전략")
        
        if ltv > 500000:
            st.success("💎 VIP 고객 관리 프로그램 적용")
            st.write("- 개인 맞춤 서비스 제공")
            st.write("- 프리미엄 혜택 및 이벤트 초대")
        elif ltv > 200000:
            st.info("⭐ 충성도 향상 프로그램 적용")
            st.write("- 정기적인 할인 쿠폰 제공")
            st.write("- 회원 등급 업그레이드 혜택")
        else:
            st.warning("📢 활성화 캠페인 필요")
            st.write("- 재구매 유도 이벤트")
            st.write("- 신제품 정보 제공")
        
        if recency > 90:
            st.error("🚨 이탈 위험 고객 - 윈백 캠페인 즉시 실행!")

# 메인 앱 실행
if __name__ == "__main__":
    ml_app = MLModelApp()
```

## 🚀 프로젝트
1. **실시간 광고 대시보드**
2. **A/B 테스트 시뮬레이터** 
3. **ML 모델 데모 플랫폼**
4. **광고 최적화 도구**