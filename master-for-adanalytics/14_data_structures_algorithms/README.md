# 14. Data Structures & Algorithms - 자료구조와 알고리즘

## 📚 과정 소개
광고 플랫폼에 특화된 자료구조와 알고리즘을 마스터합니다. 실시간 입찰, 타겟팅, 추천 시스템에 최적화된 고성능 알고리즘을 학습합니다.

## 🎯 학습 목표
- 광고 플랫폼 특화 자료구조 설계
- 실시간 입찰 알고리즘 최적화
- 타겟팅 및 매칭 알고리즘
- 대규모 데이터 처리 최적화

## 📖 주요 내용

### 광고 플랫폼 특화 자료구조
```python
import heapq
import bisect
from collections import defaultdict, deque
from typing import List, Dict, Set, Tuple, Optional
import time
import threading
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import random

@dataclass
class AdRequest:
    """광고 요청"""
    request_id: str
    user_id: str
    timestamp: float
    device_type: str
    location: Tuple[float, float]  # (lat, lng)
    interests: Set[str]
    age_group: str
    budget_range: Tuple[float, float]

@dataclass
class AdCampaign:
    """광고 캠페인"""
    campaign_id: str
    advertiser_id: str
    bid_price: float
    daily_budget: float
    spent_budget: float
    target_interests: Set[str]
    target_age_groups: Set[str]
    target_locations: List[Tuple[float, float, float]]  # (lat, lng, radius)
    is_active: bool = True
    priority: int = 0

class BidType(Enum):
    CPM = "cpm"
    CPC = "cpc" 
    CPA = "cpa"

@dataclass
class Bid:
    """입찰"""
    bid_id: str
    campaign_id: str
    bid_price: float
    bid_type: BidType
    timestamp: float
    score: float = 0.0

class BloomFilter:
    """중복 광고 노출 방지를 위한 블룸 필터"""
    
    def __init__(self, capacity: int, error_rate: float = 0.1):
        self.capacity = capacity
        self.error_rate = error_rate
        self.bit_array_size = self._calculate_bit_array_size()
        self.hash_count = self._calculate_hash_count()
        self.bit_array = [0] * self.bit_array_size
        
    def _calculate_bit_array_size(self) -> int:
        import math
        m = -(self.capacity * math.log(self.error_rate)) / (math.log(2) ** 2)
        return int(m)
    
    def _calculate_hash_count(self) -> int:
        import math
        k = (self.bit_array_size / self.capacity) * math.log(2)
        return int(k)
    
    def _hash(self, item: str, seed: int) -> int:
        """해시 함수"""
        hash_obj = hashlib.md5(f"{item}{seed}".encode())
        return int(hash_obj.hexdigest(), 16) % self.bit_array_size
    
    def add(self, item: str):
        """아이템 추가"""
        for i in range(self.hash_count):
            index = self._hash(item, i)
            self.bit_array[index] = 1
    
    def contains(self, item: str) -> bool:
        """아이템 포함 여부 확인"""
        for i in range(self.hash_count):
            index = self._hash(item, i)
            if self.bit_array[index] == 0:
                return False
        return True

class GeospatialIndex:
    """지리적 타겟팅을 위한 공간 인덱스"""
    
    def __init__(self):
        self.campaigns_by_location = defaultdict(list)
        self.grid_size = 0.01  # 약 1km 단위 그리드
        
    def _get_grid_key(self, lat: float, lng: float) -> Tuple[int, int]:
        """좌표를 그리드 키로 변환"""
        return (int(lat / self.grid_size), int(lng / self.grid_size))
    
    def add_campaign(self, campaign: AdCampaign):
        """캠페인을 지리적 인덱스에 추가"""
        for lat, lng, radius in campaign.target_locations:
            # 반경 내 모든 그리드 셀에 캠페인 추가
            grid_radius = int(radius / (self.grid_size * 111000)) + 1  # 대략적인 변환
            center_grid = self._get_grid_key(lat, lng)
            
            for i in range(-grid_radius, grid_radius + 1):
                for j in range(-grid_radius, grid_radius + 1):
                    grid_key = (center_grid[0] + i, center_grid[1] + j)
                    self.campaigns_by_location[grid_key].append(campaign)
    
    def get_campaigns_by_location(self, lat: float, lng: float) -> List[AdCampaign]:
        """위치에 해당하는 캠페인 조회"""
        grid_key = self._get_grid_key(lat, lng)
        campaigns = self.campaigns_by_location.get(grid_key, [])
        
        # 실제 거리 기반 필터링
        valid_campaigns = []
        for campaign in campaigns:
            for target_lat, target_lng, radius in campaign.target_locations:
                distance = self._haversine_distance(lat, lng, target_lat, target_lng)
                if distance <= radius:
                    valid_campaigns.append(campaign)
                    break
                    
        return valid_campaigns
    
    def _haversine_distance(self, lat1: float, lng1: float, 
                           lat2: float, lng2: float) -> float:
        """두 지점 간 거리 계산 (미터)"""
        import math
        
        R = 6371000  # 지구 반지름 (미터)
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_phi / 2) ** 2 + 
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

class FrequencyCapManager:
    """광고 노출 빈도 제한 관리"""
    
    def __init__(self, default_cap: int = 3):
        self.default_cap = default_cap
        self.exposure_counts = defaultdict(lambda: defaultdict(int))  # user_id -> campaign_id -> count
        self.exposure_times = defaultdict(lambda: defaultdict(list))  # user_id -> campaign_id -> [timestamps]
        self.lock = threading.RLock()
        
    def can_show_ad(self, user_id: str, campaign_id: str, 
                   time_window: int = 86400) -> bool:  # 24시간 윈도우
        """광고 노출 가능 여부 확인"""
        with self.lock:
            current_time = time.time()
            
            # 시간 윈도우 내 노출 기록 정리
            exposure_times = self.exposure_times[user_id][campaign_id]
            valid_exposures = [t for t in exposure_times if current_time - t <= time_window]
            self.exposure_times[user_id][campaign_id] = valid_exposures
            self.exposure_counts[user_id][campaign_id] = len(valid_exposures)
            
            return len(valid_exposures) < self.default_cap
    
    def record_exposure(self, user_id: str, campaign_id: str):
        """광고 노출 기록"""
        with self.lock:
            current_time = time.time()
            self.exposure_times[user_id][campaign_id].append(current_time)
            self.exposure_counts[user_id][campaign_id] += 1

class RealTimeBiddingEngine:
    """실시간 입찰 엔진"""
    
    def __init__(self):
        self.geospatial_index = GeospatialIndex()
        self.frequency_cap = FrequencyCapManager()
        self.user_bloom_filters = defaultdict(lambda: BloomFilter(10000))
        self.campaign_heap = []  # 우선순위 힙
        self.lock = threading.RLock()
        
    def add_campaign(self, campaign: AdCampaign):
        """캠페인 추가"""
        with self.lock:
            # 지리적 인덱스에 추가
            if campaign.target_locations:
                self.geospatial_index.add_campaign(campaign)
            
            # 우선순위 힙에 추가 (음수로 최대힙 구현)
            heapq.heappush(self.campaign_heap, (-campaign.bid_price, campaign))
    
    def process_ad_request(self, request: AdRequest) -> List[Bid]:
        """광고 요청 처리"""
        start_time = time.time()
        candidate_campaigns = self._find_matching_campaigns(request)
        
        # 입찰 생성 및 랭킹
        bids = []
        for campaign in candidate_campaigns:
            if self._is_eligible_campaign(request, campaign):
                bid = self._create_bid(request, campaign)
                bids.append(bid)
        
        # 입찰 정렬 (점수 기준)
        bids.sort(key=lambda x: x.score, reverse=True)
        
        processing_time = time.time() - start_time
        print(f"Request processed in {processing_time*1000:.2f}ms")
        
        return bids[:5]  # 상위 5개 입찰 반환
    
    def _find_matching_campaigns(self, request: AdRequest) -> List[AdCampaign]:
        """매칭되는 캠페인 찾기"""
        candidates = []
        
        # 지리적 필터링
        if request.location:
            geo_campaigns = self.geospatial_index.get_campaigns_by_location(
                request.location[0], request.location[1]
            )
            candidates.extend(geo_campaigns)
        
        # 관심사 기반 필터링
        interest_campaigns = []
        for _, campaign in self.campaign_heap:
            if campaign.is_active and campaign.target_interests & request.interests:
                interest_campaigns.append(campaign)
        
        candidates.extend(interest_campaigns)
        
        # 중복 제거
        unique_campaigns = {c.campaign_id: c for c in candidates}
        return list(unique_campaigns.values())
    
    def _is_eligible_campaign(self, request: AdRequest, campaign: AdCampaign) -> bool:
        """캠페인 자격 확인"""
        # 예산 확인
        if campaign.spent_budget >= campaign.daily_budget:
            return False
        
        # 연령대 타겟팅 확인
        if campaign.target_age_groups and request.age_group not in campaign.target_age_groups:
            return False
        
        # 빈도 제한 확인
        if not self.frequency_cap.can_show_ad(request.user_id, campaign.campaign_id):
            return False
        
        # 블룸 필터로 최근 노출 확인
        bloom_key = f"{request.user_id}:{campaign.campaign_id}"
        if self.user_bloom_filters[request.user_id].contains(bloom_key):
            return False
        
        return True
    
    def _create_bid(self, request: AdRequest, campaign: AdCampaign) -> Bid:
        """입찰 생성"""
        # 스코어 계산 (CTR 예측, 관련성 등을 고려)
        score = self._calculate_bid_score(request, campaign)
        
        return Bid(
            bid_id=f"{campaign.campaign_id}_{request.request_id}",
            campaign_id=campaign.campaign_id,
            bid_price=campaign.bid_price,
            bid_type=BidType.CPM,
            timestamp=time.time(),
            score=score
        )
    
    def _calculate_bid_score(self, request: AdRequest, campaign: AdCampaign) -> float:
        """입찰 점수 계산"""
        score = campaign.bid_price
        
        # 관심사 일치도
        interest_overlap = len(request.interests & campaign.target_interests)
        if interest_overlap > 0:
            score *= (1 + interest_overlap * 0.1)
        
        # 지리적 근접성 (거리에 반비례)
        if request.location and campaign.target_locations:
            min_distance = float('inf')
            for lat, lng, radius in campaign.target_locations:
                distance = self.geospatial_index._haversine_distance(
                    request.location[0], request.location[1], lat, lng
                )
                min_distance = min(min_distance, distance)
            
            if min_distance < float('inf'):
                # 거리가 가까울수록 높은 점수
                proximity_bonus = max(0, 1 - min_distance / 10000)  # 10km 기준
                score *= (1 + proximity_bonus)
        
        return score

class AudienceSegmentTree:
    """오디언스 세그먼트를 위한 세그먼트 트리"""
    
    def __init__(self, size: int):
        self.size = size
        self.tree = [0] * (4 * size)
        self.lazy = [0] * (4 * size)
    
    def _push(self, node: int, start: int, end: int):
        """지연 전파"""
        if self.lazy[node] != 0:
            self.tree[node] += self.lazy[node] * (end - start + 1)
            if start != end:
                self.lazy[2 * node] += self.lazy[node]
                self.lazy[2 * node + 1] += self.lazy[node]
            self.lazy[node] = 0
    
    def update_range(self, node: int, start: int, end: int, 
                    left: int, right: int, value: int):
        """범위 업데이트"""
        self._push(node, start, end)
        if start > right or end < left:
            return
        
        if start >= left and end <= right:
            self.lazy[node] += value
            self._push(node, start, end)
            return
        
        mid = (start + end) // 2
        self.update_range(2 * node, start, mid, left, right, value)
        self.update_range(2 * node + 1, mid + 1, end, left, right, value)
        
        self._push(2 * node, start, mid)
        self._push(2 * node + 1, mid + 1, end)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]
    
    def query_range(self, node: int, start: int, end: int, 
                   left: int, right: int) -> int:
        """범위 쿼리"""
        if start > right or end < left:
            return 0
        
        self._push(node, start, end)
        
        if start >= left and end <= right:
            return self.tree[node]
        
        mid = (start + end) // 2
        left_sum = self.query_range(2 * node, start, mid, left, right)
        right_sum = self.query_range(2 * node + 1, mid + 1, end, left, right)
        
        return left_sum + right_sum

class AdRecommendationSystem:
    """광고 추천 시스템"""
    
    def __init__(self):
        self.user_profiles = defaultdict(dict)
        self.item_similarity = defaultdict(dict)
        self.user_item_matrix = defaultdict(lambda: defaultdict(float))
        
    def update_user_interaction(self, user_id: str, ad_id: str, 
                              interaction_type: str, weight: float = 1.0):
        """사용자 상호작용 업데이트"""
        # 상호작용 타입별 가중치
        weights = {
            'view': 1.0,
            'click': 3.0,
            'conversion': 10.0
        }
        
        final_weight = weights.get(interaction_type, 1.0) * weight
        self.user_item_matrix[user_id][ad_id] += final_weight
    
    def calculate_item_similarity(self):
        """아이템 간 유사도 계산 (코사인 유사도)"""
        import math
        
        # 모든 광고 ID 수집
        all_ads = set()
        for user_ads in self.user_item_matrix.values():
            all_ads.update(user_ads.keys())
        
        all_ads = list(all_ads)
        
        for i, ad1 in enumerate(all_ads):
            for j, ad2 in enumerate(all_ads[i+1:], i+1):
                similarity = self._cosine_similarity(ad1, ad2)
                self.item_similarity[ad1][ad2] = similarity
                self.item_similarity[ad2][ad1] = similarity
    
    def _cosine_similarity(self, ad1: str, ad2: str) -> float:
        """코사인 유사도 계산"""
        import math
        
        # 두 광고를 모두 본 사용자들
        users1 = {user for user, ads in self.user_item_matrix.items() if ad1 in ads}
        users2 = {user for user, ads in self.user_item_matrix.items() if ad2 in ads}
        common_users = users1 & users2
        
        if not common_users:
            return 0.0
        
        # 벡터 내적과 크기 계산
        dot_product = sum(
            self.user_item_matrix[user][ad1] * self.user_item_matrix[user][ad2]
            for user in common_users
        )
        
        magnitude1 = math.sqrt(sum(
            self.user_item_matrix[user][ad1] ** 2
            for user in users1
        ))
        
        magnitude2 = math.sqrt(sum(
            self.user_item_matrix[user][ad2] ** 2
            for user in users2
        ))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def recommend_ads(self, user_id: str, n: int = 10) -> List[Tuple[str, float]]:
        """사용자에게 광고 추천"""
        user_ads = self.user_item_matrix.get(user_id, {})
        if not user_ads:
            return []
        
        recommendations = defaultdict(float)
        
        # 협업 필터링 기반 추천
        for ad_id, rating in user_ads.items():
            similar_ads = self.item_similarity.get(ad_id, {})
            for similar_ad, similarity in similar_ads.items():
                if similar_ad not in user_ads:  # 아직 보지 않은 광고만
                    recommendations[similar_ad] += rating * similarity
        
        # 점수 기준 정렬
        sorted_recommendations = sorted(
            recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return sorted_recommendations[:n]

class BudgetOptimizer:
    """예산 최적화 알고리즘"""
    
    def __init__(self):
        self.campaign_performance = defaultdict(dict)
        
    def optimize_budget_allocation(self, campaigns: List[AdCampaign], 
                                 total_budget: float) -> Dict[str, float]:
        """예산 할당 최적화 (그리디 알고리즘)"""
        # 성과 기반 우선순위 계산
        campaign_efficiency = []
        
        for campaign in campaigns:
            efficiency = self._calculate_efficiency(campaign)
            campaign_efficiency.append((campaign.campaign_id, efficiency, campaign.daily_budget))
        
        # 효율성 기준 정렬
        campaign_efficiency.sort(key=lambda x: x[1], reverse=True)
        
        # 그리디 할당
        allocation = {}
        remaining_budget = total_budget
        
        for campaign_id, efficiency, max_budget in campaign_efficiency:
            if remaining_budget <= 0:
                allocation[campaign_id] = 0
                continue
            
            # 할당 가능한 최대 예산
            allocated_budget = min(remaining_budget, max_budget)
            allocation[campaign_id] = allocated_budget
            remaining_budget -= allocated_budget
        
        return allocation
    
    def _calculate_efficiency(self, campaign: AdCampaign) -> float:
        """캠페인 효율성 계산"""
        performance = self.campaign_performance.get(campaign.campaign_id, {})
        
        # 기본 효율성은 입찰 가격
        efficiency = campaign.bid_price
        
        # 과거 성과가 있으면 반영
        if 'roas' in performance:
            efficiency *= performance['roas']
        
        if 'ctr' in performance:
            efficiency *= (1 + performance['ctr'])
        
        return efficiency

# 성능 테스트 및 벤치마크
class PerformanceBenchmark:
    """성능 벤치마크"""
    
    def __init__(self):
        self.rtb_engine = RealTimeBiddingEngine()
        self.recommendation_system = AdRecommendationSystem()
        
    def benchmark_rtb_performance(self, num_requests: int = 10000):
        """RTB 성능 벤치마크"""
        # 테스트 캠페인 생성
        campaigns = self._create_test_campaigns(1000)
        for campaign in campaigns:
            self.rtb_engine.add_campaign(campaign)
        
        # 테스트 요청 생성
        requests = self._create_test_requests(num_requests)
        
        # 성능 측정
        start_time = time.time()
        total_bids = 0
        
        for request in requests:
            bids = self.rtb_engine.process_ad_request(request)
            total_bids += len(bids)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"RTB Performance Benchmark:")
        print(f"Processed {num_requests:,} requests in {processing_time:.2f} seconds")
        print(f"Average processing time: {(processing_time/num_requests)*1000:.2f}ms per request")
        print(f"Throughput: {num_requests/processing_time:.0f} requests per second")
        print(f"Total bids generated: {total_bids:,}")
        
        return {
            'requests_per_second': num_requests / processing_time,
            'avg_processing_time_ms': (processing_time / num_requests) * 1000,
            'total_bids': total_bids
        }
    
    def _create_test_campaigns(self, count: int) -> List[AdCampaign]:
        """테스트 캠페인 생성"""
        campaigns = []
        interests_pool = ['tech', 'sports', 'fashion', 'food', 'travel', 'music']
        age_groups = ['18-24', '25-34', '35-44', '45-54', '55+']
        
        for i in range(count):
            campaign = AdCampaign(
                campaign_id=f"campaign_{i}",
                advertiser_id=f"advertiser_{i//10}",
                bid_price=random.uniform(0.5, 5.0),
                daily_budget=random.uniform(100, 10000),
                spent_budget=0,
                target_interests=set(random.sample(interests_pool, random.randint(1, 3))),
                target_age_groups=set(random.sample(age_groups, random.randint(1, 2))),
                target_locations=[(
                    random.uniform(37.4, 37.6),  # 서울 근처
                    random.uniform(126.8, 127.1),
                    random.uniform(1000, 10000)
                )]
            )
            campaigns.append(campaign)
        
        return campaigns
    
    def _create_test_requests(self, count: int) -> List[AdRequest]:
        """테스트 요청 생성"""
        requests = []
        interests_pool = ['tech', 'sports', 'fashion', 'food', 'travel', 'music']
        age_groups = ['18-24', '25-34', '35-44', '45-54', '55+']
        devices = ['mobile', 'desktop', 'tablet']
        
        for i in range(count):
            request = AdRequest(
                request_id=f"req_{i}",
                user_id=f"user_{random.randint(1, 10000)}",
                timestamp=time.time(),
                device_type=random.choice(devices),
                location=(
                    random.uniform(37.4, 37.6),
                    random.uniform(126.8, 127.1)
                ),
                interests=set(random.sample(interests_pool, random.randint(1, 4))),
                age_group=random.choice(age_groups),
                budget_range=(random.uniform(0.5, 2.0), random.uniform(2.0, 10.0))
            )
            requests.append(request)
        
        return requests

# 사용 예시
def example_ad_algorithms():
    """광고 알고리즘 예시"""
    # 성능 벤치마크 실행
    benchmark = PerformanceBenchmark()
    
    print("RTB 엔진 성능 테스트...")
    rtb_results = benchmark.benchmark_rtb_performance(1000)
    
    # 추천 시스템 테스트
    print("\n추천 시스템 테스트...")
    rec_system = AdRecommendationSystem()
    
    # 샘플 상호작용 데이터
    users = [f"user_{i}" for i in range(100)]
    ads = [f"ad_{i}" for i in range(50)]
    
    for _ in range(1000):
        user = random.choice(users)
        ad = random.choice(ads)
        interaction = random.choice(['view', 'click', 'conversion'])
        rec_system.update_user_interaction(user, ad, interaction)
    
    # 유사도 계산 및 추천
    rec_system.calculate_item_similarity()
    recommendations = rec_system.recommend_ads("user_1", 5)
    
    print(f"User_1에 대한 상위 5개 추천:")
    for ad_id, score in recommendations:
        print(f"  {ad_id}: {score:.3f}")
    
    return {
        'rtb_performance': rtb_results,
        'recommendations': recommendations
    }

if __name__ == "__main__":
    results = example_ad_algorithms()
    print("광고 알고리즘 테스트 완료!")
```

## 🚀 프로젝트
1. **실시간 입찰 엔진**
2. **지리적 타겟팅 시스템**
3. **광고 추천 알고리즘**
4. **예산 최적화 엔진**