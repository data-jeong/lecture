# 51. MMP (Mobile Measurement Partners) - 모바일 측정 파트너

## 📚 과정 소개
AppsFlyer, Adjust, Branch 등 주요 MMP 플랫폼을 활용한 모바일 광고 성과 측정 및 어트리뷰션을 마스터합니다.

## 🎯 학습 목표
- MMP 플랫폼별 특징 이해
- 모바일 어트리뷰션 구현
- 사기 방지 및 검증
- iOS 14+ (SKAdNetwork) 대응

## 📖 주요 내용

### AppsFlyer 통합 구현
```python
import requests
import hashlib
import json
from datetime import datetime, timedelta

class AppsFlyerClient:
    """AppsFlyer API 클라이언트"""
    
    def __init__(self, dev_key, api_token):
        self.dev_key = dev_key
        self.api_token = api_token
        self.base_url = "https://api2.appsflyer.com"
        
    def get_install_attribution(self, app_id, date_from, date_to):
        """설치 어트리뷰션 데이터 조회"""
        url = f"{self.base_url}/export/{app_id}/installs_report/v5"
        
        headers = {
            "authorization": self.api_token
        }
        
        params = {
            "from": date_from,
            "to": date_to,
            "timezone": "Asia/Seoul"
        }
        
        response = requests.get(url, headers=headers, params=params)
        return self._parse_csv_response(response.text)
    
    def get_in_app_events(self, app_id, date_from, date_to):
        """인앱 이벤트 데이터 조회"""
        url = f"{self.base_url}/export/{app_id}/in_app_events_report/v5"
        
        headers = {
            "authorization": self.api_token
        }
        
        params = {
            "from": date_from,
            "to": date_to,
            "timezone": "Asia/Seoul"
        }
        
        response = requests.get(url, headers=headers, params=params)
        return self._parse_csv_response(response.text)
    
    def send_server_to_server_event(self, app_id, customer_user_id, event_name, event_value=None):
        """S2S 이벤트 전송"""
        url = f"{self.base_url}/inappevent/{app_id}"
        
        # 이벤트 데이터 구성
        event_data = {
            "customer_user_id": customer_user_id,
            "eventName": event_name,
            "eventTime": datetime.utcnow().isoformat(),
            "eventCurrency": "KRW"
        }
        
        if event_value:
            event_data["eventValue"] = json.dumps(event_value)
        
        # 서명 생성
        event_data["af_sig"] = self._generate_signature(event_data)
        
        response = requests.post(url, json=event_data)
        return response.status_code == 200
    
    def _generate_signature(self, data):
        """HMAC 서명 생성"""
        # 실제 구현은 AppsFlyer 문서 참조
        pass
```

### Adjust 고급 기능
```python
class AdjustAnalytics:
    """Adjust 분석 클라이언트"""
    
    def __init__(self, app_token, environment='production'):
        self.app_token = app_token
        self.environment = environment
        self.kpi_url = "https://api.adjust.com/kpis/v1"
        
    def get_cohort_analysis(self, date_from, date_to, kpis=['retention_rate']):
        """코호트 분석 데이터"""
        params = {
            'app_token': self.app_token,
            'start_date': date_from,
            'end_date': date_to,
            'kpis': ','.join(kpis),
            'grouping': 'day',
            'cohort_period': 'day'
        }
        
        response = requests.get(f"{self.kpi_url}/cohorts", params=params)
        return response.json()
    
    def get_fraud_prevention_data(self):
        """사기 방지 데이터 조회"""
        fraud_url = f"https://api.adjust.com/fraud_prevention/v1/{self.app_token}"
        
        response = requests.get(fraud_url, headers=self._get_headers())
        return response.json()
    
    def track_revenue_event(self, adjust_id, revenue, currency='KRW'):
        """수익 이벤트 추적"""
        event_data = {
            'adjust_id': adjust_id,
            'revenue': revenue,
            'currency': currency,
            'environment': self.environment,
            'callback_params': {
                'product_id': 'premium_subscription',
                'payment_method': 'credit_card'
            }
        }
        
        # S2S 엔드포인트로 전송
        response = requests.post(
            "https://s2s.adjust.com/revenue",
            json=event_data,
            headers=self._get_headers()
        )
        
        return response.status_code == 200
```

### SKAdNetwork 구현
```python
class SKAdNetworkManager:
    """iOS 14+ SKAdNetwork 관리"""
    
    def __init__(self):
        self.conversion_values = self._setup_conversion_schema()
        
    def _setup_conversion_schema(self):
        """전환 값 스키마 설정"""
        return {
            0: {'event': 'install', 'revenue': 0},
            1: {'event': 'registration', 'revenue': 0},
            2: {'event': 'trial_start', 'revenue': 0},
            3: {'event': 'purchase_small', 'revenue': (1000, 5000)},
            4: {'event': 'purchase_medium', 'revenue': (5000, 20000)},
            5: {'event': 'purchase_large', 'revenue': (20000, 100000)},
            # ... 최대 63까지
        }
    
    def calculate_conversion_value(self, user_events):
        """사용자 이벤트 기반 전환 값 계산"""
        value = 0
        total_revenue = 0
        
        for event in user_events:
            if event['name'] == 'registration':
                value = max(value, 1)
            elif event['name'] == 'trial_start':
                value = max(value, 2)
            elif event['name'] == 'purchase':
                total_revenue += event['revenue']
                
        # 수익 기반 값 설정
        if total_revenue > 0:
            if total_revenue < 5000:
                value = max(value, 3)
            elif total_revenue < 20000:
                value = max(value, 4)
            else:
                value = max(value, 5)
                
        return value
    
    def update_conversion_value(self, new_value):
        """전환 값 업데이트 (24시간 타이머 리셋)"""
        # iOS SDK 호출
        # SKAdNetwork.updateConversionValue(new_value)
        pass
```

### 통합 대시보드
```python
class MMPUnifiedDashboard:
    """MMP 통합 대시보드"""
    
    def __init__(self):
        self.appsflyer = AppsFlyerClient(dev_key, api_token)
        self.adjust = AdjustAnalytics(app_token)
        self.branch = BranchClient(branch_key)
        
    async def get_unified_metrics(self, date_from, date_to):
        """통합 메트릭 조회"""
        # 병렬로 데이터 수집
        tasks = [
            self.appsflyer.get_install_attribution(app_id, date_from, date_to),
            self.adjust.get_cohort_analysis(date_from, date_to),
            self.branch.get_deep_link_data(date_from, date_to)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # 데이터 통합
        unified_data = self._merge_mmp_data(results)
        
        # 중복 제거 및 검증
        cleaned_data = self._deduplicate_attributions(unified_data)
        
        return cleaned_data
    
    def _deduplicate_attributions(self, data):
        """중복 어트리뷰션 제거"""
        # 설치 ID 기준 중복 제거
        seen_installs = set()
        deduplicated = []
        
        for record in sorted(data, key=lambda x: x['install_time']):
            install_id = record.get('idfa') or record.get('gaid')
            
            if install_id and install_id not in seen_installs:
                seen_installs.add(install_id)
                deduplicated.append(record)
                
        return deduplicated
```

### 고급 분석 기능
1. **멀티터치 어트리뷰션**
2. **LTV 예측 모델링**
3. **사기 탐지 알고리즘**
4. **크로스 플랫폼 분석**

## 🚀 프로젝트
1. **통합 MMP 대시보드**
2. **실시간 사기 탐지 시스템**
3. **iOS 14+ 대응 어트리뷰션**
4. **예측 기반 UA 최적화**