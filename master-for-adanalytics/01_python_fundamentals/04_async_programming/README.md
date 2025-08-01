# Chapter 04: Async Programming - 비동기 프로그래밍

## 📚 학습 목표
- 비동기 프로그래밍의 핵심 개념 이해
- asyncio를 활용한 동시성 처리
- 광고 API 통합 및 실시간 데이터 처리
- 고성능 광고 서버 구축

## 📖 이론: 비동기 프로그래밍 기초

### 1. 동기 vs 비동기

```python
import asyncio
import aiohttp
import time
from typing import List, Dict

# ❌ 동기 방식 - 순차적 처리
def sync_fetch_ad_metrics(campaign_ids: List[str]) -> List[Dict]:
    """동기 방식으로 광고 지표 조회"""
    results = []
    start = time.time()
    
    for campaign_id in campaign_ids:
        # 각 API 호출이 완료될 때까지 대기
        response = fetch_campaign_data(campaign_id)  # 2초 소요
        results.append(response)
    
    print(f"동기 처리 시간: {time.time() - start:.2f}초")
    return results

# ✅ 비동기 방식 - 동시 처리
async def async_fetch_ad_metrics(campaign_ids: List[str]) -> List[Dict]:
    """비동기 방식으로 광고 지표 조회"""
    start = time.time()
    
    # 모든 API 호출을 동시에 시작
    tasks = [fetch_campaign_data_async(cid) for cid in campaign_ids]
    results = await asyncio.gather(*tasks)
    
    print(f"비동기 처리 시간: {time.time() - start:.2f}초")
    return results

# 10개 캠페인 조회 시:
# 동기: 20초 (2초 × 10)
# 비동기: 2초 (병렬 처리)
```

### 2. 코루틴과 이벤트 루프

```python
import asyncio
from datetime import datetime

class AdEventLoop:
    """광고 이벤트 처리 시스템"""
    
    def __init__(self):
        self.events = asyncio.Queue()
        self.processed_count = 0
    
    async def impression_handler(self, event: Dict):
        """노출 이벤트 처리"""
        await asyncio.sleep(0.01)  # I/O 작업 시뮬레이션
        
        # 노출 검증
        if self._validate_impression(event):
            await self._record_impression(event)
            self.processed_count += 1
    
    async def click_handler(self, event: Dict):
        """클릭 이벤트 처리"""
        await asyncio.sleep(0.02)  # 더 복잡한 처리
        
        # 클릭 검증 및 기록
        if await self._validate_click(event):
            await self._record_click(event)
            await self._update_ctr(event)
            self.processed_count += 1
    
    async def conversion_handler(self, event: Dict):
        """전환 이벤트 처리"""
        await asyncio.sleep(0.05)  # 가장 복잡한 처리
        
        # 전환 어트리뷰션
        attribution = await self._calculate_attribution(event)
        await self._record_conversion(event, attribution)
        self.processed_count += 1
    
    async def event_dispatcher(self):
        """이벤트 디스패처"""
        handlers = {
            'impression': self.impression_handler,
            'click': self.click_handler,
            'conversion': self.conversion_handler
        }
        
        while True:
            try:
                # 이벤트 대기
                event = await asyncio.wait_for(
                    self.events.get(), 
                    timeout=1.0
                )
                
                # 적절한 핸들러로 전달
                event_type = event.get('type')
                if event_type in handlers:
                    # 논블로킹 처리
                    asyncio.create_task(handlers[event_type](event))
                
            except asyncio.TimeoutError:
                # 타임아웃 시 통계 출력
                if self.processed_count > 0:
                    print(f"처리된 이벤트: {self.processed_count}")
                    self.processed_count = 0
            except Exception as e:
                print(f"이벤트 처리 오류: {e}")
    
    async def _validate_impression(self, event: Dict) -> bool:
        """노출 유효성 검증"""
        # 비동기 검증 로직
        await asyncio.sleep(0.001)
        return event.get('ad_id') and event.get('user_id')
    
    async def _validate_click(self, event: Dict) -> bool:
        """클릭 유효성 검증"""
        # Redis에서 중복 확인
        async with aioredis.create_redis_pool('redis://localhost') as redis:
            key = f"click:{event['user_id']}:{event['ad_id']}"
            is_duplicate = await redis.exists(key)
            if not is_duplicate:
                await redis.setex(key, 3600, 1)  # 1시간 TTL
            return not is_duplicate
    
    async def _calculate_attribution(self, event: Dict) -> str:
        """전환 어트리뷰션 계산"""
        # 복잡한 어트리뷰션 로직
        await asyncio.sleep(0.01)
        return 'last_click'  # 단순화
    
    async def _record_impression(self, event: Dict):
        """노출 기록"""
        pass
    
    async def _record_click(self, event: Dict):
        """클릭 기록"""
        pass
    
    async def _update_ctr(self, event: Dict):
        """CTR 업데이트"""
        pass
    
    async def _record_conversion(self, event: Dict, attribution: str):
        """전환 기록"""
        pass
```

### 3. 비동기 컨텍스트 매니저

```python
import aiohttp
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any

class AsyncAdAPIClient:
    """비동기 광고 API 클라이언트"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limiter = asyncio.Semaphore(100)  # 동시 요청 제한
    
    async def __aenter__(self):
        """비동기 컨텍스트 진입"""
        self.session = aiohttp.ClientSession(
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 종료"""
        if self.session:
            await self.session.close()
    
    @asynccontextmanager
    async def rate_limited_request(self):
        """요청 속도 제한 컨텍스트"""
        async with self._rate_limiter:
            yield
    
    async def get_campaign(self, campaign_id: str) -> Dict:
        """캠페인 조회"""
        async with self.rate_limited_request():
            url = f"{self.base_url}/campaigns/{campaign_id}"
            
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.json()
    
    async def get_campaign_metrics(self, 
                                 campaign_id: str, 
                                 date_range: Dict) -> Dict:
        """캠페인 지표 조회"""
        async with self.rate_limited_request():
            url = f"{self.base_url}/campaigns/{campaign_id}/metrics"
            params = {
                'start_date': date_range['start'],
                'end_date': date_range['end']
            }
            
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
    
    async def create_ad(self, campaign_id: str, ad_data: Dict) -> Dict:
        """광고 생성"""
        async with self.rate_limited_request():
            url = f"{self.base_url}/campaigns/{campaign_id}/ads"
            
            async with self.session.post(url, json=ad_data) as response:
                response.raise_for_status()
                return await response.json()
    
    async def batch_update_bids(self, updates: List[Dict]) -> List[Dict]:
        """일괄 입찰가 업데이트"""
        tasks = []
        
        for update in updates:
            task = self._update_single_bid(
                update['ad_id'], 
                update['new_bid']
            )
            tasks.append(task)
        
        # 모든 업데이트 동시 실행
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 처리
        successful = []
        failed = []
        
        for update, result in zip(updates, results):
            if isinstance(result, Exception):
                failed.append({'ad_id': update['ad_id'], 'error': str(result)})
            else:
                successful.append(result)
        
        return {'successful': successful, 'failed': failed}
    
    async def _update_single_bid(self, ad_id: str, new_bid: float) -> Dict:
        """단일 입찰가 업데이트"""
        async with self.rate_limited_request():
            url = f"{self.base_url}/ads/{ad_id}/bid"
            
            async with self.session.patch(
                url, 
                json={'bid': new_bid}
            ) as response:
                response.raise_for_status()
                return await response.json()
```

## 🛠️ 실습: 실시간 광고 데이터 처리

### 실습 1: 비동기 웹 스크래핑

```python
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Set
import aiofiles
import json

class AsyncAdCompetitorScraper:
    """비동기 경쟁사 광고 스크래퍼"""
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session: Optional[aiohttp.ClientSession] = None
        self.scraped_ads: List[Dict] = []
    
    async def start_session(self):
        """세션 시작"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """세션 종료"""
        if self.session:
            await self.session.close()
    
    async def scrape_competitor_ads(self, 
                                  competitor_urls: List[str]) -> List[Dict]:
        """경쟁사 광고 스크래핑"""
        await self.start_session()
        
        try:
            # 모든 URL 동시 스크래핑
            tasks = [
                self._scrape_single_page(url) 
                for url in competitor_urls
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 성공한 결과만 수집
            for result in results:
                if isinstance(result, list):
                    self.scraped_ads.extend(result)
            
            return self.scraped_ads
            
        finally:
            await self.close_session()
    
    async def _scrape_single_page(self, url: str) -> List[Dict]:
        """단일 페이지 스크래핑"""
        async with self.semaphore:  # 동시 요청 제한
            try:
                async with self.session.get(url) as response:
                    if response.status != 200:
                        return []
                    
                    html = await response.text()
                    return await self._parse_ads(html, url)
                    
            except Exception as e:
                print(f"스크래핑 오류 {url}: {e}")
                return []
    
    async def _parse_ads(self, html: str, source_url: str) -> List[Dict]:
        """광고 파싱 (CPU 집약적 작업을 비동기로)"""
        loop = asyncio.get_event_loop()
        
        # BeautifulSoup 파싱을 별도 스레드에서 실행
        ads = await loop.run_in_executor(
            None, 
            self._parse_ads_sync, 
            html, 
            source_url
        )
        
        return ads
    
    def _parse_ads_sync(self, html: str, source_url: str) -> List[Dict]:
        """동기 파싱 함수"""
        soup = BeautifulSoup(html, 'html.parser')
        ads = []
        
        # 광고 요소 찾기 (예시)
        ad_elements = soup.find_all('div', class_='ad-container')
        
        for ad in ad_elements:
            ad_data = {
                'source_url': source_url,
                'title': ad.find('h3', class_='ad-title').text.strip(),
                'description': ad.find('p', class_='ad-desc').text.strip(),
                'cta': ad.find('button', class_='ad-cta').text.strip(),
                'image_url': ad.find('img')['src'] if ad.find('img') else None,
                'scraped_at': datetime.now().isoformat()
            }
            ads.append(ad_data)
        
        return ads
    
    async def save_results(self, filename: str):
        """결과 비동기 저장"""
        async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(
                self.scraped_ads, 
                ensure_ascii=False, 
                indent=2
            ))
```

### 실습 2: 실시간 입찰 스트림 처리

```python
import asyncio
import aioredis
import json
from typing import AsyncGenerator, Dict, Optional
from dataclasses import dataclass
import asyncio_mqtt as aiomqtt

@dataclass
class BidRequest:
    """입찰 요청"""
    request_id: str
    user_id: str
    ad_slot_id: str
    floor_price: float
    user_context: Dict
    timestamp: float

class AsyncRTBProcessor:
    """비동기 실시간 입찰 처리기"""
    
    def __init__(self, redis_url: str, mqtt_host: str):
        self.redis_url = redis_url
        self.mqtt_host = mqtt_host
        self.redis: Optional[aioredis.Redis] = None
        self.active_auctions: Dict[str, asyncio.Task] = {}
    
    async def setup(self):
        """초기 설정"""
        self.redis = await aioredis.create_redis_pool(self.redis_url)
    
    async def cleanup(self):
        """정리"""
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()
        
        # 활성 경매 취소
        for task in self.active_auctions.values():
            task.cancel()
    
    async def process_bid_stream(self):
        """입찰 스트림 처리"""
        async with aiomqtt.Client(self.mqtt_host) as client:
            async with client.filtered_messages("rtb/requests/+") as messages:
                await client.subscribe("rtb/requests/+")
                
                async for message in messages:
                    # 입찰 요청 파싱
                    bid_request = self._parse_bid_request(message.payload)
                    
                    # 비동기 경매 시작
                    auction_task = asyncio.create_task(
                        self._run_auction(bid_request)
                    )
                    
                    self.active_auctions[bid_request.request_id] = auction_task
    
    def _parse_bid_request(self, payload: bytes) -> BidRequest:
        """입찰 요청 파싱"""
        data = json.loads(payload.decode())
        return BidRequest(**data)
    
    async def _run_auction(self, request: BidRequest):
        """경매 실행"""
        try:
            # 1. 사용자 프로필 조회
            user_profile = await self._get_user_profile(request.user_id)
            
            # 2. 관련 광고주 찾기
            advertisers = await self._find_relevant_advertisers(
                user_profile, 
                request.user_context
            )
            
            # 3. 병렬 입찰 요청
            bid_tasks = [
                self._request_bid(advertiser, request, user_profile)
                for advertiser in advertisers
            ]
            
            # 4. 입찰 수집 (타임아웃 100ms)
            bids = await asyncio.wait_for(
                self._collect_bids(bid_tasks),
                timeout=0.1
            )
            
            # 5. 승자 결정
            winner = self._determine_winner(bids, request.floor_price)
            
            # 6. 결과 발행
            await self._publish_auction_result(request.request_id, winner)
            
        except asyncio.TimeoutError:
            # 타임아웃 처리
            await self._publish_timeout(request.request_id)
        except Exception as e:
            print(f"경매 오류: {e}")
        finally:
            # 완료된 경매 제거
            self.active_auctions.pop(request.request_id, None)
    
    async def _get_user_profile(self, user_id: str) -> Dict:
        """사용자 프로필 조회"""
        # Redis에서 캐시된 프로필 조회
        profile_key = f"user:profile:{user_id}"
        cached = await self.redis.get(profile_key)
        
        if cached:
            return json.loads(cached)
        
        # 캐시 미스 시 DB 조회 (시뮬레이션)
        profile = {
            'user_id': user_id,
            'interests': ['tech', 'sports'],
            'demographics': {'age': 25, 'gender': 'M'},
            'purchase_history': [],
            'ltv_score': 0.7
        }
        
        # 캐시 저장 (1시간 TTL)
        await self.redis.setex(
            profile_key, 
            3600, 
            json.dumps(profile)
        )
        
        return profile
    
    async def _find_relevant_advertisers(self, 
                                       user_profile: Dict,
                                       context: Dict) -> List[str]:
        """관련 광고주 찾기"""
        # 사용자 관심사 기반 광고주 매칭
        interests = set(user_profile.get('interests', []))
        
        # Redis에서 광고주 타겟팅 정보 조회
        advertiser_keys = await self.redis.keys('advertiser:targeting:*')
        relevant = []
        
        for key in advertiser_keys:
            targeting = await self.redis.get(key)
            if targeting:
                targeting_data = json.loads(targeting)
                target_interests = set(targeting_data.get('interests', []))
                
                # 관심사 매칭
                if interests & target_interests:
                    advertiser_id = key.decode().split(':')[-1]
                    relevant.append(advertiser_id)
        
        return relevant[:10]  # 최대 10개 광고주
    
    async def _request_bid(self, 
                         advertiser_id: str,
                         request: BidRequest,
                         user_profile: Dict) -> Optional[Dict]:
        """개별 광고주 입찰 요청"""
        try:
            # 광고주 입찰 엔드포인트 호출 (시뮬레이션)
            await asyncio.sleep(0.01)  # 네트워크 지연
            
            # 입찰 로직 (실제로는 광고주 서버에서 계산)
            base_bid = request.floor_price * 1.2
            ltv_multiplier = 1 + user_profile['ltv_score']
            
            bid_price = base_bid * ltv_multiplier
            
            return {
                'advertiser_id': advertiser_id,
                'bid_price': bid_price,
                'ad_id': f"ad_{advertiser_id}_{request.request_id[:8]}",
                'creative_url': f"https://cdn.example.com/{advertiser_id}/creative.jpg"
            }
            
        except Exception:
            return None
    
    async def _collect_bids(self, bid_tasks: List[asyncio.Task]) -> List[Dict]:
        """입찰 수집"""
        # 완료된 태스크 수집
        done, pending = await asyncio.wait(
            bid_tasks,
            return_when=asyncio.ALL_COMPLETED
        )
        
        bids = []
        for task in done:
            try:
                result = task.result()
                if result:
                    bids.append(result)
            except Exception:
                pass
        
        # 미완료 태스크 취소
        for task in pending:
            task.cancel()
        
        return bids
    
    def _determine_winner(self, bids: List[Dict], floor_price: float) -> Optional[Dict]:
        """승자 결정 (Second Price Auction)"""
        # floor price 이상인 입찰만 필터링
        valid_bids = [
            bid for bid in bids 
            if bid['bid_price'] >= floor_price
        ]
        
        if not valid_bids:
            return None
        
        # 가장 높은 입찰 찾기
        sorted_bids = sorted(
            valid_bids, 
            key=lambda x: x['bid_price'], 
            reverse=True
        )
        
        winner = sorted_bids[0].copy()
        
        # Second price 적용
        if len(sorted_bids) > 1:
            winner['clearing_price'] = sorted_bids[1]['bid_price'] + 0.01
        else:
            winner['clearing_price'] = floor_price
        
        return winner
    
    async def _publish_auction_result(self, 
                                    request_id: str, 
                                    winner: Optional[Dict]):
        """경매 결과 발행"""
        result = {
            'request_id': request_id,
            'status': 'success' if winner else 'no_bid',
            'winner': winner,
            'timestamp': time.time()
        }
        
        # Redis Pub/Sub으로 결과 발행
        await self.redis.publish(
            f'auction:results:{request_id}',
            json.dumps(result)
        )
    
    async def _publish_timeout(self, request_id: str):
        """타임아웃 발행"""
        result = {
            'request_id': request_id,
            'status': 'timeout',
            'timestamp': time.time()
        }
        
        await self.redis.publish(
            f'auction:results:{request_id}',
            json.dumps(result)
        )
```

### 실습 3: 비동기 배치 처리

```python
import asyncio
import aioboto3
from typing import List, AsyncIterator
import pandas as pd
import pyarrow.parquet as pq
import io

class AsyncAdDataProcessor:
    """비동기 광고 데이터 배치 처리기"""
    
    def __init__(self, aws_config: Dict):
        self.aws_config = aws_config
        self.processing_stats = {
            'files_processed': 0,
            'records_processed': 0,
            'errors': 0
        }
    
    async def process_daily_ad_data(self, date: str) -> Dict:
        """일별 광고 데이터 처리"""
        # S3에서 파일 목록 조회
        files = await self._list_s3_files(date)
        
        # 파일을 청크로 분할 (메모리 관리)
        chunks = [files[i:i+10] for i in range(0, len(files), 10)]
        
        # 청크별 병렬 처리
        for chunk in chunks:
            await self._process_chunk(chunk)
        
        # 최종 집계
        await self._run_final_aggregation(date)
        
        return self.processing_stats
    
    async def _list_s3_files(self, date: str) -> List[str]:
        """S3 파일 목록 조회"""
        async with aioboto3.Session().client('s3', **self.aws_config) as s3:
            paginator = s3.get_paginator('list_objects_v2')
            
            files = []
            async for page in paginator.paginate(
                Bucket='ad-data-bucket',
                Prefix=f'raw/{date}/'
            ):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        files.append(obj['Key'])
            
            return files
    
    async def _process_chunk(self, files: List[str]):
        """파일 청크 처리"""
        tasks = [self._process_single_file(f) for f in files]
        
        # 동시 처리
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 집계
        for result in results:
            if isinstance(result, Exception):
                self.processing_stats['errors'] += 1
                print(f"처리 오류: {result}")
    
    async def _process_single_file(self, file_key: str) -> Dict:
        """단일 파일 처리"""
        async with aioboto3.Session().client('s3', **self.aws_config) as s3:
            # 파일 다운로드
            response = await s3.get_object(
                Bucket='ad-data-bucket',
                Key=file_key
            )
            
            # 스트리밍 읽기
            content = await response['Body'].read()
            
            # Parquet 파일 처리
            df = await self._read_parquet_async(content)
            
            # 데이터 변환
            transformed = await self._transform_ad_data(df)
            
            # 처리된 데이터 저장
            await self._save_processed_data(transformed, file_key)
            
            self.processing_stats['files_processed'] += 1
            self.processing_stats['records_processed'] += len(df)
            
            return {'file': file_key, 'records': len(df)}
    
    async def _read_parquet_async(self, content: bytes) -> pd.DataFrame:
        """비동기 Parquet 읽기"""
        loop = asyncio.get_event_loop()
        
        # CPU 집약적 작업을 별도 스레드에서 실행
        df = await loop.run_in_executor(
            None,
            lambda: pq.read_table(io.BytesIO(content)).to_pandas()
        )
        
        return df
    
    async def _transform_ad_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """광고 데이터 변환"""
        loop = asyncio.get_event_loop()
        
        # 변환 작업을 별도 스레드에서 실행
        transformed = await loop.run_in_executor(
            None,
            self._transform_sync,
            df
        )
        
        return transformed
    
    def _transform_sync(self, df: pd.DataFrame) -> pd.DataFrame:
        """동기 변환 함수"""
        # CTR 계산
        df['ctr'] = df['clicks'] / df['impressions'].replace(0, 1)
        
        # CPC 계산
        df['cpc'] = df['cost'] / df['clicks'].replace(0, 1)
        
        # ROAS 계산
        df['roas'] = df['revenue'] / df['cost'].replace(0, 1)
        
        # 이상치 필터링
        df = df[
            (df['ctr'] <= 1.0) & 
            (df['cpc'] >= 0) & 
            (df['roas'] >= 0)
        ]
        
        return df
    
    async def _save_processed_data(self, df: pd.DataFrame, original_key: str):
        """처리된 데이터 저장"""
        # 새 키 생성
        new_key = original_key.replace('raw/', 'processed/')
        
        # Parquet으로 변환
        buffer = io.BytesIO()
        df.to_parquet(buffer, engine='pyarrow')
        buffer.seek(0)
        
        # S3에 업로드
        async with aioboto3.Session().client('s3', **self.aws_config) as s3:
            await s3.put_object(
                Bucket='ad-data-bucket',
                Key=new_key,
                Body=buffer.getvalue()
            )
    
    async def _run_final_aggregation(self, date: str):
        """최종 집계 실행"""
        # Athena 쿼리 실행
        query = f"""
        SELECT 
            campaign_id,
            SUM(impressions) as total_impressions,
            SUM(clicks) as total_clicks,
            SUM(conversions) as total_conversions,
            SUM(cost) as total_cost,
            SUM(revenue) as total_revenue,
            AVG(ctr) as avg_ctr,
            AVG(cpc) as avg_cpc,
            AVG(roas) as avg_roas
        FROM processed_ad_data
        WHERE date = '{date}'
        GROUP BY campaign_id
        """
        
        async with aioboto3.Session().client('athena', **self.aws_config) as athena:
            # 쿼리 실행
            response = await athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': 'ad_analytics'},
                ResultConfiguration={
                    'OutputLocation': 's3://ad-data-bucket/athena-results/'
                }
            )
            
            query_id = response['QueryExecutionId']
            
            # 쿼리 완료 대기
            await self._wait_for_query_completion(athena, query_id)
```

## 🚀 프로젝트: 실시간 광고 분석 대시보드

### 프로젝트 구조
```
real_time_ad_dashboard/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── websocket_server.py
│   ├── rest_endpoints.py
│   └── authentication.py
├── processors/
│   ├── __init__.py
│   ├── stream_processor.py
│   ├── aggregator.py
│   └── alerting.py
├── connectors/
│   ├── __init__.py
│   ├── facebook_ads.py
│   ├── google_ads.py
│   └── database.py
├── models/
│   ├── __init__.py
│   ├── metrics.py
│   └── predictions.py
└── main.py
```

### 메인 애플리케이션

```python
# main.py
import asyncio
import aiohttp
from aiohttp import web
import aioredis
import json
from datetime import datetime
import weakref

class RealTimeAdDashboard:
    """실시간 광고 대시보드 서버"""
    
    def __init__(self):
        self.app = web.Application()
        self.redis = None
        self.websockets = weakref.WeakSet()
        self.metrics_cache = {}
        self.setup_routes()
    
    def setup_routes(self):
        """라우트 설정"""
        self.app.router.add_get('/ws', self.websocket_handler)
        self.app.router.add_get('/api/campaigns', self.get_campaigns)
        self.app.router.add_get('/api/metrics/{campaign_id}', self.get_metrics)
        self.app.router.add_post('/api/alerts', self.create_alert)
    
    async def startup(self, app):
        """서버 시작 시 초기화"""
        # Redis 연결
        app['redis'] = await aioredis.create_redis_pool('redis://localhost')
        self.redis = app['redis']
        
        # 백그라운드 태스크 시작
        app['metric_updater'] = asyncio.create_task(self.update_metrics_loop())
        app['alert_checker'] = asyncio.create_task(self.check_alerts_loop())
    
    async def cleanup(self, app):
        """서버 종료 시 정리"""
        # 태스크 취소
        app['metric_updater'].cancel()
        app['alert_checker'].cancel()
        
        # Redis 연결 종료
        app['redis'].close()
        await app['redis'].wait_closed()
    
    async def websocket_handler(self, request):
        """WebSocket 핸들러"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.websockets.add(ws)
        
        try:
            # 초기 데이터 전송
            await ws.send_json({
                'type': 'initial',
                'data': await self.get_dashboard_snapshot()
            })
            
            # 클라이언트 메시지 처리
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self.handle_ws_message(ws, data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f'WebSocket error: {ws.exception()}')
                    
        except Exception as e:
            print(f'WebSocket handler error: {e}')
        finally:
            return ws
    
    async def handle_ws_message(self, ws, data):
        """WebSocket 메시지 처리"""
        msg_type = data.get('type')
        
        if msg_type == 'subscribe':
            # 특정 캠페인 구독
            campaign_id = data.get('campaign_id')
            await self.subscribe_to_campaign(ws, campaign_id)
            
        elif msg_type == 'unsubscribe':
            # 구독 해제
            campaign_id = data.get('campaign_id')
            await self.unsubscribe_from_campaign(ws, campaign_id)
            
        elif msg_type == 'update_bid':
            # 입찰가 업데이트
            await self.update_bid(data)
    
    async def update_metrics_loop(self):
        """메트릭 업데이트 루프"""
        while True:
            try:
                # 모든 활성 캠페인의 메트릭 업데이트
                campaigns = await self.get_active_campaigns()
                
                for campaign in campaigns:
                    metrics = await self.fetch_campaign_metrics(campaign['id'])
                    
                    # 캐시 업데이트
                    self.metrics_cache[campaign['id']] = metrics
                    
                    # 구독자에게 브로드캐스트
                    await self.broadcast_metrics_update(campaign['id'], metrics)
                
                # 5초마다 업데이트
                await asyncio.sleep(5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"메트릭 업데이트 오류: {e}")
                await asyncio.sleep(5)
    
    async def check_alerts_loop(self):
        """알림 체크 루프"""
        while True:
            try:
                # 알림 규칙 확인
                alerts = await self.get_alert_rules()
                
                for alert in alerts:
                    if await self.evaluate_alert(alert):
                        await self.trigger_alert(alert)
                
                # 30초마다 체크
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"알림 체크 오류: {e}")
                await asyncio.sleep(30)
    
    async def fetch_campaign_metrics(self, campaign_id: str) -> Dict:
        """캠페인 메트릭 조회"""
        # 여러 소스에서 동시에 데이터 수집
        tasks = [
            self.fetch_facebook_metrics(campaign_id),
            self.fetch_google_metrics(campaign_id),
            self.fetch_internal_metrics(campaign_id)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 병합
        merged_metrics = {
            'campaign_id': campaign_id,
            'timestamp': datetime.now().isoformat(),
            'impressions': 0,
            'clicks': 0,
            'conversions': 0,
            'cost': 0,
            'revenue': 0
        }
        
        for result in results:
            if isinstance(result, dict):
                for key in ['impressions', 'clicks', 'conversions', 'cost', 'revenue']:
                    merged_metrics[key] += result.get(key, 0)
        
        # 파생 메트릭 계산
        merged_metrics['ctr'] = (
            merged_metrics['clicks'] / merged_metrics['impressions'] 
            if merged_metrics['impressions'] > 0 else 0
        )
        merged_metrics['roas'] = (
            merged_metrics['revenue'] / merged_metrics['cost']
            if merged_metrics['cost'] > 0 else 0
        )
        
        return merged_metrics
    
    async def broadcast_metrics_update(self, campaign_id: str, metrics: Dict):
        """메트릭 업데이트 브로드캐스트"""
        message = {
            'type': 'metrics_update',
            'campaign_id': campaign_id,
            'data': metrics
        }
        
        # 모든 WebSocket 클라이언트에게 전송
        disconnected = []
        for ws in self.websockets:
            try:
                await ws.send_json(message)
            except ConnectionResetError:
                disconnected.append(ws)
        
        # 연결 끊긴 클라이언트 제거
        for ws in disconnected:
            self.websockets.discard(ws)
    
    async def evaluate_alert(self, alert: Dict) -> bool:
        """알림 규칙 평가"""
        campaign_id = alert['campaign_id']
        metrics = self.metrics_cache.get(campaign_id, {})
        
        condition = alert['condition']
        metric = condition['metric']
        operator = condition['operator']
        threshold = condition['threshold']
        
        current_value = metrics.get(metric, 0)
        
        # 조건 평가
        if operator == 'greater_than':
            return current_value > threshold
        elif operator == 'less_than':
            return current_value < threshold
        elif operator == 'equals':
            return current_value == threshold
        
        return False
    
    async def trigger_alert(self, alert: Dict):
        """알림 트리거"""
        # 알림 내용 생성
        notification = {
            'type': 'alert',
            'alert_id': alert['id'],
            'campaign_id': alert['campaign_id'],
            'message': alert['message'],
            'severity': alert['severity'],
            'timestamp': datetime.now().isoformat()
        }
        
        # WebSocket으로 실시간 알림
        await self.broadcast_alert(notification)
        
        # 이메일/슬랙 등 외부 알림
        await self.send_external_notifications(notification)
    
    async def get_campaigns(self, request):
        """캠페인 목록 API"""
        # 쿼리 파라미터
        status = request.query.get('status', 'active')
        limit = int(request.query.get('limit', 100))
        
        # Redis에서 캠페인 목록 조회
        campaigns = []
        cursor = b'0'
        
        while cursor:
            cursor, keys = await self.redis.scan(
                cursor, 
                match=f'campaign:{status}:*',
                count=limit
            )
            
            for key in keys:
                campaign_data = await self.redis.get(key)
                if campaign_data:
                    campaigns.append(json.loads(campaign_data))
            
            if len(campaigns) >= limit:
                break
        
        return web.json_response(campaigns[:limit])
    
    async def get_metrics(self, request):
        """메트릭 조회 API"""
        campaign_id = request.match_info['campaign_id']
        
        # 캐시 확인
        if campaign_id in self.metrics_cache:
            return web.json_response(self.metrics_cache[campaign_id])
        
        # 캐시 미스 시 조회
        metrics = await self.fetch_campaign_metrics(campaign_id)
        return web.json_response(metrics)
    
    # 헬퍼 메서드들
    async def fetch_facebook_metrics(self, campaign_id: str) -> Dict:
        """Facebook 광고 메트릭 조회"""
        # Facebook API 호출 시뮬레이션
        await asyncio.sleep(0.1)
        return {
            'impressions': 50000,
            'clicks': 1500,
            'conversions': 75,
            'cost': 2500,
            'revenue': 7500
        }
    
    async def fetch_google_metrics(self, campaign_id: str) -> Dict:
        """Google 광고 메트릭 조회"""
        # Google API 호출 시뮬레이션
        await asyncio.sleep(0.1)
        return {
            'impressions': 30000,
            'clicks': 900,
            'conversions': 45,
            'cost': 1800,
            'revenue': 5400
        }
    
    async def fetch_internal_metrics(self, campaign_id: str) -> Dict:
        """내부 메트릭 조회"""
        # 내부 DB 조회 시뮬레이션
        await asyncio.sleep(0.05)
        return {
            'impressions': 20000,
            'clicks': 600,
            'conversions': 30,
            'cost': 1200,
            'revenue': 3600
        }

# 서버 실행
async def main():
    dashboard = RealTimeAdDashboard()
    
    # 이벤트 핸들러 등록
    dashboard.app.on_startup.append(dashboard.startup)
    dashboard.app.on_cleanup.append(dashboard.cleanup)
    
    # 서버 시작
    runner = web.AppRunner(dashboard.app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    
    print("실시간 광고 대시보드 서버 시작: http://localhost:8080")
    await site.start()
    
    # 서버 유지
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(main())
```

## 📝 과제

### 과제 1: 비동기 광고 크롤러
여러 광고 플랫폼을 동시에 크롤링하는 시스템 구현:
- 동시 요청 수 제한
- 재시도 로직
- 결과 실시간 스트리밍

### 과제 2: 실시간 입찰 최적화
ML 모델을 활용한 실시간 입찰 시스템 구현:
- 비동기 모델 추론
- A/B 테스트 지원
- 성능 모니터링

### 과제 3: 스트리밍 ETL 파이프라인
실시간 광고 데이터 ETL 파이프라인 구현:
- Kafka 연동
- 데이터 변환
- 실시간 집계

### 과제 4: 비동기 리포트 생성기
대용량 리포트를 비동기로 생성하는 시스템 구현:
- 진행 상황 추적
- 부분 결과 스트리밍
- 오류 복구

## 🔗 참고 자료
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [aiohttp Documentation](https://docs.aiohttp.org/)
- [Async IO in Python: A Complete Walkthrough](https://realpython.com/async-io-python/)
- [Building Async APIs with FastAPI](https://fastapi.tiangolo.com/async/)

---

다음 장: [Chapter 05: Logging →](../05_logging/README.md)