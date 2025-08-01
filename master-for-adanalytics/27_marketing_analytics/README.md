# 27. Marketing Analytics - 마케팅 분석 핵심

## 📚 과정 소개
데이터 기반 마케팅의 핵심 분석 기법을 마스터합니다. 고객 분석부터 캠페인 최적화까지 실무에서 바로 활용 가능한 기술을 학습합니다.

## 🎯 학습 목표
- 고객 생애 가치(LTV) 예측 및 최적화
- 정교한 고객 세분화 및 타겟팅
- 마케팅 믹스 모델링(MMM)
- 어트리뷰션 모델링 마스터

## 📖 커리큘럼

### Chapter 01-02: Customer Segmentation
```python
# RFM 분석으로 고객 세분화
class RFMSegmentation:
    def __init__(self, transaction_data):
        self.data = transaction_data
        
    def calculate_rfm(self):
        current_date = pd.Timestamp.now()
        
        rfm = self.data.groupby('customer_id').agg({
            'transaction_date': lambda x: (current_date - x.max()).days,  # Recency
            'transaction_id': 'count',  # Frequency  
            'amount': 'sum'  # Monetary
        })
        
        rfm.columns = ['Recency', 'Frequency', 'Monetary']
        
        # 분위수 기반 점수 부여
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1])
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1,2,3,4,5])
        
        # 세그먼트 생성
        rfm['Segment'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
        
        # 고객 등급 분류
        def classify_customer(row):
            if row['Segment'] in ['555', '554', '544', '545', '454', '455', '445']:
                return 'Champions'
            elif row['Segment'] in ['543', '444', '435', '355', '354', '345', '344', '335']:
                return 'Loyal Customers'
            elif row['Segment'] in ['553', '551', '552', '541', '542', '533', '532', '531', '452', '451']:
                return 'Potential Loyalists'
            elif row['Segment'] in ['512', '511', '422', '421', '412', '411', '311']:
                return 'New Customers'
            elif row['Segment'] in ['525', '524', '523', '522', '521', '515', '514', '513', '425', '424', '413', '414', '415', '315', '314', '313']:
                return 'Promising'
            elif row['Segment'] in ['535', '534', '443', '434', '343', '334', '325', '324']:
                return 'Need Attention'
            elif row['Segment'] in ['331', '321', '312', '221', '213', '231', '241', '251']:
                return 'About to Sleep'
            elif row['Segment'] in ['155', '154', '144', '214', '215', '115', '114', '113']:
                return 'At Risk'
            elif row['Segment'] in ['255', '254', '245', '244', '253', '252', '243', '242', '235', '234', '225', '224', '153', '152', '145']:
                return 'Cannot Lose Them'
            elif row['Segment'] in ['332', '322', '231', '241', '251', '233', '232', '223', '222', '132', '123', '122', '212', '211']:
                return 'Hibernating'
            elif row['Segment'] in ['111', '112', '121', '131', '141', '151']:
                return 'Lost'
            else:
                return 'Others'
                
        rfm['Customer_Type'] = rfm.apply(classify_customer, axis=1)
        return rfm
```

### Chapter 03: Cohort Analysis
- 코호트 리텐션 분석
- 생애주기 패턴 발견
- 채널별 코호트 비교

### Chapter 04: LTV Modeling
- 확률적 LTV 모델
- ML 기반 LTV 예측
- CAC 대비 LTV 최적화

### Chapter 05: Churn Prediction
- 이탈 예측 모델링
- 조기 경고 시스템
- 리텐션 전략 수립

### Chapter 06-07: Attribution Modeling
- Last-click vs Multi-touch
- Data-driven Attribution
- 크로스디바이스 어트리뷰션

### Chapter 08: Campaign Optimization
- A/B 테스트 설계
- 베이지안 최적화
- 다변량 테스트

### Chapter 09: Uplift Modeling
- 처치 효과 측정
- 증분 효과 최적화
- 타겟팅 우선순위

### Chapter 10-11: Price & Market Analysis
- 가격 탄력성 분석
- 경쟁사 모니터링
- 시장 점유율 분석

### Chapter 12-13: Customer Journey
- 터치포인트 매핑
- 경로 분석
- 넥스트 베스트 액션

### Chapter 14-15: Personalization
- 추천 시스템
- 동적 컨텐츠 최적화
- 1:1 마케팅

### Chapter 16-17: Cross-sell/Upsell
- 상품 연관 분석
- 번들 최적화
- 타이밍 예측

### Chapter 18-19: ROI Measurement
- 마케팅 ROI 계산
- 증분 효과 측정
- 예산 배분 최적화

### Chapter 20: Marketing Automation
- 자동화 워크플로우
- 트리거 기반 캠페인
- 성과 모니터링

## 🚀 핵심 프로젝트
1. **통합 고객 분석 플랫폼**
2. **마케팅 믹스 최적화 시스템**
3. **실시간 개인화 엔진**
4. **멀티채널 어트리뷰션 솔루션**

## 💡 실전 예제: 마케팅 믹스 모델링

```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

class MarketingMixModel:
    """마케팅 믹스 모델링 (MMM)"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.adstock_params = {}
        
    def adstock_transformation(self, spend, decay_rate=0.7, max_lag=8):
        """광고 지연 효과 모델링"""
        adstocked = np.zeros_like(spend)
        
        for i in range(len(spend)):
            for lag in range(min(i+1, max_lag)):
                adstocked[i] += spend[i-lag] * (decay_rate ** lag)
                
        return adstocked
    
    def saturation_transformation(self, spend, alpha=2.5):
        """포화 곡선 변환"""
        return spend ** (1/alpha)
    
    def prepare_features(self, data):
        """특성 준비 및 변환"""
        features = pd.DataFrame()
        
        # 각 미디어 채널에 대해 변환 적용
        media_channels = ['tv_spend', 'digital_spend', 'print_spend', 'radio_spend']
        
        for channel in media_channels:
            if channel in data.columns:
                # Adstock 변환
                adstocked = self.adstock_transformation(
                    data[channel].values,
                    decay_rate=self.adstock_params.get(channel, 0.7)
                )
                
                # Saturation 변환
                saturated = self.saturation_transformation(adstocked)
                
                features[f'{channel}_transformed'] = saturated
        
        # 계절성 변수
        features['month'] = pd.to_datetime(data['date']).dt.month
        features['quarter'] = pd.to_datetime(data['date']).dt.quarter
        
        # 프로모션 및 가격
        if 'promo_flag' in data.columns:
            features['promo'] = data['promo_flag']
        if 'avg_price' in data.columns:
            features['price'] = data['avg_price']
            
        # 외부 요인
        if 'competitor_spend' in data.columns:
            features['competition'] = data['competitor_spend']
            
        return features
    
    def fit(self, X, y):
        """모델 학습"""
        # 특성 준비
        X_prepared = self.prepare_features(X)
        
        # 스케일링
        X_scaled = self.scaler.fit_transform(X_prepared)
        
        # OLS 회귀
        X_with_const = sm.add_constant(X_scaled)
        self.model = sm.OLS(y, X_with_const).fit()
        
        return self
    
    def calculate_contribution(self, X):
        """각 채널의 매출 기여도 계산"""
        X_prepared = self.prepare_features(X)
        X_scaled = self.scaler.transform(X_prepared)
        X_with_const = sm.add_constant(X_scaled)
        
        # 예측값
        predictions = self.model.predict(X_with_const)
        
        # 각 변수의 기여도
        contributions = {}
        coef = self.model.params[1:]  # 상수항 제외
        
        for i, col in enumerate(X_prepared.columns):
            contributions[col] = coef[i] * X_scaled[:, i]
            
        # 기여도를 DataFrame으로
        contrib_df = pd.DataFrame(contributions)
        contrib_df['base'] = self.model.params[0]  # 상수항
        contrib_df['total_predicted'] = predictions
        
        return contrib_df
    
    def calculate_roi(self, X, y):
        """각 채널의 ROI 계산"""
        contributions = self.calculate_contribution(X)
        
        roi_results = {}
        media_channels = [col for col in contributions.columns if 'spend' in col]
        
        for channel in media_channels:
            # 원래 채널명 추출
            original_channel = channel.replace('_transformed', '')
            
            if original_channel in X.columns:
                total_spend = X[original_channel].sum()
                total_contribution = contributions[channel].sum()
                
                roi = (total_contribution / total_spend - 1) * 100 if total_spend > 0 else 0
                roi_results[original_channel] = {
                    'spend': total_spend,
                    'contribution': total_contribution,
                    'roi': roi
                }
        
        return roi_results
    
    def optimize_budget(self, total_budget, constraints=None):
        """예산 최적 배분"""
        # 각 채널의 한계 효과 계산
        # 최적화 알고리즘 구현
        pass

# 사용 예시
data = pd.DataFrame({
    'date': pd.date_range('2023-01-01', periods=52, freq='W'),
    'sales': np.random.normal(100000, 20000, 52),
    'tv_spend': np.random.uniform(5000, 20000, 52),
    'digital_spend': np.random.uniform(3000, 15000, 52),
    'print_spend': np.random.uniform(1000, 5000, 52),
    'promo_flag': np.random.binomial(1, 0.3, 52)
})

mmm = MarketingMixModel()
mmm.fit(data[['date', 'tv_spend', 'digital_spend', 'print_spend', 'promo_flag']], 
        data['sales'])

# ROI 분석
roi_results = mmm.calculate_roi(data, data['sales'])
for channel, metrics in roi_results.items():
    print(f"{channel}: ROI = {metrics['roi']:.1f}%")
```

---

다음: [Chapter 01: Customer Segmentation →](01_customer_segmentation/README.md)