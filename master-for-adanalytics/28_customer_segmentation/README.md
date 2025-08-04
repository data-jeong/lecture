# 28. Customer Segmentation - 고객 세분화

## 📚 과정 소개
머신러닝을 활용한 고객 세분화와 개인화 마케팅 전략을 마스터합니다. RFM 분석부터 고급 클러스터링까지 실무에 바로 적용할 수 있는 기법을 학습합니다.

## 🎯 학습 목표
- RFM 기반 고객 세분화
- 클러스터링 알고리즘 활용
- 개인화 마케팅 전략 수립
- 고객 생애 가치(LTV) 예측

## 📖 주요 내용

### RFM 분석 구현
```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import Dict, List, Tuple
import plotly.express as px
import plotly.graph_objects as go

class RFMAnalyzer:
    """RFM 분석기"""
    
    def __init__(self):
        self.rfm_data = None
        self.segments = None
        
    def calculate_rfm(self, transactions_df: pd.DataFrame, 
                     customer_col: str = 'customer_id',
                     date_col: str = 'order_date', 
                     amount_col: str = 'amount',
                     analysis_date: datetime = None) -> pd.DataFrame:
        """RFM 값 계산"""
        
        if analysis_date is None:
            analysis_date = transactions_df[date_col].max()
        
        # Recency: 마지막 구매 이후 경과 일수
        recency = transactions_df.groupby(customer_col)[date_col].max().reset_index()
        recency['recency'] = (analysis_date - recency[date_col]).dt.days
        
        # Frequency: 구매 빈도
        frequency = transactions_df.groupby(customer_col)[date_col].count().reset_index()
        frequency.columns = [customer_col, 'frequency']
        
        # Monetary: 총 구매 금액
        monetary = transactions_df.groupby(customer_col)[amount_col].sum().reset_index()
        monetary.columns = [customer_col, 'monetary']
        
        # RFM 데이터 병합
        rfm = recency[[customer_col, 'recency']].merge(
            frequency, on=customer_col
        ).merge(monetary, on=customer_col)
        
        # RFM 점수 계산 (1-5 스케일)
        rfm['r_score'] = pd.qcut(rfm['recency'].rank(method='first'), 5, labels=[5,4,3,2,1])
        rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
        rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), 5, labels=[1,2,3,4,5])
        
        # RFM 통합 점수
        rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
        
        self.rfm_data = rfm
        return rfm
    
    def segment_customers(self, rfm_df: pd.DataFrame = None) -> pd.DataFrame:
        """고객 세분화"""
        if rfm_df is None:
            rfm_df = self.rfm_data
        
        # 세분화 규칙 정의
        def assign_segment(row):
            r, f, m = int(row['r_score']), int(row['f_score']), int(row['m_score'])
            
            # Champions: 최고 고객
            if r >= 4 and f >= 4 and m >= 4:
                return 'Champions'
            
            # Loyal Customers: 충성 고객
            elif r >= 3 and f >= 3 and m >= 3:
                return 'Loyal Customers'
            
            # Potential Loyalists: 잠재 충성 고객
            elif r >= 3 and f >= 2 and m >= 2:
                return 'Potential Loyalists'
            
            # New Customers: 신규 고객 (높은 Recency, 낮은 Frequency)
            elif r >= 4 and f <= 2:
                return 'New Customers'
            
            # Promising: 유망 고객
            elif r >= 3 and f >= 2 and m <= 2:
                return 'Promising'
            
            # Need Attention: 관심 필요
            elif r >= 3 and f <= 2 and m <= 2:
                return 'Need Attention'
            
            # About to Sleep: 잠들 위험
            elif r == 2 and f >= 2:
                return 'About to Sleep'
            
            # At Risk: 위험 고객
            elif r <= 2 and f >= 3 and m >= 3:
                return 'At Risk'
            
            # Cannot Lose Them: 잃으면 안 되는 고객
            elif r <= 2 and f >= 4 and m >= 4:
                return 'Cannot Lose Them'
            
            # Hibernating: 휴면 고객
            elif r <= 2 and f <= 2 and m >= 2:
                return 'Hibernating'
            
            # Lost: 이탈 고객
            else:
                return 'Lost'
        
        rfm_df['segment'] = rfm_df.apply(assign_segment, axis=1)
        self.segments = rfm_df
        return rfm_df
    
    def get_segment_analysis(self) -> Dict:
        """세그먼트 분석"""
        if self.segments is None:
            raise ValueError("먼저 segment_customers()를 실행하세요.")
        
        segment_analysis = self.segments.groupby('segment').agg({
            'customer_id': 'count',
            'recency': 'mean',
            'frequency': 'mean', 
            'monetary': 'mean'
        }).round(2)
        
        segment_analysis.columns = ['customer_count', 'avg_recency', 'avg_frequency', 'avg_monetary']
        segment_analysis['percentage'] = (segment_analysis['customer_count'] / 
                                        segment_analysis['customer_count'].sum() * 100).round(2)
        
        return segment_analysis.to_dict('index')
    
    def visualize_rfm_distribution(self):
        """RFM 분포 시각화"""
        if self.rfm_data is None:
            raise ValueError("먼저 calculate_rfm()을 실행하세요.")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Recency 분포
        axes[0,0].hist(self.rfm_data['recency'], bins=50, alpha=0.7, color='skyblue')
        axes[0,0].set_title('Recency Distribution')
        axes[0,0].set_xlabel('Days Since Last Purchase')
        axes[0,0].set_ylabel('Number of Customers')
        
        # Frequency 분포
        axes[0,1].hist(self.rfm_data['frequency'], bins=50, alpha=0.7, color='lightgreen')
        axes[0,1].set_title('Frequency Distribution')
        axes[0,1].set_xlabel('Number of Purchases')
        axes[0,1].set_ylabel('Number of Customers')
        
        # Monetary 분포
        axes[1,0].hist(self.rfm_data['monetary'], bins=50, alpha=0.7, color='salmon')
        axes[1,0].set_title('Monetary Distribution')
        axes[1,0].set_xlabel('Total Purchase Amount')
        axes[1,0].set_ylabel('Number of Customers')
        
        # RFM 상관관계
        correlation_data = self.rfm_data[['recency', 'frequency', 'monetary']].corr()
        sns.heatmap(correlation_data, annot=True, cmap='coolwarm', center=0, ax=axes[1,1])
        axes[1,1].set_title('RFM Correlation Matrix')
        
        plt.tight_layout()
        plt.show()
    
    def create_rfm_3d_plot(self):
        """3D RFM 시각화"""
        if self.segments is None:
            raise ValueError("먼저 segment_customers()를 실행하세요.")
        
        fig = go.Figure(data=[go.Scatter3d(
            x=self.segments['recency'],
            y=self.segments['frequency'], 
            z=self.segments['monetary'],
            mode='markers',
            marker=dict(
                size=5,
                color=self.segments['segment'].astype('category').cat.codes,
                colorscale='Viridis',
                showscale=True
            ),
            text=self.segments['segment'],
            hovertemplate='<b>%{text}</b><br>' +
                         'Recency: %{x}<br>' +
                         'Frequency: %{y}<br>' +
                         'Monetary: %{z}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            title='3D RFM Customer Segmentation',
            scene=dict(
                xaxis_title='Recency (Days)',
                yaxis_title='Frequency (Count)',
                zaxis_title='Monetary (Amount)'
            ),
            height=700
        )
        
        return fig

class AdvancedSegmentation:
    """고급 세분화 기법"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans = None
        self.features = None
        
    def prepare_features(self, customer_df: pd.DataFrame) -> pd.DataFrame:
        """특성 준비"""
        features = customer_df.copy()
        
        # 파생 변수 생성
        features['avg_order_value'] = features['monetary'] / features['frequency']
        features['recency_log'] = np.log1p(features['recency'])
        features['monetary_log'] = np.log1p(features['monetary'])
        
        # 계절성 특성 (마지막 구매 월)
        if 'last_purchase_date' in features.columns:
            features['last_purchase_month'] = pd.to_datetime(features['last_purchase_date']).dt.month
            features['last_purchase_quarter'] = pd.to_datetime(features['last_purchase_date']).dt.quarter
        
        # 구매 패턴 특성
        features['purchase_consistency'] = features['frequency'] / (features['recency'] / 30 + 1)
        
        return features
    
    def find_optimal_clusters(self, features_df: pd.DataFrame, 
                            max_clusters: int = 10) -> Dict:
        """최적 클러스터 수 찾기"""
        # 수치형 특성만 선택
        numeric_features = features_df.select_dtypes(include=[np.number])
        
        # 표준화
        scaled_features = self.scaler.fit_transform(numeric_features)
        
        # Elbow Method
        inertias = []
        silhouette_scores = []
        
        from sklearn.metrics import silhouette_score
        
        K_range = range(2, max_clusters + 1)
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(scaled_features)
            
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(scaled_features, kmeans.labels_))
        
        # 최적 클러스터 수 추천 (실루엣 점수 기준)
        optimal_k = K_range[np.argmax(silhouette_scores)]
        
        return {
            'k_range': list(K_range),
            'inertias': inertias,
            'silhouette_scores': silhouette_scores,
            'optimal_k': optimal_k
        }
    
    def perform_clustering(self, features_df: pd.DataFrame, 
                         n_clusters: int = None) -> pd.DataFrame:
        """K-means 클러스터링 수행"""
        # 수치형 특성만 선택
        numeric_features = features_df.select_dtypes(include=[np.number])
        self.features = numeric_features.columns.tolist()
        
        # 표준화
        scaled_features = self.scaler.fit_transform(numeric_features)
        
        # 최적 클러스터 수 자동 결정
        if n_clusters is None:
            cluster_analysis = self.find_optimal_clusters(features_df)
            n_clusters = cluster_analysis['optimal_k']
        
        # K-means 클러스터링
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = self.kmeans.fit_predict(scaled_features)
        
        # 결과 DataFrame 생성
        result_df = features_df.copy()
        result_df['cluster'] = clusters
        
        return result_df
    
    def analyze_clusters(self, clustered_df: pd.DataFrame) -> Dict:
        """클러스터 분석"""
        cluster_analysis = {}
        
        for cluster_id in sorted(clustered_df['cluster'].unique()):
            cluster_data = clustered_df[clustered_df['cluster'] == cluster_id]
            
            # 기본 통계
            stats = {}
            for feature in self.features:
                if feature in cluster_data.columns:
                    stats[feature] = {
                        'mean': cluster_data[feature].mean(),
                        'median': cluster_data[feature].median(),
                        'std': cluster_data[feature].std()
                    }
            
            cluster_analysis[f'Cluster_{cluster_id}'] = {
                'size': len(cluster_data),
                'percentage': len(cluster_data) / len(clustered_df) * 100,
                'statistics': stats
            }
        
        return cluster_analysis
    
    def create_cluster_profiles(self, clustered_df: pd.DataFrame) -> Dict:
        """클러스터 프로필 생성"""
        profiles = {}
        
        cluster_means = clustered_df.groupby('cluster')[self.features].mean()
        overall_means = clustered_df[self.features].mean()
        
        for cluster_id in sorted(clustered_df['cluster'].unique()):
            cluster_mean = cluster_means.loc[cluster_id]
            
            # 전체 평균 대비 차이 계산
            profile = {}
            for feature in self.features:
                ratio = cluster_mean[feature] / overall_means[feature]
                
                if ratio > 1.5:
                    profile[feature] = 'Very High'
                elif ratio > 1.2:
                    profile[feature] = 'High'
                elif ratio > 0.8:
                    profile[feature] = 'Average'
                elif ratio > 0.5:
                    profile[feature] = 'Low'
                else:
                    profile[feature] = 'Very Low'
            
            # 클러스터 특성화
            if profile.get('monetary', 'Average') in ['High', 'Very High'] and \
               profile.get('frequency', 'Average') in ['High', 'Very High']:
                cluster_name = 'VIP Customers'
            elif profile.get('recency', 'Average') in ['Very Low', 'Low']:
                cluster_name = 'Active Customers'
            elif profile.get('recency', 'Average') in ['High', 'Very High']:
                cluster_name = 'Inactive Customers'
            elif profile.get('frequency', 'Average') == 'Very Low':
                cluster_name = 'One-time Customers'
            else:
                cluster_name = f'Cluster_{cluster_id}'
            
            profiles[cluster_name] = {
                'cluster_id': cluster_id,
                'profile': profile,
                'size': len(clustered_df[clustered_df['cluster'] == cluster_id])
            }
        
        return profiles

class CustomerLifetimeValue:
    """고객 생애 가치 예측"""
    
    def __init__(self):
        self.model = None
        
    def calculate_historical_ltv(self, transactions_df: pd.DataFrame,
                               customer_col: str = 'customer_id',
                               date_col: str = 'order_date',
                               amount_col: str = 'amount') -> pd.DataFrame:
        """과거 LTV 계산"""
        
        # 고객별 집계
        customer_summary = transactions_df.groupby(customer_col).agg({
            amount_col: ['sum', 'mean', 'count'],
            date_col: ['min', 'max']
        }).round(2)
        
        customer_summary.columns = ['total_revenue', 'avg_order_value', 'frequency', 
                                  'first_purchase', 'last_purchase']
        
        # 고객 생애 기간 계산 (일)
        customer_summary['lifespan_days'] = (
            customer_summary['last_purchase'] - customer_summary['first_purchase']
        ).dt.days + 1
        
        # 구매 주기 계산
        customer_summary['avg_days_between_purchases'] = (
            customer_summary['lifespan_days'] / customer_summary['frequency']
        )
        
        # Historical LTV
        customer_summary['historical_ltv'] = customer_summary['total_revenue']
        
        return customer_summary.reset_index()
    
    def predict_future_ltv(self, customer_summary: pd.DataFrame,
                          prediction_period_days: int = 365) -> pd.DataFrame:
        """미래 LTV 예측"""
        
        # 간단한 휴리스틱 모델
        def predict_ltv(row):
            if row['frequency'] <= 1:
                # 일회성 고객
                return row['avg_order_value'] * 0.1
            
            # 평균 구매 주기로 예측 기간 내 예상 구매 횟수 계산
            if row['avg_days_between_purchases'] > 0:
                predicted_purchases = prediction_period_days / row['avg_days_between_purchases']
                
                # 이탈률 고려 (시간이 지날수록 구매 확률 감소)
                decay_factor = np.exp(-prediction_period_days / 365)  # 1년 기준 감쇠
                predicted_purchases *= decay_factor
                
                return row['avg_order_value'] * predicted_purchases
            
            return 0
        
        customer_summary['predicted_ltv'] = customer_summary.apply(predict_ltv, axis=1)
        customer_summary['total_predicted_ltv'] = (
            customer_summary['historical_ltv'] + customer_summary['predicted_ltv']
        )
        
        return customer_summary
    
    def segment_by_ltv(self, customer_ltv: pd.DataFrame) -> pd.DataFrame:
        """LTV 기반 세분화"""
        
        # LTV 분위수 계산
        customer_ltv['ltv_quartile'] = pd.qcut(
            customer_ltv['total_predicted_ltv'], 
            q=4, 
            labels=['Low Value', 'Medium Value', 'High Value', 'Top Value']
        )
        
        # LTV 세그먼트별 특성
        ltv_segments = customer_ltv.groupby('ltv_quartile').agg({
            'customer_id': 'count',
            'total_predicted_ltv': ['mean', 'median', 'sum'],
            'frequency': 'mean',
            'avg_order_value': 'mean'
        }).round(2)
        
        return customer_ltv, ltv_segments

class PersonalizationEngine:
    """개인화 엔진"""
    
    def __init__(self):
        self.segment_strategies = {
            'Champions': {
                'message': '프리미엄 고객 전용 혜택을 준비했습니다',
                'channel': ['email', 'sms', 'push'],
                'frequency': 'weekly',
                'discount': 0,
                'product_recommendation': 'premium'
            },
            'Loyal Customers': {
                'message': '충성 고객님을 위한 특별 할인',
                'channel': ['email', 'push'],
                'frequency': 'bi-weekly',
                'discount': 10,
                'product_recommendation': 'cross_sell'
            },
            'Potential Loyalists': {
                'message': '회원 등급 업그레이드 기회!',
                'channel': ['email'],
                'frequency': 'monthly',
                'discount': 15,
                'product_recommendation': 'up_sell'
            },
            'At Risk': {
                'message': '돌아오세요! 특별 혜택을 드립니다',
                'channel': ['email', 'sms'],
                'frequency': 'weekly',
                'discount': 20,
                'product_recommendation': 'win_back'
            },
            'Lost': {
                'message': '그동안 감사했습니다. 마지막 기회를 드립니다',
                'channel': ['email'],
                'frequency': 'monthly',
                'discount': 25,
                'product_recommendation': 'reactivation'
            }
        }
    
    def generate_campaign_strategy(self, segment_analysis: Dict) -> Dict:
        """세그먼트별 캠페인 전략 생성"""
        campaign_strategies = {}
        
        for segment, data in segment_analysis.items():
            if segment in self.segment_strategies:
                strategy = self.segment_strategies[segment].copy()
                strategy['segment_size'] = data['customer_count']
                strategy['expected_response_rate'] = self._estimate_response_rate(segment)
                strategy['priority'] = self._calculate_priority(segment, data)
                
                campaign_strategies[segment] = strategy
        
        return campaign_strategies
    
    def _estimate_response_rate(self, segment: str) -> float:
        """세그먼트별 예상 반응률"""
        response_rates = {
            'Champions': 0.25,
            'Loyal Customers': 0.20,
            'Potential Loyalists': 0.15,
            'New Customers': 0.12,
            'At Risk': 0.08,
            'Lost': 0.03
        }
        return response_rates.get(segment, 0.10)
    
    def _calculate_priority(self, segment: str, data: Dict) -> int:
        """세그먼트 우선순위 계산"""
        priority_weights = {
            'Champions': 10,
            'Cannot Lose Them': 9,
            'At Risk': 8,
            'Loyal Customers': 7,
            'Potential Loyalists': 6,
            'Need Attention': 5,
            'About to Sleep': 4,
            'New Customers': 3,
            'Promising': 2,
            'Lost': 1
        }
        
        base_priority = priority_weights.get(segment, 5)
        # 세그먼트 크기에 따른 조정
        size_factor = min(data['customer_count'] / 1000, 2)  # 최대 2배
        
        return int(base_priority * (1 + size_factor))

# 사용 예시
def example_customer_segmentation():
    """고객 세분화 예시"""
    # 샘플 데이터 생성
    np.random.seed(42)
    
    # 거래 데이터 생성
    customers = [f'C{i:05d}' for i in range(1, 1001)]
    transactions = []
    
    for customer in customers:
        # 고객별 거래 패턴 생성
        n_transactions = np.random.poisson(5) + 1
        first_date = pd.Timestamp('2023-01-01') + pd.Timedelta(days=np.random.randint(0, 200))
        
        for i in range(n_transactions):
            transaction_date = first_date + pd.Timedelta(days=np.random.randint(0, 300))
            amount = np.random.lognormal(4, 1)  # 평균 약 54, 다양한 분포
            
            transactions.append({
                'customer_id': customer,
                'order_date': transaction_date,
                'amount': amount
            })
    
    transactions_df = pd.DataFrame(transactions)
    
    # RFM 분석 실행
    rfm_analyzer = RFMAnalyzer()
    rfm_data = rfm_analyzer.calculate_rfm(transactions_df)
    segmented_data = rfm_analyzer.segment_customers()
    segment_analysis = rfm_analyzer.get_segment_analysis()
    
    # 고급 세분화
    advanced_seg = AdvancedSegmentation()
    clustered_data = advanced_seg.perform_clustering(rfm_data, n_clusters=5)
    cluster_profiles = advanced_seg.create_cluster_profiles(clustered_data)
    
    # LTV 분석
    ltv_analyzer = CustomerLifetimeValue()
    customer_summary = ltv_analyzer.calculate_historical_ltv(transactions_df)
    customer_ltv = ltv_analyzer.predict_future_ltv(customer_summary)
    
    # 개인화 전략
    personalization = PersonalizationEngine()
    campaign_strategies = personalization.generate_campaign_strategy(segment_analysis)
    
    return {
        'rfm_analysis': segment_analysis,
        'cluster_profiles': cluster_profiles,
        'ltv_segments': customer_ltv.head(10),
        'campaign_strategies': campaign_strategies
    }

if __name__ == "__main__":
    results = example_customer_segmentation()
    print("고객 세분화 분석 완료!")
```

## 🚀 프로젝트
1. **RFM 기반 고객 세분화 시스템**
2. **머신러닝 클러스터링 모델**
3. **고객 생애 가치 예측 엔진**
4. **개인화 마케팅 캠페인 플랫폼**