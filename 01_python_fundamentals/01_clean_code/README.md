# Chapter 01: Clean Code - 클린 코드 작성법

## 📚 학습 목표
- PEP 8 스타일 가이드 완벽 이해
- 가독성 높은 코드 작성
- 유지보수 가능한 코드 구조 설계
- 광고 도메인에 특화된 클린 코드 패턴

## 📖 이론: 클린 코드의 원칙

### 1. 명명 규칙 (Naming Conventions)

```python
# ❌ Bad - 의미 없는 변수명
def calc(x, y):
    z = x * y * 0.1
    return z

# ✅ Good - 명확한 변수명
def calculate_advertising_cost(impressions, cpm):
    """
    광고 비용 계산
    impressions: 노출 수
    cpm: 1000회 노출당 비용
    """
    cost = (impressions / 1000) * cpm
    return cost
```

### 2. 함수는 한 가지 일만 해야 한다

```python
# ❌ Bad - 여러 책임을 가진 함수
def process_campaign_data(campaign_id):
    # 데이터 가져오기
    data = fetch_from_db(campaign_id)
    # 검증
    if not data:
        send_email("admin@company.com", "No data")
        return None
    # 계산
    ctr = data['clicks'] / data['impressions']
    # 저장
    save_to_db(campaign_id, ctr)
    # 리포트
    generate_report(campaign_id, ctr)
    return ctr

# ✅ Good - 단일 책임 원칙
def fetch_campaign_data(campaign_id):
    """캠페인 데이터 조회"""
    return fetch_from_db(campaign_id)

def calculate_ctr(clicks, impressions):
    """CTR 계산"""
    if impressions == 0:
        return 0
    return clicks / impressions

def save_campaign_metrics(campaign_id, metrics):
    """캠페인 지표 저장"""
    save_to_db(campaign_id, metrics)
```

### 3. 주석보다는 코드로 설명하라

```python
# ❌ Bad - 주석으로 설명
# 사용자가 18세 이상이고 관심사가 스포츠인 경우
if user.age >= 18 and user.interest == 'sports':
    show_ad('sports_equipment')

# ✅ Good - 의미 있는 함수명
def is_adult_sports_enthusiast(user):
    return user.age >= 18 and user.interest == 'sports'

if is_adult_sports_enthusiast(user):
    show_ad('sports_equipment')
```

## 🛠️ 실습: 광고 캠페인 분석기 리팩토링

### 실습 1: 기본 리팩토링

```python
# Before: 더러운 코드
def analyze(d):
    r = []
    for i in d:
        if i[2] > 0:
            c = i[1] / i[2]
            if c > 0.02:
                r.append({'n': i[0], 'c': c})
    return r

# After: 클린 코드
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Campaign:
    name: str
    clicks: int
    impressions: int
    
    @property
    def ctr(self) -> float:
        """Click-Through Rate 계산"""
        if self.impressions == 0:
            return 0.0
        return self.clicks / self.impressions

def analyze_high_performing_campaigns(
    campaigns: List[Campaign], 
    min_ctr: float = 0.02
) -> List[Dict[str, float]]:
    """
    높은 성과를 보이는 캠페인 분석
    
    Args:
        campaigns: 캠페인 리스트
        min_ctr: 최소 CTR 기준 (기본값: 2%)
    
    Returns:
        높은 성과 캠페인 정보
    """
    high_performers = []
    
    for campaign in campaigns:
        if campaign.impressions > 0 and campaign.ctr > min_ctr:
            high_performers.append({
                'campaign_name': campaign.name,
                'ctr': campaign.ctr
            })
    
    return high_performers
```

### 실습 2: 광고 비용 계산기 클린 코드

```python
# 광고 비용 계산 클래스
class AdCostCalculator:
    """광고 비용 계산기"""
    
    TAX_RATE = 0.1  # 세율 10%
    
    def __init__(self, currency: str = 'KRW'):
        self.currency = currency
        self._exchange_rates = {
            'KRW': 1,
            'USD': 1300,
            'EUR': 1400
        }
    
    def calculate_base_cost(
        self, 
        impressions: int, 
        cpm: float
    ) -> float:
        """기본 광고 비용 계산"""
        return (impressions / 1000) * cpm
    
    def apply_tax(self, base_cost: float) -> float:
        """세금 적용"""
        return base_cost * (1 + self.TAX_RATE)
    
    def convert_currency(
        self, 
        amount: float, 
        from_currency: str, 
        to_currency: str
    ) -> float:
        """환율 변환"""
        if from_currency == to_currency:
            return amount
            
        # KRW 기준으로 변환
        amount_in_krw = amount * self._exchange_rates[from_currency]
        return amount_in_krw / self._exchange_rates[to_currency]
    
    def calculate_total_cost(
        self,
        impressions: int,
        cpm: float,
        apply_tax: bool = True,
        target_currency: str = None
    ) -> Dict[str, float]:
        """총 광고 비용 계산"""
        base_cost = self.calculate_base_cost(impressions, cpm)
        
        if apply_tax:
            total_cost = self.apply_tax(base_cost)
        else:
            total_cost = base_cost
        
        if target_currency and target_currency != self.currency:
            total_cost = self.convert_currency(
                total_cost, 
                self.currency, 
                target_currency
            )
        
        return {
            'base_cost': base_cost,
            'tax': base_cost * self.TAX_RATE if apply_tax else 0,
            'total_cost': total_cost,
            'currency': target_currency or self.currency
        }
```

### 실습 3: 컨텍스트 매니저를 활용한 클린 코드

```python
from contextlib import contextmanager
import logging
from datetime import datetime

@contextmanager
def campaign_performance_logger(campaign_name: str):
    """캠페인 성과 측정 로거"""
    logger = logging.getLogger(__name__)
    start_time = datetime.now()
    
    logger.info(f"캠페인 '{campaign_name}' 분석 시작")
    
    try:
        yield logger
    except Exception as e:
        logger.error(f"캠페인 '{campaign_name}' 분석 중 오류: {str(e)}")
        raise
    finally:
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"캠페인 '{campaign_name}' 분석 완료 (소요시간: {duration:.2f}초)")

# 사용 예시
def analyze_campaign_performance(campaign_data):
    with campaign_performance_logger(campaign_data['name']) as logger:
        # 분석 로직
        ctr = calculate_ctr(
            campaign_data['clicks'], 
            campaign_data['impressions']
        )
        logger.debug(f"CTR 계산 완료: {ctr:.2%}")
        
        roas = calculate_roas(
            campaign_data['revenue'], 
            campaign_data['cost']
        )
        logger.debug(f"ROAS 계산 완료: {roas:.2f}")
        
        return {
            'ctr': ctr,
            'roas': roas
        }
```

## 🚀 프로젝트: 광고 캠페인 분석 시스템

### 프로젝트 구조
```
ad_campaign_analyzer/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── campaign.py
│   └── metrics.py
├── analyzers/
│   ├── __init__.py
│   ├── performance.py
│   └── cost.py
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   └── formatters.py
└── main.py
```

### models/campaign.py
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class CampaignStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

@dataclass
class Campaign:
    """광고 캠페인 모델"""
    id: str
    name: str
    advertiser: str
    budget: float
    status: CampaignStatus = CampaignStatus.DRAFT
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        """캠페인 데이터 검증"""
        if self.budget <= 0:
            raise ValueError("예산은 0보다 커야 합니다")
        
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValueError("종료일은 시작일보다 늦어야 합니다")
    
    @property
    def is_active(self) -> bool:
        """활성 캠페인 여부"""
        if self.status != CampaignStatus.ACTIVE:
            return False
            
        now = datetime.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
            
        return True
    
    @property
    def days_remaining(self) -> Optional[int]:
        """남은 일수"""
        if not self.end_date or not self.is_active:
            return None
        
        delta = self.end_date - datetime.now()
        return max(0, delta.days)
```

### analyzers/performance.py
```python
from typing import Dict, List
from dataclasses import dataclass
import statistics

@dataclass
class PerformanceMetrics:
    """성과 지표"""
    impressions: int
    clicks: int
    conversions: int
    cost: float
    revenue: float
    
    @property
    def ctr(self) -> float:
        """Click-Through Rate"""
        if self.impressions == 0:
            return 0.0
        return self.clicks / self.impressions
    
    @property
    def cvr(self) -> float:
        """Conversion Rate"""
        if self.clicks == 0:
            return 0.0
        return self.conversions / self.clicks
    
    @property
    def cpc(self) -> float:
        """Cost Per Click"""
        if self.clicks == 0:
            return 0.0
        return self.cost / self.clicks
    
    @property
    def cpa(self) -> float:
        """Cost Per Acquisition"""
        if self.conversions == 0:
            return 0.0
        return self.cost / self.conversions
    
    @property
    def roas(self) -> float:
        """Return on Ad Spend"""
        if self.cost == 0:
            return 0.0
        return self.revenue / self.cost


class PerformanceAnalyzer:
    """캠페인 성과 분석기"""
    
    def __init__(self, metrics_history: List[PerformanceMetrics]):
        self.metrics_history = metrics_history
    
    def calculate_average_metrics(self) -> Dict[str, float]:
        """평균 지표 계산"""
        if not self.metrics_history:
            return {}
        
        return {
            'avg_ctr': statistics.mean(m.ctr for m in self.metrics_history),
            'avg_cvr': statistics.mean(m.cvr for m in self.metrics_history),
            'avg_cpc': statistics.mean(m.cpc for m in self.metrics_history),
            'avg_cpa': statistics.mean(m.cpa for m in self.metrics_history),
            'avg_roas': statistics.mean(m.roas for m in self.metrics_history)
        }
    
    def identify_trends(self) -> Dict[str, str]:
        """트렌드 식별"""
        if len(self.metrics_history) < 2:
            return {'status': 'insufficient_data'}
        
        recent_ctr = self.metrics_history[-1].ctr
        previous_ctr = self.metrics_history[-2].ctr
        
        ctr_change = (recent_ctr - previous_ctr) / previous_ctr if previous_ctr > 0 else 0
        
        return {
            'ctr_trend': self._classify_trend(ctr_change),
            'ctr_change_percentage': f"{ctr_change * 100:.1f}%"
        }
    
    @staticmethod
    def _classify_trend(change: float) -> str:
        """트렌드 분류"""
        if change > 0.1:
            return "급상승"
        elif change > 0.05:
            return "상승"
        elif change > -0.05:
            return "안정"
        elif change > -0.1:
            return "하락"
        else:
            return "급하락"
```

## 📝 과제

### 과제 1: 코드 리뷰 체크리스트 작성
다음 항목들을 포함한 코드 리뷰 체크리스트를 작성하세요:
- 명명 규칙
- 함수 크기
- 주석의 적절성
- 에러 처리
- 테스트 가능성

### 과제 2: 레거시 코드 리팩토링
주어진 레거시 광고 분석 코드를 클린 코드 원칙에 따라 리팩토링하세요.

### 과제 3: 클린 코드 적용 프로젝트
실제 광고 데이터를 사용하여 클린 코드 원칙을 적용한 분석 시스템을 구축하세요.

## 🔗 참고 자료
- [PEP 8 - Python 스타일 가이드](https://www.python.org/dev/peps/pep-0008/)
- Clean Code by Robert C. Martin
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

---

다음 장: [Chapter 02: Object-Oriented Programming →](../02_object_oriented/README.md)