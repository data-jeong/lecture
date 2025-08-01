# 34. Programmatic Advertising - 프로그래매틱 광고

## 📚 과정 소개
실시간 입찰(RTB), 광고 거래소(Ad Exchange), 수요측 플랫폼(DSP) 개발을 통한 프로그래매틱 광고 시스템을 구축합니다.

## 🎯 학습 목표
- RTB 시스템 아키텍처 설계
- 광고 거래소 개발
- 실시간 입찰 알고리즘 구현
- 프로그래매틱 최적화 전략

## 📖 주요 내용

### RTB 시스템 기본 구조
```python
import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class BidResponseStatus(Enum):
    WIN = "win"
    LOSE = "lose"
    NO_BID = "no_bid"
    ERROR = "error"

@dataclass
class BidRequest:
    """입찰 요청 데이터"""
    id: str
    imp: List[Dict]  # Impression 정보
    device: Dict
    user: Dict
    site: Optional[Dict] = None
    app: Optional[Dict] = None
    geo: Optional[Dict] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@dataclass
class BidResponse:
    """입찰 응답 데이터"""
    id: str
    seatbid: List[Dict]
    cur: str = "KRW"
    
class RTBBidder:
    """실시간 입찰 시스템"""
    
    def __init__(self, bidder_id: str, timeout_ms: int = 100):
        self.bidder_id = bidder_id
        self.timeout_ms = timeout_ms
        self.campaign_targeting = {}
        self.bid_history = []
        
    async def handle_bid_request(self, request_data: Dict) -> Optional[BidResponse]:
        """입찰 요청 처리"""
        try:
            # 입찰 요청 파싱
            bid_request = self._parse_bid_request(request_data)
            
            # 타겟팅 검증
            if not await self._validate_targeting(bid_request):
                return None
            
            # 입찰가 계산
            bids = await self._calculate_bids(bid_request)
            
            if not bids:
                return None
            
            # 입찰 응답 생성
            response = BidResponse(
                id=bid_request.id,
                seatbid=[{
                    "bid": bids,
                    "seat": self.bidder_id
                }]
            )
            
            # 입찰 이력 저장
            self._log_bid(bid_request, response)
            
            return response
            
        except Exception as e:
            print(f"Bid request error: {e}")
            return None
    
    def _parse_bid_request(self, data: Dict) -> BidRequest:
        """입찰 요청 파싱"""
        return BidRequest(
            id=data['id'],
            imp=data['imp'],
            device=data.get('device', {}),
            user=data.get('user', {}),
            site=data.get('site'),
            app=data.get('app'),
            geo=data.get('geo')
        )
    
    async def _validate_targeting(self, request: BidRequest) -> bool:
        """타겟팅 조건 검증"""
        # 지역 타겟팅
        if request.geo:
            country = request.geo.get('country')
            if country not in ['KR', 'US', 'JP']:  # 허용 국가
                return False
        
        # 디바이스 타겟팅
        device_type = request.device.get('devicetype')
        if device_type not in [1, 2, 4]:  # Mobile, PC, Tablet만
            return False
        
        # 시간 타겟팅
        current_hour = time.localtime().tm_hour
        if not (9 <= current_hour <= 23):  # 광고 허용 시간
            return False
        
        return True
    
    async def _calculate_bids(self, request: BidRequest) -> List[Dict]:
        """입찰가 계산"""
        bids = []
        
        for imp in request.imp:
            # 기본 입찰가 계산
            base_bid = await self._calculate_base_bid(imp, request)
            
            if base_bid <= 0:
                continue
            
            # CTR 예측
            predicted_ctr = await self._predict_ctr(imp, request)
            
            # 최종 입찰가 = 기본입찰가 × CTR × 조정계수
            final_bid = base_bid * predicted_ctr * self._get_adjustment_factor(request)
            
            # 최소/최대 입찰가 제한
            final_bid = max(min(final_bid, 5000), 100)  # 100원~5000원
            
            bid = {
                "id": f"bid_{imp['id']}",
                "impid": imp['id'],
                "price": final_bid,
                "adm": await self._get_ad_markup(imp, request),
                "crid": f"creative_{imp['id']}",
                "w": imp.get('banner', {}).get('w', 320),
                "h": imp.get('banner', {}).get('h', 50)
            }
            
            bids.append(bid)
        
        return bids
    
    async def _calculate_base_bid(self, imp: Dict, request: BidRequest) -> float:
        """기본 입찰가 계산"""
        # 광고 위치별 기본가
        position_multiplier = {
            'above_fold': 1.5,
            'below_fold': 1.0,
            'sidebar': 0.8
        }.get(imp.get('pos', 'below_fold'), 1.0)
        
        # 광고 크기별 기본가
        banner = imp.get('banner', {})
        size_score = (banner.get('w', 320) * banner.get('h', 50)) / 16000  # 320x50 기준
        
        base_bid = 1000 * position_multiplier * min(size_score, 2.0)
        return base_bid
    
    async def _predict_ctr(self, imp: Dict, request: BidRequest) -> float:
        """CTR 예측 (간단한 룰 기반)"""
        ctr = 0.02  # 기본 CTR 2%
        
        # 디바이스별 조정
        device_type = request.device.get('devicetype')
        if device_type == 2:  # Mobile
            ctr *= 1.2
        elif device_type == 1:  # PC
            ctr *= 0.9
        
        # 시간대별 조정
        hour = time.localtime().tm_hour
        if 19 <= hour <= 22:  # 저녁 시간대
            ctr *= 1.3
        elif 9 <= hour <= 18:  # 업무 시간
            ctr *= 1.1
        
        return min(ctr, 0.1)  # 최대 10%
    
    def _get_adjustment_factor(self, request: BidRequest) -> float:
        """입찰 조정 계수"""
        factor = 1.0
        
        # 사용자 재방문 여부
        if request.user.get('id') in self._get_retargeting_users():
            factor *= 1.5
        
        # 프리미엄 사이트 가중치
        if request.site and request.site.get('domain') in self._get_premium_sites():
            factor *= 1.3
        
        return factor
    
    async def _get_ad_markup(self, imp: Dict, request: BidRequest) -> str:
        """광고 마크업 생성"""
        # 실제로는 크리에이티브 서버에서 가져옴
        return f"""
        <div style="width:{imp.get('banner', {}).get('w', 320)}px; 
                    height:{imp.get('banner', {}).get('h', 50)}px;">
            <a href="https://advertiser.com/landing" target="_blank">
                <img src="https://cdn.advertiser.com/creative.jpg" 
                     width="100%" height="100%" alt="광고">
            </a>
        </div>
        """
    
    def _get_retargeting_users(self) -> set:
        """리타겟팅 사용자 목록"""
        return {"user123", "user456", "user789"}
    
    def _get_premium_sites(self) -> set:
        """프리미엄 사이트 목록"""
        return {"naver.com", "daum.net", "google.com"}
    
    def _log_bid(self, request: BidRequest, response: BidResponse):
        """입찰 로그 저장"""
        self.bid_history.append({
            'timestamp': request.timestamp,
            'request_id': request.id,
            'bids_count': len(response.seatbid[0]['bid']) if response.seatbid else 0,
            'total_bid_value': sum(
                bid['price'] for bid in response.seatbid[0]['bid']
            ) if response.seatbid else 0
        })
```

### 광고 거래소 (Ad Exchange) 구현
```python
import asyncio
import aioredis
from aiohttp import web
import json
from typing import Dict, List
import uuid

class AdExchange:
    """광고 거래소"""
    
    def __init__(self):
        self.bidders = {}  # 등록된 DSP들
        self.redis = None
        self.auction_timeout = 0.1  # 100ms
        
    async def initialize(self):
        """초기화"""
        self.redis = await aioredis.create_redis_pool('redis://localhost')
    
    def register_bidder(self, bidder_id: str, endpoint: str, timeout_ms: int = 100):
        """DSP 등록"""
        self.bidders[bidder_id] = {
            'endpoint': endpoint,
            'timeout': timeout_ms / 1000,
            'active': True,
            'qps_limit': 1000  # 초당 요청 제한
        }
    
    async def conduct_auction(self, request_data: Dict) -> Dict:
        """경매 진행"""
        auction_id = str(uuid.uuid4())
        
        try:
            # 1. 입찰 요청 생성
            bid_request = self._prepare_bid_request(request_data, auction_id)
            
            # 2. 병렬 입찰 요청
            bid_responses = await self._send_bid_requests(bid_request)
            
            # 3. 입찰 검증
            valid_bids = self._validate_bids(bid_responses)
            
            # 4. 경매 진행 (Second Price Auction)
            auction_result = self._run_auction(valid_bids)
            
            # 5. 결과 저장
            await self._store_auction_result(auction_id, auction_result)
            
            return auction_result
            
        except Exception as e:
            print(f"Auction error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _prepare_bid_request(self, request_data: Dict, auction_id: str) -> Dict:
        """입찰 요청 준비"""
        bid_request = {
            'id': auction_id,
            'imp': request_data['impressions'],
            'device': request_data.get('device', {}),
            'user': request_data.get('user', {}),
            'site': request_data.get('site'),
            'app': request_data.get('app'),
            'tmax': int(self.auction_timeout * 1000)  # ms 단위
        }
        
        return bid_request
    
    async def _send_bid_requests(self, bid_request: Dict) -> List[Dict]:
        """병렬 입찰 요청 전송"""
        tasks = []
        
        for bidder_id, config in self.bidders.items():
            if config['active']:
                task = self._send_single_bid_request(bidder_id, config, bid_request)
                tasks.append(task)
        
        # 타임아웃과 함께 실행
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 예외 처리
        valid_responses = []
        for response in responses:
            if isinstance(response, dict) and 'seatbid' in response:
                valid_responses.append(response)
        
        return valid_responses
    
    async def _send_single_bid_request(self, bidder_id: str, config: Dict, 
                                     bid_request: Dict) -> Optional[Dict]:
        """단일 DSP로 입찰 요청"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config['endpoint'],
                    json=bid_request,
                    timeout=aiohttp.ClientTimeout(total=config['timeout'])
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        data['bidder_id'] = bidder_id
                        return data
                    else:
                        print(f"Bidder {bidder_id} returned status {response.status}")
                        return None
        except asyncio.TimeoutError:
            print(f"Bidder {bidder_id} timeout")
            return None
        except Exception as e:
            print(f"Bidder {bidder_id} error: {e}")
            return None
    
    def _validate_bids(self, responses: List[Dict]) -> List[Dict]:
        """입찰 검증"""
        valid_bids = []
        
        for response in responses:
            if not response or 'seatbid' not in response:
                continue
                
            for seatbid in response['seatbid']:
                for bid in seatbid.get('bid', []):
                    # 입찰가 검증
                    if bid.get('price', 0) <= 0:
                        continue
                    
                    # 광고 마크업 검증
                    if not bid.get('adm'):
                        continue
                    
                    # 크리에이티브 ID 검증
                    if not bid.get('crid'):
                        continue
                    
                    bid['bidder_id'] = response['bidder_id']
                    valid_bids.append(bid)
        
        return valid_bids
    
    def _run_auction(self, bids: List[Dict]) -> Dict:
        """Second Price Auction 진행"""
        if not bids:
            return {'status': 'no_bid'}
        
        # impression ID별로 그룹화
        imp_bids = {}
        for bid in bids:
            imp_id = bid['impid']
            if imp_id not in imp_bids:
                imp_bids[imp_id] = []
            imp_bids[imp_id].append(bid)
        
        winners = []
        
        for imp_id, imp_bid_list in imp_bids.items():
            # 입찰가 기준 정렬
            sorted_bids = sorted(imp_bid_list, key=lambda x: x['price'], reverse=True)
            
            if len(sorted_bids) >= 2:
                # Second Price: 두 번째 높은 가격
                winning_price = sorted_bids[1]['price']
            else:
                # 입찰자가 1명뿐이면 최저 입찰가
                winning_price = max(sorted_bids[0]['price'] * 0.8, 100)
            
            winner = sorted_bids[0].copy()
            winner['winning_price'] = winning_price
            winners.append(winner)
        
        return {
            'status': 'success',
            'winners': winners,
            'total_impressions': len(winners),
            'total_revenue': sum(w['winning_price'] for w in winners)
        }
    
    async def _store_auction_result(self, auction_id: str, result: Dict):
        """경매 결과 저장"""
        await self.redis.setex(
            f"auction:{auction_id}",
            3600,  # 1시간 보관
            json.dumps(result)
        )
    
    async def notify_winner(self, auction_id: str, winner_bid: Dict):
        """낙찰 알림"""
        # 실시간 낙찰 알림을 DSP에게 전송
        bidder_config = self.bidders.get(winner_bid['bidder_id'])
        if not bidder_config:
            return
        
        notification = {
            'auction_id': auction_id,
            'bid_id': winner_bid['id'],
            'winning_price': winner_bid['winning_price'],
            'impression_id': winner_bid['impid']
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    bidder_config['endpoint'] + '/win',
                    json=notification
                )
        except Exception as e:
            print(f"Win notification failed: {e}")
```

### DSP (Demand Side Platform) 구현
```python
class DSPlatform:
    """수요측 플랫폼"""
    
    def __init__(self, dsp_id: str):
        self.dsp_id = dsp_id
        self.campaigns = {}
        self.budgets = {}
        self.targeting_rules = {}
        self.performance_data = {}
        
    def create_campaign(self, campaign_config: Dict) -> str:
        """캠페인 생성"""
        campaign_id = str(uuid.uuid4())
        
        self.campaigns[campaign_id] = {
            'id': campaign_id,
            'name': campaign_config['name'],
            'advertiser_id': campaign_config['advertiser_id'],
            'status': 'active',
            'start_date': campaign_config['start_date'],
            'end_date': campaign_config['end_date'],
            'creatives': campaign_config['creatives'],
            'max_bid': campaign_config.get('max_bid', 1000)
        }
        
        self.budgets[campaign_id] = {
            'daily_budget': campaign_config['daily_budget'],
            'total_budget': campaign_config['total_budget'],
            'spent_today': 0,
            'spent_total': 0
        }
        
        self.targeting_rules[campaign_id] = campaign_config.get('targeting', {})
        
        return campaign_id
    
    async def handle_bid_request(self, request: BidRequest) -> Optional[BidResponse]:
        """입찰 요청 처리"""
        eligible_campaigns = await self._find_eligible_campaigns(request)
        
        if not eligible_campaigns:
            return None
        
        bids = []
        
        for campaign_id in eligible_campaigns:
            campaign = self.campaigns[campaign_id]
            
            # 예산 확인
            if not self._check_budget(campaign_id):
                continue
            
            # 입찰가 계산
            bid_price = await self._calculate_campaign_bid(campaign_id, request)
            
            if bid_price <= 0:
                continue
            
            # 크리에이티브 선택
            creative = self._select_creative(campaign_id, request)
            
            bid = {
                'id': f"bid_{campaign_id}_{request.id}",
                'impid': request.imp[0]['id'],  # 첫 번째 impression
                'price': bid_price,
                'adm': creative['markup'],
                'crid': creative['id'],
                'cid': campaign_id
            }
            
            bids.append(bid)
        
        if not bids:
            return None
        
        return BidResponse(
            id=request.id,
            seatbid=[{
                'bid': bids,
                'seat': self.dsp_id
            }]
        )
    
    async def _find_eligible_campaigns(self, request: BidRequest) -> List[str]:
        """타겟팅 조건에 맞는 캠페인 찾기"""
        eligible = []
        
        for campaign_id, campaign in self.campaigns.items():
            if campaign['status'] != 'active':
                continue
            
            # 날짜 검증
            current_date = datetime.now().date()
            if not (campaign['start_date'] <= current_date <= campaign['end_date']):
                continue
            
            # 타겟팅 규칙 검증
            if await self._check_targeting(campaign_id, request):
                eligible.append(campaign_id)
        
        return eligible
    
    async def _check_targeting(self, campaign_id: str, request: BidRequest) -> bool:
        """타겟팅 조건 검증"""
        rules = self.targeting_rules.get(campaign_id, {})
        
        # 지역 타겟팅
        if 'geo' in rules and request.geo:
            allowed_countries = rules['geo'].get('countries', [])
            if request.geo.get('country') not in allowed_countries:
                return False
        
        # 디바이스 타겟팅
        if 'device' in rules and request.device:
            allowed_types = rules['device'].get('types', [])
            if request.device.get('devicetype') not in allowed_types:
                return False
        
        # 사이트/앱 타겟팅
        if 'site' in rules and request.site:
            allowed_domains = rules['site'].get('domains', [])
            site_domain = request.site.get('domain', '')
            if not any(domain in site_domain for domain in allowed_domains):
                return False
        
        return True
    
    def _check_budget(self, campaign_id: str) -> bool:
        """예산 확인"""
        budget = self.budgets[campaign_id]
        
        # 일일 예산 확인
        if budget['spent_today'] >= budget['daily_budget']:
            return False
        
        # 총 예산 확인
        if budget['spent_total'] >= budget['total_budget']:
            return False
        
        return True
    
    async def _calculate_campaign_bid(self, campaign_id: str, request: BidRequest) -> float:
        """캠페인별 입찰가 계산"""
        campaign = self.campaigns[campaign_id]
        max_bid = campaign['max_bid']
        
        # 성과 데이터 기반 조정
        performance = self.performance_data.get(campaign_id, {})
        avg_ctr = performance.get('ctr', 0.02)
        avg_cvr = performance.get('cvr', 0.05)
        
        # 예상 가치 계산
        expected_value = avg_ctr * avg_cvr * 10000  # 가정: 전환당 가치 10,000원
        
        # 최대 입찰가의 80% 내에서 조정
        bid_price = min(expected_value, max_bid * 0.8)
        
        return max(bid_price, 100)  # 최소 100원
    
    def _select_creative(self, campaign_id: str, request: BidRequest) -> Dict:
        """크리에이티브 선택"""
        campaign = self.campaigns[campaign_id]
        creatives = campaign['creatives']
        
        # 간단한 라운드 로빈 선택
        creative_index = hash(request.id) % len(creatives)
        return creatives[creative_index]
```

## 🚀 프로젝트
1. **실시간 입찰 시스템 (RTB)**
2. **광고 거래소 플랫폼**
3. **DSP 대시보드 및 캠페인 관리**
4. **프로그래매틱 성과 분석 도구**