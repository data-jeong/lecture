# 22. Redis Caching - 레디스 캐싱

## 📚 과정 소개
Redis를 활용한 광고 플랫폼의 고성능 캐싱 시스템을 마스터합니다. 실시간 입찰, 사용자 프로필, 캠페인 데이터의 효율적인 캐싱 전략을 학습합니다.

## 🎯 학습 목표
- 광고 플랫폼 캐싱 아키텍처 설계
- 실시간 입찰 데이터 캐싱
- 사용자 세션 및 프로필 관리
- 캐시 성능 최적화 및 모니터링

## 📖 주요 내용

### Redis 기반 광고 캐싱 시스템
```python
import redis
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import pickle
import hashlib
import threading
from contextlib import contextmanager
import logging
from enum import Enum

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """캐시 전략"""
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"
    WRITE_AROUND = "write_around"
    CACHE_ASIDE = "cache_aside"

@dataclass
class CacheConfig:
    """캐시 설정"""
    default_ttl: int = 3600  # 1시간
    max_connections: int = 100
    decode_responses: bool = True
    retry_on_timeout: bool = True

@dataclass
class UserProfile:
    """사용자 프로필"""
    user_id: str
    interests: List[str]
    demographics: Dict[str, Any]
    behavior_score: float
    last_activity: datetime
    segment: str

@dataclass
class CampaignData:
    """캠페인 데이터"""
    campaign_id: str
    advertiser_id: str
    budget: float
    spent: float
    bid_price: float
    targeting: Dict[str, Any]
    status: str
    start_date: datetime
    end_date: datetime

class RedisAdCache:
    """Redis 광고 캐시 관리자"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, 
                 db: int = 0, password: Optional[str] = None,
                 config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        
        # Redis 연결 풀 설정
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=self.config.max_connections,
            decode_responses=self.config.decode_responses,
            retry_on_timeout=self.config.retry_on_timeout
        )
        
        self.redis_client = redis.Redis(connection_pool=self.pool)
        self.lua_scripts = self._load_lua_scripts()
        
        # 키 패턴 정의
        self.key_patterns = {
            'user_profile': 'user:profile:{user_id}',
            'campaign': 'campaign:{campaign_id}',
            'bid_request': 'bid:request:{request_id}',
            'user_session': 'session:{session_id}',
            'frequency_cap': 'freq:cap:{user_id}:{campaign_id}',
            'real_time_bid': 'rtb:{auction_id}',
            'performance_stats': 'stats:{campaign_id}:{date}',
            'user_segments': 'segments:{segment_id}',
            'ad_creative': 'creative:{creative_id}',
            'targeting_index': 'targeting:{interest}:{location}'
        }
        
        logger.info("Redis Ad Cache initialized")
    
    def _load_lua_scripts(self) -> Dict[str, Any]:
        """Lua 스크립트 로드"""
        scripts = {}
        
        # 빈도 제한 스크립트
        frequency_cap_script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local current_time = tonumber(ARGV[3])
        
        -- 현재 카운트 가져오기
        local current = redis.call('GET', key)
        if current == false then
            current = 0
        else
            current = tonumber(current)
        end
        
        -- 제한 확인
        if current >= limit then
            return 0  -- 제한 초과
        end
        
        -- 카운트 증가 및 TTL 설정
        redis.call('INCR', key)
        redis.call('EXPIRE', key, window)
        
        return 1  -- 허용
        """
        
        scripts['frequency_cap'] = self.redis_client.register_script(frequency_cap_script)
        
        # 실시간 입찰 스크립트
        rtb_auction_script = """
        local auction_key = KEYS[1]
        local bid_price = tonumber(ARGV[1])
        local campaign_id = ARGV[2]
        local ttl = tonumber(ARGV[3])
        
        -- 현재 최고 입찰가 확인
        local current_bid = redis.call('HGET', auction_key, 'highest_bid')
        if current_bid == false then
            current_bid = 0
        else
            current_bid = tonumber(current_bid)
        end
        
        -- 더 높은 입찰가인 경우 업데이트
        if bid_price > current_bid then
            redis.call('HSET', auction_key, 'highest_bid', bid_price)
            redis.call('HSET', auction_key, 'winning_campaign', campaign_id)
            redis.call('EXPIRE', auction_key, ttl)
            return 1  -- 낙찰
        end
        
        return 0  -- 낙찰 실패
        """
        
        scripts['rtb_auction'] = self.redis_client.register_script(rtb_auction_script)
        
        return scripts
    
    @contextmanager
    def get_client(self):
        """Redis 클라이언트 컨텍스트 매니저"""
        client = self.redis_client
        try:
            yield client
        except redis.RedisError as e:
            logger.error(f"Redis error: {e}")
            raise
        finally:
            # 연결 풀 사용으로 명시적 종료 불필요
            pass
    
    def get_key(self, pattern: str, **kwargs) -> str:
        """키 패턴으로 실제 키 생성"""
        if pattern in self.key_patterns:
            return self.key_patterns[pattern].format(**kwargs)
        return pattern.format(**kwargs)

class UserProfileCache:
    """사용자 프로필 캐시"""
    
    def __init__(self, redis_cache: RedisAdCache):
        self.cache = redis_cache
        
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """사용자 프로필 조회"""
        key = self.cache.get_key('user_profile', user_id=user_id)
        
        with self.cache.get_client() as client:
            profile_data = client.hgetall(key)
            
            if not profile_data:
                return None
            
            # JSON 문자열을 파이썬 객체로 변환
            return UserProfile(
                user_id=profile_data['user_id'],
                interests=json.loads(profile_data['interests']),
                demographics=json.loads(profile_data['demographics']),
                behavior_score=float(profile_data['behavior_score']),
                last_activity=datetime.fromisoformat(profile_data['last_activity']),
                segment=profile_data['segment']
            )
    
    def set_user_profile(self, profile: UserProfile, ttl: int = 3600):
        """사용자 프로필 저장"""
        key = self.cache.get_key('user_profile', user_id=profile.user_id)
        
        profile_data = {
            'user_id': profile.user_id,
            'interests': json.dumps(profile.interests),
            'demographics': json.dumps(profile.demographics),
            'behavior_score': profile.behavior_score,
            'last_activity': profile.last_activity.isoformat(),
            'segment': profile.segment
        }
        
        with self.cache.get_client() as client:
            pipe = client.pipeline()
            pipe.hset(key, mapping=profile_data)
            pipe.expire(key, ttl)
            pipe.execute()
            
        logger.info(f"User profile cached: {profile.user_id}")
    
    def update_user_activity(self, user_id: str, activity_data: Dict[str, Any]):
        """사용자 활동 업데이트"""
        key = self.cache.get_key('user_profile', user_id=user_id)
        
        with self.cache.get_client() as client:
            # 마지막 활동 시간 업데이트
            client.hset(key, 'last_activity', datetime.now().isoformat())
            
            # 행동 점수 업데이트 (간단한 로직)
            current_score = client.hget(key, 'behavior_score')
            if current_score:
                new_score = float(current_score) + activity_data.get('score_delta', 0)
                client.hset(key, 'behavior_score', new_score)
    
    def get_users_by_segment(self, segment: str, limit: int = 100) -> List[str]:
        """세그먼트별 사용자 조회"""
        segment_key = self.cache.get_key('user_segments', segment_id=segment)
        
        with self.cache.get_client() as client:
            return client.lrange(segment_key, 0, limit-1)
    
    def add_user_to_segment(self, user_id: str, segment: str):
        """사용자를 세그먼트에 추가"""
        segment_key = self.cache.get_key('user_segments', segment_id=segment)
        
        with self.cache.get_client() as client:
            client.lpush(segment_key, user_id)
            client.expire(segment_key, 86400)  # 24시간

class CampaignCache:
    """캠페인 캐시"""
    
    def __init__(self, redis_cache: RedisAdCache):
        self.cache = redis_cache
        
    def get_campaign(self, campaign_id: str) -> Optional[CampaignData]:
        """캠페인 데이터 조회"""
        key = self.cache.get_key('campaign', campaign_id=campaign_id)
        
        with self.cache.get_client() as client:
            campaign_data = client.hgetall(key)
            
            if not campaign_data:
                return None
            
            return CampaignData(
                campaign_id=campaign_data['campaign_id'],
                advertiser_id=campaign_data['advertiser_id'],
                budget=float(campaign_data['budget']),
                spent=float(campaign_data['spent']),
                bid_price=float(campaign_data['bid_price']),
                targeting=json.loads(campaign_data['targeting']),
                status=campaign_data['status'],
                start_date=datetime.fromisoformat(campaign_data['start_date']),
                end_date=datetime.fromisoformat(campaign_data['end_date'])
            )
    
    def set_campaign(self, campaign: CampaignData, ttl: int = 7200):
        """캠페인 데이터 저장"""
        key = self.cache.get_key('campaign', campaign_id=campaign.campaign_id)
        
        campaign_data = {
            'campaign_id': campaign.campaign_id,
            'advertiser_id': campaign.advertiser_id,
            'budget': campaign.budget,
            'spent': campaign.spent,
            'bid_price': campaign.bid_price,
            'targeting': json.dumps(campaign.targeting),
            'status': campaign.status,
            'start_date': campaign.start_date.isoformat(),
            'end_date': campaign.end_date.isoformat()
        }
        
        with self.cache.get_client() as client:
            pipe = client.pipeline()
            pipe.hset(key, mapping=campaign_data)
            pipe.expire(key, ttl)
            pipe.execute()
            
        logger.info(f"Campaign cached: {campaign.campaign_id}")
    
    def update_campaign_spend(self, campaign_id: str, spend_amount: float):
        """캠페인 지출 업데이트"""
        key = self.cache.get_key('campaign', campaign_id=campaign_id)
        
        with self.cache.get_client() as client:
            client.hincrbyfloat(key, 'spent', spend_amount)
    
    def get_active_campaigns(self, targeting_criteria: Dict[str, Any]) -> List[str]:
        """타겟팅 조건에 맞는 활성 캠페인 조회"""
        results = []
        
        # 관심사 기반 인덱스
        for interest in targeting_criteria.get('interests', []):
            index_key = self.cache.get_key('targeting_index', 
                                         interest=interest, 
                                         location=targeting_criteria.get('location', 'all'))
            
            with self.cache.get_client() as client:
                campaign_ids = client.smembers(index_key)
                results.extend(campaign_ids)
        
        return list(set(results))  # 중복 제거
    
    def index_campaign_targeting(self, campaign_id: str, targeting: Dict[str, Any]):
        """캠페인 타겟팅 인덱싱"""
        with self.cache.get_client() as client:
            pipe = client.pipeline()
            
            # 관심사별 인덱싱
            for interest in targeting.get('interests', []):
                for location in targeting.get('locations', ['all']):
                    index_key = self.cache.get_key('targeting_index', 
                                                 interest=interest, 
                                                 location=location)
                    pipe.sadd(index_key, campaign_id)
                    pipe.expire(index_key, 86400)  # 24시간
            
            pipe.execute()

class RealTimeBiddingCache:
    """실시간 입찰 캐시"""
    
    def __init__(self, redis_cache: RedisAdCache):
        self.cache = redis_cache
        
    def create_auction(self, auction_id: str, floor_price: float, ttl: int = 120):
        """경매 생성"""
        key = self.cache.get_key('real_time_bid', auction_id=auction_id)
        
        auction_data = {
            'auction_id': auction_id,
            'floor_price': floor_price,
            'highest_bid': 0,
            'winning_campaign': '',
            'created_at': datetime.now().isoformat()
        }
        
        with self.cache.get_client() as client:
            pipe = client.pipeline()
            pipe.hset(key, mapping=auction_data)
            pipe.expire(key, ttl)  # 2분 TTL
            pipe.execute()
            
        logger.info(f"Auction created: {auction_id}")
    
    def submit_bid(self, auction_id: str, campaign_id: str, bid_price: float) -> bool:
        """입찰 제출"""
        key = self.cache.get_key('real_time_bid', auction_id=auction_id)
        
        # Lua 스크립트를 사용한 원자적 입찰 처리
        result = self.cache.lua_scripts['rtb_auction'](
            keys=[key],
            args=[bid_price, campaign_id, 120]
        )
        
        if result == 1:
            logger.info(f"Bid won: {campaign_id} - {bid_price}")
            return True
        else:
            logger.info(f"Bid lost: {campaign_id} - {bid_price}")
            return False
    
    def get_auction_winner(self, auction_id: str) -> Optional[Dict[str, Any]]:
        """경매 낙찰자 조회"""
        key = self.cache.get_key('real_time_bid', auction_id=auction_id)
        
        with self.cache.get_client() as client:
            auction_data = client.hgetall(key)
            
            if not auction_data or not auction_data.get('winning_campaign'):
                return None
            
            return {
                'campaign_id': auction_data['winning_campaign'],
                'winning_bid': float(auction_data['highest_bid']),
                'auction_id': auction_id
            }
    
    def close_auction(self, auction_id: str):
        """경매 종료"""
        key = self.cache.get_key('real_time_bid', auction_id=auction_id)
        
        with self.cache.get_client() as client:
            client.delete(key)

class FrequencyCapManager:
    """빈도 제한 관리"""
    
    def __init__(self, redis_cache: RedisAdCache):
        self.cache = redis_cache
        
    def check_frequency_cap(self, user_id: str, campaign_id: str, 
                           limit: int = 3, window: int = 86400) -> bool:
        """빈도 제한 확인"""
        key = self.cache.get_key('frequency_cap', 
                               user_id=user_id, 
                               campaign_id=campaign_id)
        
        current_time = int(time.time())
        
        # Lua 스크립트를 사용한 원자적 카운팅
        result = self.cache.lua_scripts['frequency_cap'](
            keys=[key],
            args=[limit, window, current_time]
        )
        
        return result == 1  # 1이면 허용, 0이면 제한 초과
    
    def reset_frequency_cap(self, user_id: str, campaign_id: str):
        """빈도 제한 리셋"""
        key = self.cache.get_key('frequency_cap', 
                               user_id=user_id, 
                               campaign_id=campaign_id)
        
        with self.cache.get_client() as client:
            client.delete(key)

class SessionManager:
    """세션 관리"""
    
    def __init__(self, redis_cache: RedisAdCache):
        self.cache = redis_cache
        
    def create_session(self, session_id: str, user_data: Dict[str, Any], 
                      ttl: int = 1800) -> str:
        """세션 생성"""
        key = self.cache.get_key('user_session', session_id=session_id)
        
        session_data = {
            'session_id': session_id,
            'user_id': user_data.get('user_id', ''),
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'user_agent': user_data.get('user_agent', ''),
            'ip_address': user_data.get('ip_address', ''),
            'data': json.dumps(user_data)
        }
        
        with self.cache.get_client() as client:
            pipe = client.pipeline()
            pipe.hset(key, mapping=session_data)
            pipe.expire(key, ttl)  # 30분 TTL
            pipe.execute()
            
        logger.info(f"Session created: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 조회"""
        key = self.cache.get_key('user_session', session_id=session_id)
        
        with self.cache.get_client() as client:
            session_data = client.hgetall(key)
            
            if not session_data:
                return None
            
            return {
                'session_id': session_data['session_id'],
                'user_id': session_data['user_id'],
                'created_at': datetime.fromisoformat(session_data['created_at']),
                'last_activity': datetime.fromisoformat(session_data['last_activity']),
                'user_agent': session_data['user_agent'],
                'ip_address': session_data['ip_address'],
                'data': json.loads(session_data['data'])
            }
    
    def update_session_activity(self, session_id: str):
        """세션 활동 업데이트"""
        key = self.cache.get_key('user_session', session_id=session_id)
        
        with self.cache.get_client() as client:
            client.hset(key, 'last_activity', datetime.now().isoformat())
            client.expire(key, 1800)  # TTL 갱신
    
    def delete_session(self, session_id: str):
        """세션 삭제"""
        key = self.cache.get_key('user_session', session_id=session_id)
        
        with self.cache.get_client() as client:
            client.delete(key)

class PerformanceStatsCache:
    """성과 통계 캐시"""
    
    def __init__(self, redis_cache: RedisAdCache):
        self.cache = redis_cache
        
    def increment_stat(self, campaign_id: str, metric: str, value: float = 1.0, 
                      date: Optional[str] = None):
        """통계 증가"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        key = self.cache.get_key('performance_stats', 
                               campaign_id=campaign_id, 
                               date=date)
        
        with self.cache.get_client() as client:
            client.hincrbyfloat(key, metric, value)
            client.expire(key, 86400 * 7)  # 7일 보관
    
    def get_daily_stats(self, campaign_id: str, date: Optional[str] = None) -> Dict[str, float]:
        """일별 통계 조회"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        key = self.cache.get_key('performance_stats', 
                               campaign_id=campaign_id, 
                               date=date)
        
        with self.cache.get_client() as client:
            stats = client.hgetall(key)
            return {k: float(v) for k, v in stats.items()}
    
    def get_campaign_summary(self, campaign_id: str, days: int = 7) -> Dict[str, Any]:
        """캠페인 요약 통계"""
        summary = {
            'impressions': 0,
            'clicks': 0,
            'conversions': 0,
            'cost': 0.0,
            'revenue': 0.0
        }
        
        # 최근 N일간 데이터 집계
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_stats = self.get_daily_stats(campaign_id, date)
            
            for metric in summary:
                summary[metric] += daily_stats.get(metric, 0)
        
        # 파생 지표 계산
        if summary['impressions'] > 0:
            summary['ctr'] = summary['clicks'] / summary['impressions']
        else:
            summary['ctr'] = 0.0
            
        if summary['clicks'] > 0:
            summary['cvr'] = summary['conversions'] / summary['clicks']
            summary['cpc'] = summary['cost'] / summary['clicks']
        else:
            summary['cvr'] = 0.0
            summary['cpc'] = 0.0
            
        if summary['cost'] > 0:
            summary['roas'] = summary['revenue'] / summary['cost']
        else:
            summary['roas'] = 0.0
        
        return summary

class CacheMonitor:
    """캐시 모니터링"""
    
    def __init__(self, redis_cache: RedisAdCache):
        self.cache = redis_cache
        self.monitoring = False
        
    def start_monitoring(self, interval: int = 60):
        """모니터링 시작"""
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    stats = self.get_cache_stats()
                    self._log_stats(stats)
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(interval)
        
        monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitoring_thread.start()
        logger.info("Cache monitoring started")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring = False
        logger.info("Cache monitoring stopped")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 조회"""
        with self.cache.get_client() as client:
            info = client.info()
            
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'expired_keys': info.get('expired_keys', 0),
                'evicted_keys': info.get('evicted_keys', 0),
                'total_commands_processed': info.get('total_commands_processed', 0)
            }
    
    def _log_stats(self, stats: Dict[str, Any]):
        """통계 로깅"""
        hit_rate = 0
        if stats['keyspace_hits'] + stats['keyspace_misses'] > 0:
            hit_rate = stats['keyspace_hits'] / (stats['keyspace_hits'] + stats['keyspace_misses'])
        
        logger.info(f"Cache Stats - Memory: {stats['used_memory_human']}, "
                   f"Clients: {stats['connected_clients']}, "
                   f"Hit Rate: {hit_rate:.2%}, "
                   f"Commands: {stats['total_commands_processed']}")
    
    def clear_expired_keys(self):
        """만료된 키 정리"""
        with self.cache.get_client() as client:
            # 패턴별로 만료된 키 정리
            for pattern_name, pattern in self.cache.key_patterns.items():
                if '*' not in pattern:
                    continue
                    
                # 패턴에 맞는 키들 찾기
                keys = client.keys(pattern.replace('{', '*').replace('}', '*'))
                
                expired_count = 0
                for key in keys:
                    ttl = client.ttl(key)
                    if ttl == -1:  # TTL이 없는 키
                        client.expire(key, 86400)  # 기본 24시간 TTL 설정
                    elif ttl == -2:  # 이미 만료된 키
                        expired_count += 1
                
                if expired_count > 0:
                    logger.info(f"Cleaned {expired_count} expired keys for pattern: {pattern_name}")

# 사용 예시
def example_redis_ad_caching():
    """Redis 광고 캐싱 예시"""
    # Redis 캐시 초기화
    cache_config = CacheConfig(default_ttl=3600, max_connections=50)
    redis_cache = RedisAdCache(host='localhost', port=6379, config=cache_config)
    
    # 각 캐시 매니저 초기화
    user_cache = UserProfileCache(redis_cache)
    campaign_cache = CampaignCache(redis_cache)
    rtb_cache = RealTimeBiddingCache(redis_cache)
    freq_manager = FrequencyCapManager(redis_cache)
    session_manager = SessionManager(redis_cache)
    stats_cache = PerformanceStatsCache(redis_cache)
    monitor = CacheMonitor(redis_cache)
    
    # 모니터링 시작
    monitor.start_monitoring(interval=30)
    
    # 샘플 데이터 생성 및 테스트
    try:
        # 사용자 프로필 캐싱 테스트
        print("=== User Profile Caching Test ===")
        user_profile = UserProfile(
            user_id='user_123',
            interests=['tech', 'gaming', 'sports'],
            demographics={'age': 28, 'gender': 'M', 'location': 'Seoul'},
            behavior_score=75.5,
            last_activity=datetime.now(),
            segment='high_value'
        )
        
        user_cache.set_user_profile(user_profile)
        cached_profile = user_cache.get_user_profile('user_123')
        print(f"Cached user profile: {cached_profile.user_id if cached_profile else 'None'}")
        
        # 캠페인 캐싱 테스트
        print("\n=== Campaign Caching Test ===")
        campaign = CampaignData(
            campaign_id='campaign_456',
            advertiser_id='advertiser_789',
            budget=10000.0,
            spent=2500.0,
            bid_price=2.5,
            targeting={'interests': ['tech', 'gaming'], 'age_range': [25, 35]},
            status='active',
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        campaign_cache.set_campaign(campaign)
        cached_campaign = campaign_cache.get_campaign('campaign_456')
        print(f"Cached campaign: {cached_campaign.campaign_id if cached_campaign else 'None'}")
        
        # 실시간 입찰 테스트
        print("\n=== Real-time Bidding Test ===")
        auction_id = str(uuid.uuid4())
        rtb_cache.create_auction(auction_id, floor_price=1.0)
        
        # 여러 입찰 제출
        bids = [
            ('campaign_456', 2.5),
            ('campaign_789', 3.0),
            ('campaign_101', 2.8)
        ]
        
        for campaign_id, bid_price in bids:
            won = rtb_cache.submit_bid(auction_id, campaign_id, bid_price)
            print(f"Bid {campaign_id}: ${bid_price} - {'WON' if won else 'LOST'}")
        
        winner = rtb_cache.get_auction_winner(auction_id)
        print(f"Auction winner: {winner}")
        
        # 빈도 제한 테스트
        print("\n=== Frequency Cap Test ===")
        for i in range(5):
            allowed = freq_manager.check_frequency_cap('user_123', 'campaign_456', limit=3)
            print(f"Ad request {i+1}: {'ALLOWED' if allowed else 'BLOCKED'}")
        
        # 세션 관리 테스트
        print("\n=== Session Management Test ===")
        session_id = str(uuid.uuid4())
        session_data = {
            'user_id': 'user_123',
            'user_agent': 'Mozilla/5.0',
            'ip_address': '192.168.1.1',
            'referrer': 'https://google.com'
        }
        
        session_manager.create_session(session_id, session_data)
        session = session_manager.get_session(session_id)
        print(f"Session created: {session['session_id'] if session else 'None'}")
        
        # 성과 통계 테스트
        print("\n=== Performance Stats Test ===")
        stats_cache.increment_stat('campaign_456', 'impressions', 100)
        stats_cache.increment_stat('campaign_456', 'clicks', 5)
        stats_cache.increment_stat('campaign_456', 'cost', 12.5)
        
        daily_stats = stats_cache.get_daily_stats('campaign_456')
        print(f"Daily stats: {daily_stats}")
        
        campaign_summary = stats_cache.get_campaign_summary('campaign_456', days=1)
        print(f"Campaign summary: {campaign_summary}")
        
        # 캐시 통계 확인
        print("\n=== Cache Statistics ===")
        cache_stats = monitor.get_cache_stats()
        print(f"Cache hit rate: {cache_stats.get('keyspace_hits', 0) / max(1, cache_stats.get('keyspace_hits', 0) + cache_stats.get('keyspace_misses', 0)):.2%}")
        print(f"Memory usage: {cache_stats.get('used_memory_human', '0B')}")
        
        # 성능 테스트
        print("\n=== Performance Test ===")
        start_time = time.time()
        
        for i in range(1000):
            user_cache.get_user_profile('user_123')
        
        end_time = time.time()
        print(f"1000 cache reads took: {(end_time - start_time)*1000:.2f}ms")
        
        return {
            'user_profile_cached': cached_profile is not None,
            'campaign_cached': cached_campaign is not None,
            'auction_winner': winner,
            'cache_performance_ms': (end_time - start_time) * 1000
        }
        
    except Exception as e:
        logger.error(f"Test error: {e}")
        return {'error': str(e)}
    
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    results = example_redis_ad_caching()
    print("Redis 광고 캐싱 테스트 완료!")
```

## 🚀 프로젝트
1. **고성능 실시간 입찰 캐시**
2. **사용자 프로필 캐싱 시스템**
3. **캠페인 성과 실시간 추적**
4. **세션 기반 타겟팅 엔진**