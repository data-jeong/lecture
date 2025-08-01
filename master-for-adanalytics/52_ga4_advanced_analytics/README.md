# 52. GA4 Advanced Analytics - GA4 고급 분석

## 📚 과정 소개
Google Analytics 4의 고급 기능을 활용한 심층 분석 기법을 마스터합니다. BigQuery 연동부터 머신러닝 기반 예측까지 GA4의 모든 것을 다룹니다.

## 🎯 학습 목표
- GA4 Measurement Protocol 완벽 이해
- BigQuery Export 데이터 고급 분석
- 서버사이드 태깅 구현
- 머신러닝 기반 예측 분석

## 📖 커리큘럼

### Chapter 01: GA4 Measurement Protocol
```python
import requests
import json
import time
import hashlib

class GA4MeasurementProtocol:
    """GA4 Measurement Protocol 구현"""
    
    def __init__(self, api_secret, measurement_id):
        self.api_secret = api_secret
        self.measurement_id = measurement_id
        self.endpoint = "https://www.google-analytics.com/mp/collect"
        
    def generate_client_id(self, user_id=None):
        """클라이언트 ID 생성"""
        if user_id:
            return hashlib.md5(user_id.encode()).hexdigest()
        return f"{int(time.time())}.{int(time.time() * 1000000) % 1000000}"
    
    def send_event(self, client_id, events, user_id=None, user_properties=None):
        """이벤트 전송"""
        payload = {
            "client_id": client_id,
            "events": events
        }
        
        if user_id:
            payload["user_id"] = user_id
            
        if user_properties:
            payload["user_properties"] = user_properties
        
        params = {
            "api_secret": self.api_secret,
            "measurement_id": self.measurement_id
        }
        
        response = requests.post(
            self.endpoint,
            params=params,
            json=payload
        )
        
        return response.status_code == 204
    
    def track_purchase(self, client_id, transaction_id, value, currency="KRW", items=None):
        """구매 이벤트 추적"""
        event = {
            "name": "purchase",
            "params": {
                "transaction_id": transaction_id,
                "value": value,
                "currency": currency,
                "items": items or []
            }
        }
        
        return self.send_event(client_id, [event])
    
    def track_custom_conversion(self, client_id, conversion_name, value=None, custom_params=None):
        """커스텀 전환 추적"""
        event = {
            "name": conversion_name,
            "params": {
                "value": value,
                "conversion": True
            }
        }
        
        if custom_params:
            event["params"].update(custom_params)
            
        return self.send_event(client_id, [event])

# 사용 예시
ga4 = GA4MeasurementProtocol("YOUR_API_SECRET", "YOUR_MEASUREMENT_ID")

# 서버사이드 구매 추적
client_id = ga4.generate_client_id("user123")
ga4.track_purchase(
    client_id=client_id,
    transaction_id="TRX_12345",
    value=150000,
    items=[{
        "item_id": "SKU_001",
        "item_name": "광고 패키지 A",
        "quantity": 1,
        "price": 150000
    }]
)
```

### Chapter 02: Enhanced Ecommerce GA4
- 상품 노출, 클릭, 구매 추적
- 프로모션 성과 측정
- 환불 및 취소 처리

### Chapter 03-04: Custom Dimensions & Metrics
- 맞춤 측정기준 설계
- 사용자 속성 활용
- 이벤트 파라미터 최적화

### Chapter 05: Audience Builder Advanced
- 예측 잠재고객 생성
- 시퀀스 기반 세그먼트
- 동적 리마케팅 목록

### Chapter 06-07: Exploration Reports
- 유입경로 탐색 분석
- 세그먼트 중첩 분석
- 코호트 탐색

### Chapter 08: Attribution Modeling GA4
- 데이터 기반 어트리뷰션
- 맞춤 어트리뷰션 모델
- 교차 채널 분석

### Chapter 09: GA4 BigQuery Export
```python
from google.cloud import bigquery
import pandas as pd

class GA4BigQueryAnalyzer:
    """GA4 BigQuery 데이터 분석"""
    
    def __init__(self, project_id, dataset_id):
        self.client = bigquery.Client(project=project_id)
        self.dataset_id = dataset_id
        
    def get_daily_active_users(self, start_date, end_date):
        """일별 활성 사용자 분석"""
        query = f"""
        SELECT
            event_date,
            COUNT(DISTINCT user_pseudo_id) as daily_active_users,
            COUNT(DISTINCT user_id) as daily_logged_in_users
        FROM
            `{self.dataset_id}.events_*`
        WHERE
            _TABLE_SUFFIX BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY
            event_date
        ORDER BY
            event_date
        """
        
        return self.client.query(query).to_dataframe()
    
    def analyze_user_journey(self, user_id):
        """사용자 여정 분석"""
        query = f"""
        WITH user_events AS (
            SELECT
                event_timestamp,
                event_name,
                event_params,
                user_properties,
                device,
                geo,
                traffic_source
            FROM
                `{self.dataset_id}.events_*`
            WHERE
                user_id = '{user_id}'
            ORDER BY
                event_timestamp
        )
        SELECT
            TIMESTAMP_MICROS(event_timestamp) as event_time,
            event_name,
            (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_location') as page,
            device.category as device_category,
            geo.country as country,
            traffic_source.source as traffic_source
        FROM
            user_events
        """
        
        return self.client.query(query).to_dataframe()
    
    def calculate_ltv_segments(self):
        """LTV 기반 사용자 세분화"""
        query = f"""
        WITH user_ltv AS (
            SELECT
                user_id,
                SUM(ecommerce.purchase_revenue) as total_ltv,
                COUNT(DISTINCT event_date) as active_days,
                MIN(PARSE_DATE('%Y%m%d', event_date)) as first_seen,
                MAX(PARSE_DATE('%Y%m%d', event_date)) as last_seen
            FROM
                `{self.dataset_id}.events_*`
            WHERE
                user_id IS NOT NULL
            GROUP BY
                user_id
        )
        SELECT
            CASE
                WHEN total_ltv >= 1000000 THEN 'VIP'
                WHEN total_ltv >= 500000 THEN 'High Value'
                WHEN total_ltv >= 100000 THEN 'Medium Value'
                ELSE 'Low Value'
            END as ltv_segment,
            COUNT(*) as user_count,
            AVG(total_ltv) as avg_ltv,
            AVG(active_days) as avg_active_days
        FROM
            user_ltv
        GROUP BY
            ltv_segment
        ORDER BY
            avg_ltv DESC
        """
        
        return self.client.query(query).to_dataframe()
```

### Chapter 10-11: Custom Events & Conversions
- 맞춤 이벤트 설계
- 전환 추적 최적화
- 이벤트 검증 및 디버깅

### Chapter 12: Server-side Tagging
- Google Tag Manager 서버 컨테이너
- 서버사이드 추적 구현
- 데이터 프라이버시 강화

### Chapter 13: Consent Mode Implementation
- 동의 모드 구현
- 쿠키리스 측정
- 데이터 모델링

### Chapter 14-15: Data Stream Configuration
- 크로스플랫폼 추적
- 앱+웹 통합 분석
- 데이터 필터링

### Chapter 16: Debug View Advanced
- 실시간 디버깅
- 이벤트 검증
- 문제 해결

### Chapter 17: Real-time Reports
- 실시간 대시보드
- 라이브 캠페인 모니터링
- 즉각적 인사이트

### Chapter 18: Cohort & Funnel Analysis
- 고급 코호트 분석
- 다단계 퍼널 최적화
- 이탈 지점 분석

### Chapter 19: Path Analysis
- 사용자 경로 분석
- 주요 전환 경로 발견
- 경로 최적화

### Chapter 20: GA4 API Integration
```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

class GA4APIClient:
    """GA4 Data API 클라이언트"""
    
    def __init__(self, property_id):
        self.property_id = property_id
        self.client = BetaAnalyticsDataClient()
        
    def get_campaign_performance(self, start_date, end_date):
        """캠페인 성과 데이터 조회"""
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[
                Dimension(name="campaignName"),
                Dimension(name="sourceMedium"),
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="newUsers"),
                Metric(name="screenPageViews"),
                Metric(name="conversions"),
                Metric(name="purchaseRevenue"),
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        )
        
        response = self.client.run_report(request)
        
        # 데이터프레임으로 변환
        data = []
        for row in response.rows:
            data.append({
                'campaign': row.dimension_values[0].value,
                'source_medium': row.dimension_values[1].value,
                'sessions': int(row.metric_values[0].value),
                'users': int(row.metric_values[1].value),
                'new_users': int(row.metric_values[2].value),
                'pageviews': int(row.metric_values[3].value),
                'conversions': int(row.metric_values[4].value),
                'revenue': float(row.metric_values[5].value),
            })
            
        return pd.DataFrame(data)
    
    def create_custom_report(self, dimensions, metrics, filters=None):
        """맞춤 보고서 생성"""
        # 동적 보고서 생성 로직
        pass
```

## 🚀 핵심 프로젝트
1. **서버사이드 추적 시스템 구축**
2. **GA4 + BigQuery 통합 분석 플랫폼**
3. **실시간 마케팅 대시보드**
4. **예측 분석 기반 자동화 시스템**

## 💡 실전 팁
- BigQuery 비용 최적화 전략
- 데이터 샘플링 회피 방법
- 맞춤 채널 그룹 설정
- 향상된 측정 활용법

---

다음: [Chapter 01: GA4 Measurement Protocol →](01_ga4_measurement_protocol/README.md)