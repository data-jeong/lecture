# Chapter 02: Object-Oriented Programming - 객체지향 프로그래밍

## 📚 학습 목표
- 객체지향 프로그래밍의 4대 원칙 이해
- 광고 도메인 모델 설계 능력 향상
- SOLID 원칙을 적용한 확장 가능한 시스템 구축
- 디자인 패턴을 활용한 유연한 아키텍처 설계

## 📖 이론: OOP 핵심 개념

### 1. 캡슐화 (Encapsulation)

```python
# ❌ Bad - 데이터 노출
class Campaign:
    def __init__(self):
        self.budget = 1000000  # 직접 접근 가능
        self.spent = 0

campaign = Campaign()
campaign.budget = -1000  # 잘못된 값 설정 가능

# ✅ Good - 데이터 보호
class Campaign:
    def __init__(self, initial_budget: float):
        self._budget = initial_budget
        self._spent = 0.0
        self._validate_budget()
    
    def _validate_budget(self):
        if self._budget <= 0:
            raise ValueError("예산은 0보다 커야 합니다")
    
    @property
    def budget(self) -> float:
        return self._budget
    
    @property
    def remaining_budget(self) -> float:
        return self._budget - self._spent
    
    def spend(self, amount: float):
        if amount > self.remaining_budget:
            raise ValueError("예산 초과")
        self._spent += amount
```

### 2. 상속 (Inheritance)

```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List

# 기본 광고 클래스
class BaseAd(ABC):
    """모든 광고의 기본 클래스"""
    
    def __init__(self, ad_id: str, title: str, budget: float):
        self.ad_id = ad_id
        self.title = title
        self.budget = budget
        self.impressions = 0
        self.clicks = 0
        self.created_at = datetime.now()
    
    @abstractmethod
    def calculate_cost(self) -> float:
        """광고 비용 계산 (하위 클래스에서 구현)"""
        pass
    
    @abstractmethod
    def get_targeting_params(self) -> Dict:
        """타겟팅 파라미터 반환"""
        pass
    
    @property
    def ctr(self) -> float:
        """Click-Through Rate"""
        if self.impressions == 0:
            return 0.0
        return self.clicks / self.impressions

# 검색 광고
class SearchAd(BaseAd):
    """검색 광고 클래스"""
    
    def __init__(self, ad_id: str, title: str, budget: float, 
                 keywords: List[str], max_cpc: float):
        super().__init__(ad_id, title, budget)
        self.keywords = keywords
        self.max_cpc = max_cpc
    
    def calculate_cost(self) -> float:
        """CPC 기반 비용 계산"""
        return self.clicks * self.max_cpc
    
    def get_targeting_params(self) -> Dict:
        return {
            'type': 'search',
            'keywords': self.keywords,
            'max_cpc': self.max_cpc
        }

# 디스플레이 광고
class DisplayAd(BaseAd):
    """디스플레이 광고 클래스"""
    
    def __init__(self, ad_id: str, title: str, budget: float,
                 audience_segments: List[str], cpm: float):
        super().__init__(ad_id, title, budget)
        self.audience_segments = audience_segments
        self.cpm = cpm
    
    def calculate_cost(self) -> float:
        """CPM 기반 비용 계산"""
        return (self.impressions / 1000) * self.cpm
    
    def get_targeting_params(self) -> Dict:
        return {
            'type': 'display',
            'audience_segments': self.audience_segments,
            'cpm': self.cpm
        }
```

### 3. 다형성 (Polymorphism)

```python
class AdCampaignManager:
    """광고 캠페인 관리자"""
    
    def __init__(self):
        self.ads: List[BaseAd] = []
    
    def add_ad(self, ad: BaseAd):
        """광고 추가 (다형성 활용)"""
        self.ads.append(ad)
    
    def calculate_total_cost(self) -> float:
        """전체 광고 비용 계산"""
        return sum(ad.calculate_cost() for ad in self.ads)
    
    def get_performance_report(self) -> List[Dict]:
        """성과 리포트 생성"""
        report = []
        for ad in self.ads:
            report.append({
                'ad_id': ad.ad_id,
                'title': ad.title,
                'type': ad.__class__.__name__,
                'cost': ad.calculate_cost(),
                'ctr': ad.ctr,
                'targeting': ad.get_targeting_params()
            })
        return report

# 사용 예시
manager = AdCampaignManager()
manager.add_ad(SearchAd("s1", "봄 세일", 1000000, ["봄옷", "세일"], 500))
manager.add_ad(DisplayAd("d1", "브랜드 인지도", 2000000, ["패션관심"], 10000))

total_cost = manager.calculate_total_cost()  # 다형성 활용
```

### 4. 추상화 (Abstraction)

```python
from abc import ABC, abstractmethod
from enum import Enum

class BidStrategy(ABC):
    """입찰 전략 추상 클래스"""
    
    @abstractmethod
    def calculate_bid(self, base_bid: float, 
                     quality_score: float, 
                     competition_level: float) -> float:
        """입찰가 계산"""
        pass

class ConservativeBidStrategy(BidStrategy):
    """보수적 입찰 전략"""
    
    def calculate_bid(self, base_bid: float, 
                     quality_score: float, 
                     competition_level: float) -> float:
        # 경쟁이 심할수록 입찰가를 조금만 올림
        adjustment = 1 + (competition_level * 0.1)
        return base_bid * quality_score * adjustment

class AggressiveBidStrategy(BidStrategy):
    """공격적 입찰 전략"""
    
    def calculate_bid(self, base_bid: float, 
                     quality_score: float, 
                     competition_level: float) -> float:
        # 경쟁이 심할수록 입찰가를 크게 올림
        adjustment = 1 + (competition_level * 0.5)
        return base_bid * quality_score * adjustment

class SmartBidStrategy(BidStrategy):
    """스마트 입찰 전략"""
    
    def calculate_bid(self, base_bid: float, 
                     quality_score: float, 
                     competition_level: float) -> float:
        # 품질 점수가 높으면 입찰가를 낮춤
        if quality_score > 0.8:
            adjustment = 0.9
        elif competition_level > 0.7:
            adjustment = 1.3
        else:
            adjustment = 1.1
        
        return base_bid * quality_score * adjustment
```

## 🛠️ 실습: 광고 시스템 설계

### 실습 1: 광고 계층 구조 설계

```python
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import uuid

class AdAccount:
    """광고 계정"""
    
    def __init__(self, account_id: str, name: str, 
                 currency: str = 'KRW'):
        self._account_id = account_id
        self._name = name
        self._currency = currency
        self._balance = 0.0
        self._campaigns: List['Campaign'] = []
        self._created_at = datetime.now()
    
    def add_balance(self, amount: float):
        """잔액 추가"""
        if amount <= 0:
            raise ValueError("추가 금액은 0보다 커야 합니다")
        self._balance += amount
    
    def create_campaign(self, name: str, budget: float) -> 'Campaign':
        """캠페인 생성"""
        if budget > self._balance:
            raise ValueError("잔액이 부족합니다")
        
        campaign = Campaign(
            campaign_id=str(uuid.uuid4()),
            account=self,
            name=name,
            budget=budget
        )
        self._campaigns.append(campaign)
        self._balance -= budget
        return campaign
    
    @property
    def active_campaigns(self) -> List['Campaign']:
        """활성 캠페인 목록"""
        return [c for c in self._campaigns if c.is_active]

class Campaign:
    """광고 캠페인"""
    
    def __init__(self, campaign_id: str, account: AdAccount, 
                 name: str, budget: float):
        self._campaign_id = campaign_id
        self._account = account
        self._name = name
        self._budget = budget
        self._spent = 0.0
        self._ad_groups: List['AdGroup'] = []
        self._status = 'DRAFT'
        self._start_date: Optional[datetime] = None
        self._end_date: Optional[datetime] = None
    
    def create_ad_group(self, name: str, 
                       default_bid: float) -> 'AdGroup':
        """광고 그룹 생성"""
        ad_group = AdGroup(
            ad_group_id=str(uuid.uuid4()),
            campaign=self,
            name=name,
            default_bid=default_bid
        )
        self._ad_groups.append(ad_group)
        return ad_group
    
    def activate(self, duration_days: int = 30):
        """캠페인 활성화"""
        self._status = 'ACTIVE'
        self._start_date = datetime.now()
        self._end_date = self._start_date + timedelta(days=duration_days)
    
    @property
    def is_active(self) -> bool:
        """활성 상태 확인"""
        if self._status != 'ACTIVE':
            return False
        
        now = datetime.now()
        return (self._start_date <= now <= self._end_date)
    
    @property
    def remaining_budget(self) -> float:
        """남은 예산"""
        return self._budget - self._spent

class AdGroup:
    """광고 그룹"""
    
    def __init__(self, ad_group_id: str, campaign: Campaign,
                 name: str, default_bid: float):
        self._ad_group_id = ad_group_id
        self._campaign = campaign
        self._name = name
        self._default_bid = default_bid
        self._ads: List['Ad'] = []
        self._targeting = TargetingOptions()
    
    def add_ad(self, ad: 'Ad'):
        """광고 추가"""
        self._ads.append(ad)
    
    def set_targeting(self, targeting: 'TargetingOptions'):
        """타겟팅 설정"""
        self._targeting = targeting

class TargetingOptions:
    """타겟팅 옵션"""
    
    def __init__(self):
        self.age_range: Optional[tuple] = None
        self.genders: List[str] = []
        self.interests: List[str] = []
        self.locations: List[str] = []
        self.devices: List[str] = []
        self.custom_audiences: List[str] = []
    
    def set_demographics(self, age_range: tuple, 
                        genders: List[str]):
        """인구통계 설정"""
        self.age_range = age_range
        self.genders = genders
    
    def add_interest(self, interest: str):
        """관심사 추가"""
        if interest not in self.interests:
            self.interests.append(interest)
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            'age_range': self.age_range,
            'genders': self.genders,
            'interests': self.interests,
            'locations': self.locations,
            'devices': self.devices,
            'custom_audiences': self.custom_audiences
        }
```

### 실습 2: SOLID 원칙 적용

```python
# Single Responsibility Principle
class AdMetricsCalculator:
    """광고 지표 계산 전용 클래스"""
    
    @staticmethod
    def calculate_ctr(clicks: int, impressions: int) -> float:
        if impressions == 0:
            return 0.0
        return clicks / impressions
    
    @staticmethod
    def calculate_cvr(conversions: int, clicks: int) -> float:
        if clicks == 0:
            return 0.0
        return conversions / clicks
    
    @staticmethod
    def calculate_roas(revenue: float, cost: float) -> float:
        if cost == 0:
            return 0.0
        return revenue / cost

# Open/Closed Principle
class AdOptimizer(ABC):
    """광고 최적화 기본 클래스"""
    
    @abstractmethod
    def optimize(self, ad_data: Dict) -> Dict:
        pass

class CTROptimizer(AdOptimizer):
    """CTR 최적화"""
    
    def optimize(self, ad_data: Dict) -> Dict:
        # CTR 기반 최적화 로직
        if ad_data['ctr'] < 0.01:
            return {'action': 'pause', 'reason': 'Low CTR'}
        elif ad_data['ctr'] > 0.05:
            return {'action': 'increase_budget', 'reason': 'High CTR'}
        return {'action': 'maintain', 'reason': 'Normal CTR'}

class ROASOptimizer(AdOptimizer):
    """ROAS 최적화"""
    
    def optimize(self, ad_data: Dict) -> Dict:
        # ROAS 기반 최적화 로직
        if ad_data['roas'] < 1.0:
            return {'action': 'decrease_bid', 'reason': 'Low ROAS'}
        elif ad_data['roas'] > 3.0:
            return {'action': 'increase_bid', 'reason': 'High ROAS'}
        return {'action': 'maintain', 'reason': 'Normal ROAS'}

# Liskov Substitution Principle
class BaseAdFormat(ABC):
    """광고 포맷 기본 클래스"""
    
    def __init__(self, creative_id: str):
        self.creative_id = creative_id
    
    @abstractmethod
    def validate(self) -> bool:
        """검증 로직"""
        pass
    
    @abstractmethod
    def render(self) -> str:
        """렌더링"""
        pass

class TextAd(BaseAdFormat):
    def __init__(self, creative_id: str, headline: str, 
                 description: str):
        super().__init__(creative_id)
        self.headline = headline
        self.description = description
    
    def validate(self) -> bool:
        return (len(self.headline) <= 30 and 
                len(self.description) <= 90)
    
    def render(self) -> str:
        return f"{self.headline}\n{self.description}"

class ImageAd(BaseAdFormat):
    def __init__(self, creative_id: str, image_url: str, 
                 alt_text: str):
        super().__init__(creative_id)
        self.image_url = image_url
        self.alt_text = alt_text
    
    def validate(self) -> bool:
        return self.image_url.startswith(('http://', 'https://'))
    
    def render(self) -> str:
        return f'<img src="{self.image_url}" alt="{self.alt_text}"/>'

# Interface Segregation Principle
class Trackable(ABC):
    @abstractmethod
    def track_impression(self):
        pass
    
    @abstractmethod
    def track_click(self):
        pass

class Convertible(ABC):
    @abstractmethod
    def track_conversion(self, value: float):
        pass

class Optimizable(ABC):
    @abstractmethod
    def get_optimization_score(self) -> float:
        pass

# 필요한 인터페이스만 구현
class BasicAd(Trackable):
    def track_impression(self):
        # 노출 추적
        pass
    
    def track_click(self):
        # 클릭 추적
        pass

class ConversionAd(Trackable, Convertible, Optimizable):
    def track_impression(self):
        pass
    
    def track_click(self):
        pass
    
    def track_conversion(self, value: float):
        # 전환 추적
        pass
    
    def get_optimization_score(self) -> float:
        # 최적화 점수 계산
        return 0.85

# Dependency Inversion Principle
class DataStorage(ABC):
    """데이터 저장소 인터페이스"""
    
    @abstractmethod
    def save(self, key: str, data: Dict):
        pass
    
    @abstractmethod
    def load(self, key: str) -> Dict:
        pass

class RedisStorage(DataStorage):
    """Redis 저장소 구현"""
    
    def save(self, key: str, data: Dict):
        # Redis에 저장
        print(f"Saving to Redis: {key}")
    
    def load(self, key: str) -> Dict:
        # Redis에서 로드
        print(f"Loading from Redis: {key}")
        return {}

class FileStorage(DataStorage):
    """파일 저장소 구현"""
    
    def save(self, key: str, data: Dict):
        # 파일에 저장
        print(f"Saving to file: {key}.json")
    
    def load(self, key: str) -> Dict:
        # 파일에서 로드
        print(f"Loading from file: {key}.json")
        return {}

class AdDataManager:
    """광고 데이터 관리자 (DIP 적용)"""
    
    def __init__(self, storage: DataStorage):
        self.storage = storage  # 추상화에 의존
    
    def save_campaign(self, campaign_id: str, data: Dict):
        self.storage.save(f"campaign:{campaign_id}", data)
    
    def load_campaign(self, campaign_id: str) -> Dict:
        return self.storage.load(f"campaign:{campaign_id}")
```

### 실습 3: 디자인 패턴 활용

```python
# Factory Pattern
class AdCreativeFactory:
    """광고 크리에이티브 팩토리"""
    
    @staticmethod
    def create_ad(ad_type: str, **kwargs) -> BaseAdFormat:
        if ad_type == 'text':
            return TextAd(
                kwargs['creative_id'],
                kwargs['headline'],
                kwargs['description']
            )
        elif ad_type == 'image':
            return ImageAd(
                kwargs['creative_id'],
                kwargs['image_url'],
                kwargs['alt_text']
            )
        elif ad_type == 'video':
            return VideoAd(
                kwargs['creative_id'],
                kwargs['video_url'],
                kwargs['duration']
            )
        else:
            raise ValueError(f"Unknown ad type: {ad_type}")

# Strategy Pattern
class AdDeliveryContext:
    """광고 전달 컨텍스트"""
    
    def __init__(self, strategy: BidStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: BidStrategy):
        """전략 변경"""
        self._strategy = strategy
    
    def calculate_bid(self, base_bid: float, 
                     quality_score: float,
                     competition_level: float) -> float:
        """입찰가 계산"""
        return self._strategy.calculate_bid(
            base_bid, quality_score, competition_level
        )

# Observer Pattern
class AdPerformanceSubject:
    """광고 성과 주체"""
    
    def __init__(self):
        self._observers: List['PerformanceObserver'] = []
        self._metrics = {}
    
    def attach(self, observer: 'PerformanceObserver'):
        """옵저버 등록"""
        self._observers.append(observer)
    
    def detach(self, observer: 'PerformanceObserver'):
        """옵저버 해제"""
        self._observers.remove(observer)
    
    def notify(self):
        """모든 옵저버에게 알림"""
        for observer in self._observers:
            observer.update(self._metrics)
    
    def update_metrics(self, metrics: Dict):
        """지표 업데이트"""
        self._metrics = metrics
        self.notify()

class PerformanceObserver(ABC):
    """성과 옵저버 인터페이스"""
    
    @abstractmethod
    def update(self, metrics: Dict):
        pass

class BudgetAlertObserver(PerformanceObserver):
    """예산 알림 옵저버"""
    
    def update(self, metrics: Dict):
        if metrics.get('spent_ratio', 0) > 0.8:
            print(f"⚠️ 예산의 {metrics['spent_ratio']*100:.0f}% 소진됨!")

class PerformanceAlertObserver(PerformanceObserver):
    """성과 알림 옵저버"""
    
    def update(self, metrics: Dict):
        if metrics.get('roas', 0) < 1.0:
            print(f"📉 ROAS가 {metrics['roas']:.2f}로 목표 미달!")
```

## 🚀 프로젝트: 광고 관리 플랫폼

### 프로젝트 구조
```
ad_management_platform/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── account.py
│   ├── campaign.py
│   ├── ad_group.py
│   ├── ad.py
│   └── targeting.py
├── services/
│   ├── __init__.py
│   ├── optimizer.py
│   ├── bidding.py
│   └── reporting.py
├── repositories/
│   ├── __init__.py
│   ├── base.py
│   └── campaign_repository.py
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   └── decorators.py
└── main.py
```

### 통합 예제: 광고 관리 시스템

```python
# main.py
from datetime import datetime
from typing import List, Dict, Optional
import json

class AdManagementSystem:
    """광고 관리 시스템"""
    
    def __init__(self):
        self.accounts: Dict[str, AdAccount] = {}
        self.storage = FileStorage()  # DIP 적용
        self.performance_monitor = AdPerformanceSubject()
        
        # 옵저버 등록
        self.performance_monitor.attach(BudgetAlertObserver())
        self.performance_monitor.attach(PerformanceAlertObserver())
    
    def create_account(self, name: str, 
                      initial_balance: float) -> AdAccount:
        """계정 생성"""
        account_id = f"acc_{datetime.now().timestamp()}"
        account = AdAccount(account_id, name)
        account.add_balance(initial_balance)
        
        self.accounts[account_id] = account
        return account
    
    def create_campaign_workflow(
        self,
        account: AdAccount,
        campaign_name: str,
        budget: float,
        ad_groups_config: List[Dict]
    ) -> Campaign:
        """캠페인 생성 워크플로우"""
        
        # 1. 캠페인 생성
        campaign = account.create_campaign(campaign_name, budget)
        
        # 2. 광고 그룹 및 광고 생성
        for config in ad_groups_config:
            ad_group = campaign.create_ad_group(
                config['name'],
                config['default_bid']
            )
            
            # 타겟팅 설정
            targeting = TargetingOptions()
            targeting.set_demographics(
                config.get('age_range', (18, 65)),
                config.get('genders', ['all'])
            )
            
            for interest in config.get('interests', []):
                targeting.add_interest(interest)
            
            ad_group.set_targeting(targeting)
            
            # 광고 생성
            for ad_config in config.get('ads', []):
                ad = AdCreativeFactory.create_ad(
                    ad_config['type'],
                    **ad_config['params']
                )
                ad_group.add_ad(ad)
        
        # 3. 캠페인 활성화
        campaign.activate()
        
        # 4. 저장
        self._save_campaign(campaign)
        
        return campaign
    
    def optimize_campaigns(self):
        """모든 캠페인 최적화"""
        optimizer = CTROptimizer()  # 전략 패턴
        
        for account in self.accounts.values():
            for campaign in account.active_campaigns:
                metrics = self._get_campaign_metrics(campaign)
                
                # 성과 모니터링
                self.performance_monitor.update_metrics(metrics)
                
                # 최적화 실행
                optimization = optimizer.optimize(metrics)
                self._apply_optimization(campaign, optimization)
    
    def _get_campaign_metrics(self, campaign: Campaign) -> Dict:
        """캠페인 지표 조회"""
        # 실제로는 데이터베이스에서 조회
        return {
            'campaign_id': campaign._campaign_id,
            'impressions': 10000,
            'clicks': 150,
            'conversions': 10,
            'cost': campaign._spent,
            'revenue': 50000,
            'ctr': 0.015,
            'roas': 2.5,
            'spent_ratio': campaign._spent / campaign._budget
        }
    
    def _apply_optimization(self, campaign: Campaign, 
                           optimization: Dict):
        """최적화 적용"""
        action = optimization['action']
        
        if action == 'pause':
            campaign._status = 'PAUSED'
        elif action == 'increase_budget':
            campaign._budget *= 1.2
        elif action == 'decrease_bid':
            for ad_group in campaign._ad_groups:
                ad_group._default_bid *= 0.9
        
        print(f"캠페인 {campaign._name}: {optimization}")
    
    def _save_campaign(self, campaign: Campaign):
        """캠페인 저장"""
        data = {
            'campaign_id': campaign._campaign_id,
            'name': campaign._name,
            'budget': campaign._budget,
            'status': campaign._status,
            'created_at': datetime.now().isoformat()
        }
        self.storage.save(f"campaign:{campaign._campaign_id}", data)
    
    def generate_report(self) -> Dict:
        """전체 리포트 생성"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'accounts': []
        }
        
        for account in self.accounts.values():
            account_data = {
                'account_id': account._account_id,
                'name': account._name,
                'balance': account._balance,
                'campaigns': []
            }
            
            for campaign in account._campaigns:
                metrics = self._get_campaign_metrics(campaign)
                calculator = AdMetricsCalculator()
                
                campaign_data = {
                    'campaign_id': campaign._campaign_id,
                    'name': campaign._name,
                    'status': campaign._status,
                    'budget': campaign._budget,
                    'spent': campaign._spent,
                    'metrics': {
                        'ctr': calculator.calculate_ctr(
                            metrics['clicks'], 
                            metrics['impressions']
                        ),
                        'roas': calculator.calculate_roas(
                            metrics['revenue'],
                            metrics['cost']
                        )
                    }
                }
                account_data['campaigns'].append(campaign_data)
            
            report['accounts'].append(account_data)
        
        return report

# 사용 예시
if __name__ == "__main__":
    # 시스템 초기화
    system = AdManagementSystem()
    
    # 계정 생성
    account = system.create_account("패션 브랜드 A", 10000000)
    
    # 캠페인 설정
    ad_groups_config = [
        {
            'name': '봄 신상품',
            'default_bid': 500,
            'age_range': (20, 35),
            'genders': ['female'],
            'interests': ['패션', '쇼핑', '뷰티'],
            'ads': [
                {
                    'type': 'text',
                    'params': {
                        'creative_id': 'txt_001',
                        'headline': '봄 신상 최대 50% 할인',
                        'description': '지금 바로 만나보세요!'
                    }
                },
                {
                    'type': 'image',
                    'params': {
                        'creative_id': 'img_001',
                        'image_url': 'https://example.com/spring.jpg',
                        'alt_text': '봄 신상품 이미지'
                    }
                }
            ]
        }
    ]
    
    # 캠페인 생성
    campaign = system.create_campaign_workflow(
        account,
        "2024 봄 시즌 캠페인",
        2000000,
        ad_groups_config
    )
    
    # 최적화 실행
    system.optimize_campaigns()
    
    # 리포트 생성
    report = system.generate_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))
```

## 📝 과제

### 과제 1: 광고 타입 확장
다음 광고 타입을 추가로 구현하세요:
- VideoAd: 동영상 광고
- CarouselAd: 캐러셀 광고
- DynamicAd: 다이나믹 광고

### 과제 2: 새로운 최적화 전략
다음 최적화 전략을 구현하세요:
- BudgetPacingOptimizer: 예산 소진 속도 최적화
- AudienceOptimizer: 타겟 오디언스 최적화
- CreativeOptimizer: 크리에이티브 성과 최적화

### 과제 3: 리포지토리 패턴 구현
캠페인 데이터를 관리하는 리포지토리 패턴을 구현하세요:
- CampaignRepository
- AdGroupRepository
- PerformanceRepository

### 과제 4: 통합 테스트
전체 시스템에 대한 통합 테스트를 작성하세요:
- 캠페인 생성 플로우 테스트
- 최적화 로직 테스트
- 리포트 생성 테스트

## 🔗 참고 자료
- [Python OOP Tutorial](https://realpython.com/python3-object-oriented-programming/)
- [SOLID Principles in Python](https://realpython.com/solid-principles-python/)
- [Design Patterns in Python](https://refactoring.guru/design-patterns/python)
- Clean Architecture by Robert C. Martin

---

다음 장: [Chapter 03: Multiprocessing →](../03_multiprocessing/README.md)