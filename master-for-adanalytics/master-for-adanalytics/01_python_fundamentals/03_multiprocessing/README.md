# Chapter 03: Multiprocessing - 멀티프로세싱

## 📚 학습 목표
- 프로세스와 스레드의 차이점 이해
- Python GIL(Global Interpreter Lock) 이해
- multiprocessing 모듈을 활용한 병렬 처리
- 대용량 광고 데이터 처리 최적화

## 📖 이론: 병렬 처리 기초

### 1. 프로세스 vs 스레드

```python
import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# CPU 집약적 작업 예시
def cpu_bound_task(n):
    """CPU 집약적 작업 - 소수 계산"""
    count = 0
    for i in range(n):
        for j in range(2, int(i**0.5) + 1):
            if i % j == 0:
                break
        else:
            if i > 1:
                count += 1
    return count

# I/O 집약적 작업 예시
def io_bound_task(url):
    """I/O 집약적 작업 - 네트워크 요청"""
    import requests
    response = requests.get(url)
    return len(response.content)

# 성능 비교
def compare_performance():
    """스레드 vs 프로세스 성능 비교"""
    numbers = [100000] * 4
    
    # 순차 처리
    start = time.time()
    results = [cpu_bound_task(n) for n in numbers]
    sequential_time = time.time() - start
    print(f"순차 처리: {sequential_time:.2f}초")
    
    # 스레드 풀 (GIL로 인해 CPU 작업에서는 비효율적)
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(cpu_bound_task, numbers))
    thread_time = time.time() - start
    print(f"스레드 풀: {thread_time:.2f}초")
    
    # 프로세스 풀 (진정한 병렬 처리)
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(cpu_bound_task, numbers))
    process_time = time.time() - start
    print(f"프로세스 풀: {process_time:.2f}초")
```

### 2. multiprocessing 기본 사용법

```python
import multiprocessing as mp
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np

class AdDataProcessor:
    """광고 데이터 병렬 처리기"""
    
    def __init__(self, num_processes: int = None):
        self.num_processes = num_processes or mp.cpu_count()
    
    def process_campaign_data(self, campaign_ids: List[str]) -> Dict:
        """캠페인 데이터 병렬 처리"""
        # 작업을 프로세스 수만큼 분할
        chunks = self._split_into_chunks(campaign_ids, self.num_processes)
        
        # 프로세스 풀 생성
        with mp.Pool(processes=self.num_processes) as pool:
            # 각 청크를 별도 프로세스에서 처리
            results = pool.map(self._process_campaign_chunk, chunks)
        
        # 결과 병합
        return self._merge_results(results)
    
    def _split_into_chunks(self, data: List, n: int) -> List[List]:
        """데이터를 n개의 청크로 분할"""
        chunk_size = len(data) // n
        chunks = []
        
        for i in range(n):
            start = i * chunk_size
            end = start + chunk_size if i < n - 1 else len(data)
            chunks.append(data[start:end])
        
        return chunks
    
    def _process_campaign_chunk(self, campaign_ids: List[str]) -> Dict:
        """캠페인 청크 처리"""
        results = {}
        
        for campaign_id in campaign_ids:
            # 실제로는 데이터베이스에서 조회
            campaign_data = self._fetch_campaign_data(campaign_id)
            
            # 복잡한 계산 수행
            metrics = {
                'impressions': campaign_data['impressions'],
                'clicks': campaign_data['clicks'],
                'conversions': campaign_data['conversions'],
                'ctr': campaign_data['clicks'] / campaign_data['impressions'],
                'cvr': campaign_data['conversions'] / campaign_data['clicks'],
                'cost': campaign_data['cost'],
                'revenue': campaign_data['revenue'],
                'roas': campaign_data['revenue'] / campaign_data['cost']
            }
            
            results[campaign_id] = metrics
        
        return results
    
    def _fetch_campaign_data(self, campaign_id: str) -> Dict:
        """캠페인 데이터 조회 (시뮬레이션)"""
        np.random.seed(hash(campaign_id) % 1000)
        return {
            'impressions': np.random.randint(10000, 1000000),
            'clicks': np.random.randint(100, 10000),
            'conversions': np.random.randint(10, 1000),
            'cost': np.random.uniform(1000, 100000),
            'revenue': np.random.uniform(5000, 500000)
        }
    
    def _merge_results(self, results: List[Dict]) -> Dict:
        """결과 병합"""
        merged = {}
        for result in results:
            merged.update(result)
        return merged
```

### 3. 프로세스 간 통신

```python
from multiprocessing import Queue, Pipe, Value, Array, Lock
import time

class AdBidProcessor:
    """실시간 광고 입찰 처리기"""
    
    def __init__(self):
        self.bid_queue = mp.Queue()
        self.result_queue = mp.Queue()
        self.stats = mp.Manager().dict()
        self.lock = mp.Lock()
    
    def bid_worker(self, worker_id: int):
        """입찰 처리 워커"""
        processed = 0
        
        while True:
            try:
                # 입찰 요청 가져오기 (타임아웃 설정)
                bid_request = self.bid_queue.get(timeout=1)
                
                if bid_request is None:  # 종료 신호
                    break
                
                # 입찰 처리
                result = self._process_bid(bid_request)
                
                # 결과 전송
                self.result_queue.put(result)
                
                # 통계 업데이트 (동기화 필요)
                with self.lock:
                    processed += 1
                    self.stats[f'worker_{worker_id}_processed'] = processed
                    
            except mp.queues.Empty:
                continue
    
    def _process_bid(self, bid_request: Dict) -> Dict:
        """입찰 처리 로직"""
        # 복잡한 입찰 계산
        time.sleep(0.01)  # 처리 시간 시뮬레이션
        
        bid_price = self._calculate_bid_price(
            bid_request['user_profile'],
            bid_request['ad_inventory'],
            bid_request['context']
        )
        
        return {
            'request_id': bid_request['request_id'],
            'bid_price': bid_price,
            'timestamp': time.time()
        }
    
    def _calculate_bid_price(self, user_profile: Dict, 
                           ad_inventory: Dict, 
                           context: Dict) -> float:
        """입찰가 계산"""
        base_bid = ad_inventory.get('floor_price', 100)
        
        # 사용자 가치 점수
        user_value = user_profile.get('ltv_score', 0.5)
        
        # 컨텍스트 점수
        context_score = context.get('relevance_score', 0.5)
        
        # 최종 입찰가
        bid_price = base_bid * (1 + user_value) * (1 + context_score)
        
        return min(bid_price, ad_inventory.get('max_bid', 1000))
    
    def process_bid_stream(self, bid_requests: List[Dict], 
                          num_workers: int = 4) -> List[Dict]:
        """입찰 스트림 처리"""
        # 워커 프로세스 시작
        workers = []
        for i in range(num_workers):
            p = mp.Process(target=self.bid_worker, args=(i,))
            p.start()
            workers.append(p)
        
        # 입찰 요청 전송
        for request in bid_requests:
            self.bid_queue.put(request)
        
        # 종료 신호 전송
        for _ in range(num_workers):
            self.bid_queue.put(None)
        
        # 결과 수집
        results = []
        for _ in range(len(bid_requests)):
            result = self.result_queue.get()
            results.append(result)
        
        # 워커 종료 대기
        for p in workers:
            p.join()
        
        # 통계 출력
        print("처리 통계:", dict(self.stats))
        
        return results
```

## 🛠️ 실습: 대용량 광고 데이터 처리

### 실습 1: 병렬 데이터 집계

```python
import pandas as pd
import numpy as np
from functools import partial
from multiprocessing import Pool
import time

class ParallelAdAggregator:
    """병렬 광고 데이터 집계기"""
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.num_cores = mp.cpu_count()
    
    def aggregate_campaign_performance(self, 
                                     start_date: str, 
                                     end_date: str) -> pd.DataFrame:
        """캠페인 성과 병렬 집계"""
        # 날짜 범위 생성
        date_range = pd.date_range(start_date, end_date)
        
        # 날짜를 청크로 분할
        date_chunks = np.array_split(date_range, self.num_cores)
        
        # 부분 함수 생성 (추가 인자 고정)
        process_func = partial(
            self._process_date_chunk,
            data_path=self.data_path
        )
        
        # 병렬 처리
        with Pool(processes=self.num_cores) as pool:
            chunk_results = pool.map(process_func, date_chunks)
        
        # 결과 병합
        final_result = pd.concat(chunk_results, ignore_index=True)
        
        # 최종 집계
        aggregated = final_result.groupby('campaign_id').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum',
            'cost': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # 파생 지표 계산
        aggregated['ctr'] = aggregated['clicks'] / aggregated['impressions']
        aggregated['cvr'] = aggregated['conversions'] / aggregated['clicks']
        aggregated['cpc'] = aggregated['cost'] / aggregated['clicks']
        aggregated['roas'] = aggregated['revenue'] / aggregated['cost']
        
        return aggregated
    
    @staticmethod
    def _process_date_chunk(dates: pd.DatetimeIndex, 
                           data_path: str) -> pd.DataFrame:
        """날짜 청크 처리"""
        chunk_data = []
        
        for date in dates:
            # 일별 데이터 로드 (실제로는 데이터베이스 쿼리)
            daily_data = ParallelAdAggregator._load_daily_data(
                data_path, date
            )
            chunk_data.append(daily_data)
        
        return pd.concat(chunk_data, ignore_index=True)
    
    @staticmethod
    def _load_daily_data(data_path: str, date: pd.Timestamp) -> pd.DataFrame:
        """일별 데이터 로드 (시뮬레이션)"""
        # 실제로는 파일이나 DB에서 로드
        num_campaigns = 100
        
        data = {
            'date': [date] * num_campaigns,
            'campaign_id': [f'camp_{i}' for i in range(num_campaigns)],
            'impressions': np.random.randint(1000, 100000, num_campaigns),
            'clicks': np.random.randint(10, 1000, num_campaigns),
            'conversions': np.random.randint(1, 100, num_campaigns),
            'cost': np.random.uniform(100, 10000, num_campaigns),
            'revenue': np.random.uniform(500, 50000, num_campaigns)
        }
        
        return pd.DataFrame(data)

# 병렬 처리 vs 순차 처리 성능 비교
def benchmark_aggregation():
    """집계 성능 벤치마크"""
    aggregator = ParallelAdAggregator('dummy_path')
    
    # 병렬 처리
    start = time.time()
    parallel_result = aggregator.aggregate_campaign_performance(
        '2024-01-01', '2024-01-31'
    )
    parallel_time = time.time() - start
    
    print(f"병렬 처리 시간: {parallel_time:.2f}초")
    print(f"처리된 캠페인 수: {len(parallel_result)}")
    print(f"평균 ROAS: {parallel_result['roas'].mean():.2f}")
```

### 실습 2: 실시간 스트림 처리

```python
from multiprocessing import Process, Queue, Event
import queue
import json

class RealTimeAdStreamProcessor:
    """실시간 광고 스트림 처리기"""
    
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.input_queue = mp.Queue(maxsize=10000)
        self.output_queue = mp.Queue(maxsize=10000)
        self.error_queue = mp.Queue(maxsize=1000)
        self.shutdown_event = mp.Event()
        self.stats = mp.Manager().dict({
            'processed': 0,
            'errors': 0,
            'filtered': 0
        })
    
    def stream_processor(self, worker_id: int):
        """스트림 처리 워커"""
        local_stats = {'processed': 0, 'errors': 0, 'filtered': 0}
        
        while not self.shutdown_event.is_set():
            try:
                # 이벤트 가져오기
                event = self.input_queue.get(timeout=0.1)
                
                # 이벤트 처리
                try:
                    processed_event = self._process_ad_event(event)
                    
                    if processed_event:
                        self.output_queue.put(processed_event)
                        local_stats['processed'] += 1
                    else:
                        local_stats['filtered'] += 1
                        
                except Exception as e:
                    self.error_queue.put({
                        'worker_id': worker_id,
                        'event': event,
                        'error': str(e)
                    })
                    local_stats['errors'] += 1
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
        
        # 최종 통계 업데이트
        for key, value in local_stats.items():
            self.stats[key] = self.stats.get(key, 0) + value
    
    def _process_ad_event(self, event: Dict) -> Optional[Dict]:
        """광고 이벤트 처리"""
        event_type = event.get('type')
        
        if event_type == 'impression':
            return self._process_impression(event)
        elif event_type == 'click':
            return self._process_click(event)
        elif event_type == 'conversion':
            return self._process_conversion(event)
        else:
            return None
    
    def _process_impression(self, event: Dict) -> Dict:
        """노출 이벤트 처리"""
        # 봇 필터링
        if self._is_bot(event.get('user_agent', '')):
            return None
        
        # 유효성 검증
        if not all(k in event for k in ['ad_id', 'user_id', 'timestamp']):
            return None
        
        # 처리된 이벤트 반환
        return {
            'type': 'processed_impression',
            'ad_id': event['ad_id'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
            'cost': self._calculate_impression_cost(event)
        }
    
    def _process_click(self, event: Dict) -> Dict:
        """클릭 이벤트 처리"""
        # 중복 클릭 필터링
        if self._is_duplicate_click(event):
            return None
        
        return {
            'type': 'processed_click',
            'ad_id': event['ad_id'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
            'cost': self._calculate_click_cost(event)
        }
    
    def _process_conversion(self, event: Dict) -> Dict:
        """전환 이벤트 처리"""
        # 어트리뷰션 윈도우 확인
        if not self._within_attribution_window(event):
            return None
        
        return {
            'type': 'processed_conversion',
            'ad_id': event['ad_id'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
            'value': event.get('value', 0),
            'attribution': self._calculate_attribution(event)
        }
    
    def _is_bot(self, user_agent: str) -> bool:
        """봇 탐지"""
        bot_patterns = ['bot', 'crawler', 'spider', 'scraper']
        return any(pattern in user_agent.lower() for pattern in bot_patterns)
    
    def _is_duplicate_click(self, event: Dict) -> bool:
        """중복 클릭 확인"""
        # 실제로는 Redis 등을 사용하여 확인
        return False
    
    def _within_attribution_window(self, event: Dict) -> bool:
        """어트리뷰션 윈도우 내 확인"""
        # 실제로는 클릭 시간과 비교
        return True
    
    def _calculate_impression_cost(self, event: Dict) -> float:
        """노출 비용 계산"""
        return event.get('bid_price', 0) / 1000  # CPM
    
    def _calculate_click_cost(self, event: Dict) -> float:
        """클릭 비용 계산"""
        return event.get('bid_price', 0)  # CPC
    
    def _calculate_attribution(self, event: Dict) -> str:
        """어트리뷰션 계산"""
        return 'last_click'  # 단순화된 어트리뷰션
    
    def start_processing(self):
        """처리 시작"""
        # 워커 프로세스 시작
        workers = []
        for i in range(self.num_workers):
            p = Process(target=self.stream_processor, args=(i,))
            p.start()
            workers.append(p)
        
        return workers
    
    def stop_processing(self, workers: List[Process]):
        """처리 중지"""
        # 종료 신호
        self.shutdown_event.set()
        
        # 워커 종료 대기
        for p in workers:
            p.join(timeout=5)
            if p.is_alive():
                p.terminate()
        
        # 최종 통계 출력
        print("처리 통계:")
        print(f"  처리됨: {self.stats['processed']}")
        print(f"  필터됨: {self.stats['filtered']}")
        print(f"  오류: {self.stats['errors']}")
```

### 실습 3: 분산 머신러닝 훈련

```python
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np

class DistributedAdModelTrainer:
    """분산 광고 모델 훈련기"""
    
    def __init__(self, n_estimators: int = 100):
        self.n_estimators = n_estimators
        self.n_jobs = mp.cpu_count()
    
    def train_click_prediction_model(self, 
                                   X: np.ndarray, 
                                   y: np.ndarray) -> RandomForestClassifier:
        """클릭 예측 모델 병렬 훈련"""
        # 데이터 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 각 프로세스가 훈련할 트리 수 계산
        trees_per_process = self.n_estimators // self.n_jobs
        
        # 병렬 훈련 작업 생성
        train_tasks = []
        for i in range(self.n_jobs):
            n_trees = trees_per_process
            if i == self.n_jobs - 1:
                # 마지막 프로세스는 나머지 트리도 훈련
                n_trees += self.n_estimators % self.n_jobs
            
            task = (X_train, y_train, n_trees, i)
            train_tasks.append(task)
        
        # 병렬 훈련
        with Pool(processes=self.n_jobs) as pool:
            sub_models = pool.map(self._train_sub_model, train_tasks)
        
        # 모델 앙상블
        ensemble_model = self._ensemble_models(sub_models)
        
        # 평가
        score = ensemble_model.score(X_test, y_test)
        print(f"모델 정확도: {score:.4f}")
        
        return ensemble_model
    
    @staticmethod
    def _train_sub_model(args: Tuple) -> RandomForestClassifier:
        """서브 모델 훈련"""
        X_train, y_train, n_trees, seed = args
        
        model = RandomForestClassifier(
            n_estimators=n_trees,
            random_state=seed,
            n_jobs=1  # 각 프로세스는 단일 스레드 사용
        )
        
        model.fit(X_train, y_train)
        return model
    
    def _ensemble_models(self, 
                        sub_models: List[RandomForestClassifier]
                        ) -> RandomForestClassifier:
        """서브 모델 앙상블"""
        # 모든 트리 수집
        all_estimators = []
        for model in sub_models:
            all_estimators.extend(model.estimators_)
        
        # 앙상블 모델 생성
        ensemble = RandomForestClassifier(n_estimators=1)
        ensemble.fit([[0]], [0])  # 더미 학습
        ensemble.estimators_ = all_estimators
        ensemble.n_estimators = len(all_estimators)
        
        # 기타 속성 복사
        ensemble.classes_ = sub_models[0].classes_
        ensemble.n_classes_ = sub_models[0].n_classes_
        ensemble.n_features_in_ = sub_models[0].n_features_in_
        
        return ensemble
    
    def parallel_feature_importance(self, 
                                  model: RandomForestClassifier,
                                  feature_names: List[str]) -> pd.DataFrame:
        """병렬 특성 중요도 계산"""
        # 각 트리의 특성 중요도 계산을 병렬화
        with Pool(processes=self.n_jobs) as pool:
            tree_importances = pool.map(
                self._get_tree_importance,
                model.estimators_
            )
        
        # 평균 계산
        avg_importance = np.mean(tree_importances, axis=0)
        
        # 결과 정리
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': avg_importance
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    @staticmethod
    def _get_tree_importance(tree):
        """개별 트리의 특성 중요도"""
        return tree.feature_importances_
```

## 🚀 프로젝트: 실시간 광고 입찰 시스템

### 프로젝트 구조
```
real_time_bidding_system/
├── __init__.py
├── bidder/
│   ├── __init__.py
│   ├── bid_processor.py
│   ├── bid_strategy.py
│   └── feature_extractor.py
├── stream/
│   ├── __init__.py
│   ├── event_processor.py
│   └── data_pipeline.py
├── analytics/
│   ├── __init__.py
│   ├── real_time_analytics.py
│   └── batch_analytics.py
├── models/
│   ├── __init__.py
│   ├── click_predictor.py
│   └── bid_optimizer.py
└── main.py
```

### 통합 시스템 구현

```python
# main.py
import multiprocessing as mp
from multiprocessing import Process, Queue, Manager
import time
import json
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np

class RealTimeBiddingSystem:
    """실시간 입찰 시스템"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.manager = Manager()
        
        # 공유 자원
        self.bid_requests = Queue(maxsize=100000)
        self.bid_responses = Queue(maxsize=100000)
        self.analytics_queue = Queue(maxsize=50000)
        
        # 공유 상태
        self.system_stats = self.manager.dict({
            'total_requests': 0,
            'total_bids': 0,
            'total_wins': 0,
            'total_spend': 0.0,
            'avg_response_time': 0.0
        })
        
        # 프로세스 풀
        self.bidder_processes = []
        self.analytics_processes = []
        self.is_running = mp.Event()
    
    def bidder_worker(self, worker_id: int):
        """입찰 워커 프로세스"""
        local_stats = {
            'requests': 0,
            'bids': 0,
            'total_time': 0
        }
        
        while self.is_running.is_set():
            try:
                # 입찰 요청 받기
                request = self.bid_requests.get(timeout=0.1)
                start_time = time.time()
                
                # 입찰 결정
                bid_response = self._process_bid_request(request, worker_id)
                
                # 응답 전송
                if bid_response:
                    self.bid_responses.put(bid_response)
                    local_stats['bids'] += 1
                
                # 분석용 데이터 전송
                self.analytics_queue.put({
                    'type': 'bid_event',
                    'worker_id': worker_id,
                    'request_id': request['id'],
                    'bid': bid_response is not None,
                    'response_time': time.time() - start_time
                })
                
                local_stats['requests'] += 1
                local_stats['total_time'] += time.time() - start_time
                
            except mp.queues.Empty:
                continue
            except Exception as e:
                print(f"Bidder {worker_id} error: {e}")
        
        # 최종 통계 업데이트
        avg_time = local_stats['total_time'] / max(local_stats['requests'], 1)
        print(f"Bidder {worker_id} - Requests: {local_stats['requests']}, "
              f"Bids: {local_stats['bids']}, Avg Time: {avg_time:.3f}s")
    
    def _process_bid_request(self, request: Dict, worker_id: int) -> Optional[Dict]:
        """입찰 요청 처리"""
        # 특징 추출
        features = self._extract_features(request)
        
        # 클릭 확률 예측
        click_prob = self._predict_click_probability(features)
        
        # 입찰가 계산
        bid_price = self._calculate_bid_price(
            click_prob,
            request.get('floor_price', 0),
            request.get('user_value', 1.0)
        )
        
        # 입찰 결정
        if bid_price > request.get('floor_price', 0):
            return {
                'request_id': request['id'],
                'bid_price': bid_price,
                'worker_id': worker_id,
                'timestamp': time.time(),
                'click_prob': click_prob
            }
        
        return None
    
    def _extract_features(self, request: Dict) -> np.ndarray:
        """특징 추출"""
        features = []
        
        # 사용자 특징
        user = request.get('user', {})
        features.extend([
            user.get('age', 0) / 100,
            1 if user.get('gender') == 'M' else 0,
            len(user.get('interests', [])) / 10
        ])
        
        # 광고 슬롯 특징
        slot = request.get('slot', {})
        features.extend([
            slot.get('width', 0) / 1000,
            slot.get('height', 0) / 1000,
            1 if slot.get('position') == 'above_fold' else 0
        ])
        
        # 컨텍스트 특징
        context = request.get('context', {})
        features.extend([
            context.get('hour', 0) / 24,
            context.get('day_of_week', 0) / 7,
            1 if context.get('device') == 'mobile' else 0
        ])
        
        return np.array(features)
    
    def _predict_click_probability(self, features: np.ndarray) -> float:
        """클릭 확률 예측 (간단한 모델)"""
        # 실제로는 훈련된 ML 모델 사용
        weights = np.random.rand(len(features))
        logit = np.dot(features, weights)
        return 1 / (1 + np.exp(-logit))
    
    def _calculate_bid_price(self, click_prob: float, 
                           floor_price: float,
                           user_value: float) -> float:
        """입찰가 계산"""
        # 예상 가치 = 클릭 확률 * 사용자 가치
        expected_value = click_prob * user_value * 1000  # CPM 기준
        
        # 마진 고려
        bid_price = expected_value * 0.8
        
        # 최소/최대 제약
        bid_price = max(bid_price, floor_price)
        bid_price = min(bid_price, self.config.get('max_bid', 1000))
        
        return bid_price
    
    def analytics_worker(self):
        """분석 워커 프로세스"""
        batch = []
        batch_size = 1000
        last_flush = time.time()
        
        while self.is_running.is_set() or not self.analytics_queue.empty():
            try:
                # 이벤트 수집
                event = self.analytics_queue.get(timeout=0.1)
                batch.append(event)
                
                # 배치 처리
                if len(batch) >= batch_size or time.time() - last_flush > 5:
                    self._process_analytics_batch(batch)
                    batch = []
                    last_flush = time.time()
                    
            except mp.queues.Empty:
                # 타임아웃 시 배치 처리
                if batch:
                    self._process_analytics_batch(batch)
                    batch = []
                    last_flush = time.time()
            except Exception as e:
                print(f"Analytics error: {e}")
    
    def _process_analytics_batch(self, batch: List[Dict]):
        """분석 배치 처리"""
        # 집계
        total_requests = sum(1 for e in batch if e['type'] == 'bid_event')
        total_bids = sum(1 for e in batch if e.get('bid', False))
        avg_response_time = np.mean([
            e['response_time'] for e in batch 
            if 'response_time' in e
        ])
        
        # 통계 업데이트
        self.system_stats['total_requests'] += total_requests
        self.system_stats['total_bids'] += total_bids
        self.system_stats['avg_response_time'] = avg_response_time
        
        # 실시간 대시보드 업데이트 (실제로는 외부 시스템)
        print(f"[Analytics] Batch processed - "
              f"Requests: {total_requests}, "
              f"Bids: {total_bids}, "
              f"Avg Response: {avg_response_time*1000:.1f}ms")
    
    def start(self):
        """시스템 시작"""
        self.is_running.set()
        
        # 입찰 워커 시작
        num_bidders = self.config.get('num_bidders', 4)
        for i in range(num_bidders):
            p = Process(target=self.bidder_worker, args=(i,))
            p.start()
            self.bidder_processes.append(p)
        
        # 분석 워커 시작
        analytics_process = Process(target=self.analytics_worker)
        analytics_process.start()
        self.analytics_processes.append(analytics_process)
        
        print(f"RTB System started with {num_bidders} bidders")
    
    def stop(self):
        """시스템 중지"""
        print("Shutting down RTB System...")
        
        # 종료 신호
        self.is_running.clear()
        
        # 프로세스 종료 대기
        for p in self.bidder_processes:
            p.join(timeout=5)
            if p.is_alive():
                p.terminate()
        
        for p in self.analytics_processes:
            p.join(timeout=5)
            if p.is_alive():
                p.terminate()
        
        # 최종 통계
        print("\n=== Final Statistics ===")
        print(f"Total Requests: {self.system_stats['total_requests']}")
        print(f"Total Bids: {self.system_stats['total_bids']}")
        print(f"Bid Rate: {self.system_stats['total_bids'] / max(self.system_stats['total_requests'], 1) * 100:.1f}%")
        print(f"Avg Response Time: {self.system_stats['avg_response_time']*1000:.1f}ms")
    
    def simulate_bid_stream(self, duration: int = 10):
        """입찰 스트림 시뮬레이션"""
        print(f"Simulating bid stream for {duration} seconds...")
        
        start_time = time.time()
        request_id = 0
        
        while time.time() - start_time < duration:
            # 입찰 요청 생성
            request = {
                'id': f'req_{request_id}',
                'user': {
                    'age': np.random.randint(18, 65),
                    'gender': np.random.choice(['M', 'F']),
                    'interests': np.random.choice(
                        ['sports', 'fashion', 'tech', 'food'],
                        size=np.random.randint(1, 4)
                    ).tolist()
                },
                'slot': {
                    'width': np.random.choice([300, 728, 970]),
                    'height': np.random.choice([250, 90, 250]),
                    'position': np.random.choice(['above_fold', 'below_fold'])
                },
                'context': {
                    'hour': datetime.now().hour,
                    'day_of_week': datetime.now().weekday(),
                    'device': np.random.choice(['mobile', 'desktop'])
                },
                'floor_price': np.random.uniform(0.1, 5.0),
                'user_value': np.random.uniform(0.5, 10.0)
            }
            
            self.bid_requests.put(request)
            request_id += 1
            
            # QPS 제어
            time.sleep(0.001)  # 1000 QPS
        
        print(f"Generated {request_id} bid requests")

# 시스템 실행
if __name__ == "__main__":
    config = {
        'num_bidders': 8,
        'max_bid': 10.0,
        'batch_size': 1000
    }
    
    rtb_system = RealTimeBiddingSystem(config)
    
    try:
        # 시스템 시작
        rtb_system.start()
        
        # 입찰 스트림 시뮬레이션
        rtb_system.simulate_bid_stream(duration=30)
        
        # 처리 대기
        time.sleep(5)
        
    finally:
        # 시스템 종료
        rtb_system.stop()
```

## 📝 과제

### 과제 1: 병렬 A/B 테스트 분석
여러 캠페인의 A/B 테스트 결과를 병렬로 분석하는 시스템을 구현하세요:
- 통계적 유의성 검정
- 신뢰구간 계산
- 다중 비교 보정

### 과제 2: 분산 CTR 예측 모델
대용량 데이터로 CTR 예측 모델을 분산 훈련하는 시스템을 구현하세요:
- 데이터 병렬화
- 모델 병렬화
- 하이퍼파라미터 튜닝

### 과제 3: 실시간 이상 탐지
광고 트래픽의 이상을 실시간으로 탐지하는 시스템을 구현하세요:
- 스트리밍 데이터 처리
- 이상 패턴 감지
- 실시간 알림

### 과제 4: 분산 리포트 생성
대규모 광고 캠페인 리포트를 병렬로 생성하는 시스템을 구현하세요:
- 다차원 집계
- 시각화 생성
- PDF/Excel 출력

## 🔗 참고 자료
- [Python multiprocessing Documentation](https://docs.python.org/3/library/multiprocessing.html)
- [Parallel and Distributed Computing in Python](https://realpython.com/python-parallel-processing/)
- [High Performance Python](https://www.oreilly.com/library/view/high-performance-python/9781492055013/)
- [Scaling Python](https://scaling-python.com/)

---

다음 장: [Chapter 04: Async Programming →](../04_async_programming/README.md)