# Chapter 05: Logging - 로깅

## 📚 학습 목표
- 효과적인 로깅 전략 수립
- 구조화된 로깅 구현
- 광고 시스템 모니터링 체계 구축
- 로그 분석을 통한 인사이트 도출

## 📖 이론: 로깅의 핵심 개념

### 1. 로깅 레벨과 사용 시나리오

```python
import logging
import json
from datetime import datetime
from typing import Dict, Any
import traceback

# 광고 시스템을 위한 로깅 설정
class AdSystemLogger:
    """광고 시스템 전용 로거"""
    
    @staticmethod
    def setup_logging(app_name: str = "ad_system") -> logging.Logger:
        """로깅 설정"""
        
        # 로거 생성
        logger = logging.getLogger(app_name)
        logger.setLevel(logging.DEBUG)
        
        # 포맷터 생성
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - '
            '%(filename)s:%(lineno)d - %(message)s'
        )
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # 파일 핸들러 (일별 로테이션)
        from logging.handlers import TimedRotatingFileHandler
        file_handler = TimedRotatingFileHandler(
            f'logs/{app_name}.log',
            when='midnight',
            interval=1,
            backupCount=30
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # 에러 전용 핸들러
        error_handler = logging.FileHandler(f'logs/{app_name}_errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # 핸들러 추가
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        
        return logger

# 로깅 레벨별 사용 예시
logger = AdSystemLogger.setup_logging()

# DEBUG: 상세한 디버깅 정보
logger.debug(f"캠페인 데이터 조회: campaign_id={campaign_id}, filters={filters}")

# INFO: 일반적인 정보성 메시지
logger.info(f"광고 캠페인 생성 완료: {campaign_name} (ID: {campaign_id})")

# WARNING: 주의가 필요한 상황
logger.warning(f"일일 예산의 80% 소진: campaign_id={campaign_id}, spent={spent}")

# ERROR: 오류 발생 (복구 가능)
logger.error(f"광고 API 호출 실패: {api_error}", exc_info=True)

# CRITICAL: 심각한 오류 (시스템 중단 가능)
logger.critical(f"데이터베이스 연결 실패: {db_error}")
```

### 2. 구조화된 로깅

```python
import json
import logging
from typing import Dict, Any, Optional
from functools import wraps
import time
import uuid

class StructuredLogger:
    """구조화된 로깅을 위한 커스텀 로거"""
    
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
        self.context = {}
    
    def set_context(self, **kwargs):
        """로깅 컨텍스트 설정"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """컨텍스트 초기화"""
        self.context = {}
    
    def _create_log_entry(self, 
                         level: str,
                         message: str,
                         **kwargs) -> Dict[str, Any]:
        """구조화된 로그 엔트리 생성"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            'context': self.context.copy()
        }
        
        # 추가 필드
        log_entry.update(kwargs)
        
        return log_entry
    
    def debug(self, message: str, **kwargs):
        log_entry = self._create_log_entry('DEBUG', message, **kwargs)
        self.logger.debug(json.dumps(log_entry))
    
    def info(self, message: str, **kwargs):
        log_entry = self._create_log_entry('INFO', message, **kwargs)
        self.logger.info(json.dumps(log_entry))
    
    def warning(self, message: str, **kwargs):
        log_entry = self._create_log_entry('WARNING', message, **kwargs)
        self.logger.warning(json.dumps(log_entry))
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        log_entry = self._create_log_entry('ERROR', message, **kwargs)
        
        if exception:
            log_entry['exception'] = {
                'type': type(exception).__name__,
                'message': str(exception),
                'traceback': traceback.format_exc()
            }
        
        self.logger.error(json.dumps(log_entry))
    
    def critical(self, message: str, **kwargs):
        log_entry = self._create_log_entry('CRITICAL', message, **kwargs)
        self.logger.critical(json.dumps(log_entry))

# 광고 이벤트 로깅
class AdEventLogger(StructuredLogger):
    """광고 이벤트 전용 로거"""
    
    def log_impression(self, ad_id: str, user_id: str, **kwargs):
        """노출 로깅"""
        self.info(
            "Ad impression recorded",
            event_type="impression",
            ad_id=ad_id,
            user_id=user_id,
            **kwargs
        )
    
    def log_click(self, ad_id: str, user_id: str, **kwargs):
        """클릭 로깅"""
        self.info(
            "Ad click recorded",
            event_type="click",
            ad_id=ad_id,
            user_id=user_id,
            **kwargs
        )
    
    def log_conversion(self, ad_id: str, user_id: str, value: float, **kwargs):
        """전환 로깅"""
        self.info(
            "Conversion recorded",
            event_type="conversion",
            ad_id=ad_id,
            user_id=user_id,
            conversion_value=value,
            **kwargs
        )
    
    def log_bid_request(self, request_id: str, **kwargs):
        """입찰 요청 로깅"""
        self.debug(
            "Bid request received",
            event_type="bid_request",
            request_id=request_id,
            **kwargs
        )
    
    def log_bid_response(self, request_id: str, bid_price: float, 
                        win: bool, **kwargs):
        """입찰 응답 로깅"""
        self.info(
            "Bid response sent",
            event_type="bid_response",
            request_id=request_id,
            bid_price=bid_price,
            win=win,
            **kwargs
        )
```

### 3. 성능 로깅과 메트릭

```python
import time
from contextlib import contextmanager
from functools import wraps
import statistics

class PerformanceLogger:
    """성능 측정 및 로깅"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.metrics = {}
    
    @contextmanager
    def measure_time(self, operation: str, **tags):
        """실행 시간 측정 컨텍스트 매니저"""
        start_time = time.time()
        
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.logger.info(
                f"Operation completed: {operation}",
                operation=operation,
                duration_ms=duration * 1000,
                **tags
            )
            
            # 메트릭 저장
            if operation not in self.metrics:
                self.metrics[operation] = []
            self.metrics[operation].append(duration)
    
    def log_api_call(self, func):
        """API 호출 로깅 데코레이터"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            request_id = str(uuid.uuid4())
            start_time = time.time()
            
            self.logger.info(
                f"API call started: {func.__name__}",
                api_method=func.__name__,
                request_id=request_id,
                args=str(args)[:100],  # 인자 일부만 로깅
                kwargs=str(kwargs)[:100]
            )
            
            try:
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                self.logger.info(
                    f"API call succeeded: {func.__name__}",
                    api_method=func.__name__,
                    request_id=request_id,
                    duration_ms=duration * 1000,
                    status="success"
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                self.logger.error(
                    f"API call failed: {func.__name__}",
                    exception=e,
                    api_method=func.__name__,
                    request_id=request_id,
                    duration_ms=duration * 1000,
                    status="error"
                )
                raise
        
        return wrapper
    
    def get_performance_summary(self) -> Dict[str, Dict[str, float]]:
        """성능 요약 통계"""
        summary = {}
        
        for operation, durations in self.metrics.items():
            if durations:
                summary[operation] = {
                    'count': len(durations),
                    'mean_ms': statistics.mean(durations) * 1000,
                    'median_ms': statistics.median(durations) * 1000,
                    'min_ms': min(durations) * 1000,
                    'max_ms': max(durations) * 1000,
                    'stdev_ms': statistics.stdev(durations) * 1000 if len(durations) > 1 else 0
                }
        
        return summary

# 사용 예시
logger = StructuredLogger("ad_api")
perf_logger = PerformanceLogger(logger)

class AdAPI:
    """광고 API 클래스"""
    
    @perf_logger.log_api_call
    def create_campaign(self, name: str, budget: float) -> Dict:
        """캠페인 생성 API"""
        with perf_logger.measure_time("db_insert", table="campaigns"):
            # DB 작업 시뮬레이션
            time.sleep(0.1)
        
        return {"campaign_id": "camp_123", "status": "created"}
    
    @perf_logger.log_api_call
    def get_campaign_metrics(self, campaign_id: str) -> Dict:
        """캠페인 메트릭 조회 API"""
        with perf_logger.measure_time("metrics_calculation", campaign_id=campaign_id):
            # 복잡한 계산 시뮬레이션
            time.sleep(0.2)
        
        return {
            "impressions": 10000,
            "clicks": 500,
            "conversions": 50
        }
```

## 🛠️ 실습: 광고 시스템 로깅 구현

### 실습 1: 광고 요청 추적 시스템

```python
import logging
import json
from typing import Dict, Optional
import hashlib
from datetime import datetime, timedelta

class AdRequestTracker:
    """광고 요청 추적 시스템"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.request_cache = {}
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger("ad_request_tracker")
        logger.setLevel(logging.DEBUG)
        
        # JSON 포맷터
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_obj = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                
                # 추가 속성
                if hasattr(record, 'request_id'):
                    log_obj['request_id'] = record.request_id
                if hasattr(record, 'user_id'):
                    log_obj['user_id'] = record.user_id
                if hasattr(record, 'ad_id'):
                    log_obj['ad_id'] = record.ad_id
                
                return json.dumps(log_obj)
        
        # 핸들러 설정
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        
        return logger
    
    def generate_request_id(self, user_id: str, timestamp: float) -> str:
        """요청 ID 생성"""
        data = f"{user_id}:{timestamp}".encode()
        return hashlib.sha256(data).hexdigest()[:16]
    
    def track_ad_request(self, user_id: str, 
                        user_context: Dict,
                        available_ads: List[Dict]) -> str:
        """광고 요청 추적"""
        timestamp = datetime.now().timestamp()
        request_id = self.generate_request_id(user_id, timestamp)
        
        # 요청 정보 로깅
        self.logger.info(
            "Ad request received",
            extra={
                'request_id': request_id,
                'user_id': user_id,
                'user_context': user_context,
                'available_ads_count': len(available_ads)
            }
        )
        
        # 캐시에 저장
        self.request_cache[request_id] = {
            'user_id': user_id,
            'timestamp': timestamp,
            'context': user_context,
            'status': 'pending'
        }
        
        return request_id
    
    def track_ad_selection(self, request_id: str, 
                         selected_ad: Dict,
                         selection_reason: str):
        """광고 선택 추적"""
        if request_id not in self.request_cache:
            self.logger.warning(
                "Unknown request ID",
                extra={'request_id': request_id}
            )
            return
        
        self.logger.info(
            "Ad selected",
            extra={
                'request_id': request_id,
                'ad_id': selected_ad['id'],
                'selection_reason': selection_reason,
                'bid_price': selected_ad.get('bid_price')
            }
        )
        
        self.request_cache[request_id]['selected_ad'] = selected_ad['id']
        self.request_cache[request_id]['status'] = 'served'
    
    def track_ad_impression(self, request_id: str, ad_id: str):
        """노출 추적"""
        self.logger.info(
            "Ad impression",
            extra={
                'request_id': request_id,
                'ad_id': ad_id,
                'event_type': 'impression'
            }
        )
    
    def track_ad_click(self, request_id: str, ad_id: str, 
                      click_position: Dict):
        """클릭 추적"""
        self.logger.info(
            "Ad click",
            extra={
                'request_id': request_id,
                'ad_id': ad_id,
                'event_type': 'click',
                'click_x': click_position.get('x'),
                'click_y': click_position.get('y')
            }
        )
    
    def track_conversion(self, request_id: str, ad_id: str, 
                        conversion_value: float,
                        conversion_type: str):
        """전환 추적"""
        self.logger.info(
            "Conversion tracked",
            extra={
                'request_id': request_id,
                'ad_id': ad_id,
                'event_type': 'conversion',
                'conversion_value': conversion_value,
                'conversion_type': conversion_type
            }
        )
    
    def get_request_journey(self, request_id: str) -> Dict:
        """요청 여정 조회"""
        if request_id not in self.request_cache:
            return None
        
        journey = self.request_cache[request_id].copy()
        
        # 로그에서 관련 이벤트 수집 (실제로는 로그 저장소에서 조회)
        journey['events'] = [
            {'type': 'request', 'timestamp': journey['timestamp']},
            # 추가 이벤트들...
        ]
        
        return journey
```

### 실습 2: 에러 추적 및 알림 시스템

```python
import logging
from logging.handlers import SMTPHandler, HTTPHandler
import requests
from typing import List, Dict
import json

class AdSystemErrorTracker:
    """광고 시스템 에러 추적기"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = self._setup_error_logging()
        self.error_stats = {}
    
    def _setup_error_logging(self) -> logging.Logger:
        """에러 로깅 설정"""
        logger = logging.getLogger("ad_system_errors")
        logger.setLevel(logging.ERROR)
        
        # 파일 핸들러
        error_handler = logging.FileHandler('logs/errors.log')
        error_handler.setLevel(logging.ERROR)
        
        # 이메일 핸들러 (심각한 에러)
        if self.config.get('email_alerts'):
            email_handler = SMTPHandler(
                mailhost=self.config['smtp_host'],
                fromaddr=self.config['from_email'],
                toaddrs=self.config['alert_emails'],
                subject='광고 시스템 심각한 오류 발생'
            )
            email_handler.setLevel(logging.CRITICAL)
            logger.addHandler(email_handler)
        
        # Slack 핸들러 (커스텀)
        if self.config.get('slack_webhook'):
            slack_handler = SlackHandler(self.config['slack_webhook'])
            slack_handler.setLevel(logging.ERROR)
            logger.addHandler(slack_handler)
        
        # 포맷터
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
            'File: %(filename)s - Line: %(lineno)d - Function: %(funcName)s\n'
            '%(exc_info)s'
        )
        error_handler.setFormatter(formatter)
        
        logger.addHandler(error_handler)
        return logger
    
    def track_error(self, error_type: str, error_message: str, 
                   context: Dict = None, exception: Exception = None):
        """에러 추적"""
        # 에러 통계 업데이트
        if error_type not in self.error_stats:
            self.error_stats[error_type] = {
                'count': 0,
                'first_seen': datetime.now(),
                'last_seen': None
            }
        
        self.error_stats[error_type]['count'] += 1
        self.error_stats[error_type]['last_seen'] = datetime.now()
        
        # 에러 로깅
        error_data = {
            'error_type': error_type,
            'message': error_message,
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }
        
        if exception:
            error_data['exception'] = {
                'type': type(exception).__name__,
                'message': str(exception),
                'traceback': traceback.format_exc()
            }
            self.logger.error(
                f"{error_type}: {error_message}",
                exc_info=exception,
                extra=error_data
            )
        else:
            self.logger.error(
                f"{error_type}: {error_message}",
                extra=error_data
            )
        
        # 에러 빈도 체크
        self._check_error_frequency(error_type)
    
    def _check_error_frequency(self, error_type: str):
        """에러 빈도 체크 및 알림"""
        stats = self.error_stats[error_type]
        
        # 5분 내 10회 이상 발생 시 알림
        if stats['count'] >= 10:
            time_window = datetime.now() - stats['first_seen']
            if time_window.total_seconds() <= 300:  # 5분
                self.logger.critical(
                    f"높은 에러 빈도 감지: {error_type}",
                    extra={
                        'error_type': error_type,
                        'count': stats['count'],
                        'time_window_seconds': time_window.total_seconds()
                    }
                )
                
                # 통계 리셋
                self.error_stats[error_type]['count'] = 0
                self.error_stats[error_type]['first_seen'] = datetime.now()

class SlackHandler(logging.Handler):
    """Slack 알림 핸들러"""
    
    def __init__(self, webhook_url: str):
        super().__init__()
        self.webhook_url = webhook_url
    
    def emit(self, record):
        try:
            # Slack 메시지 포맷
            message = {
                'text': f':warning: *{record.levelname}* in Ad System',
                'attachments': [{
                    'color': 'danger' if record.levelname == 'CRITICAL' else 'warning',
                    'fields': [
                        {
                            'title': 'Error',
                            'value': record.getMessage(),
                            'short': False
                        },
                        {
                            'title': 'Location',
                            'value': f'{record.filename}:{record.lineno}',
                            'short': True
                        },
                        {
                            'title': 'Function',
                            'value': record.funcName,
                            'short': True
                        },
                        {
                            'title': 'Time',
                            'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'short': True
                        }
                    ]
                }]
            }
            
            # Webhook 전송
            requests.post(self.webhook_url, json=message)
            
        except Exception as e:
            self.handleError(record)
```

### 실습 3: 로그 분석 및 모니터링

```python
import re
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import pandas as pd

class AdLogAnalyzer:
    """광고 로그 분석기"""
    
    def __init__(self, log_path: str):
        self.log_path = log_path
        self.patterns = {
            'timestamp': r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',
            'level': r'"level":\s*"(\w+)"',
            'event_type': r'"event_type":\s*"(\w+)"',
            'ad_id': r'"ad_id":\s*"([^"]+)"',
            'user_id': r'"user_id":\s*"([^"]+)"',
            'error_type': r'"error_type":\s*"([^"]+)"'
        }
    
    def parse_log_line(self, line: str) -> Dict:
        """로그 라인 파싱"""
        try:
            # JSON 로그 파싱
            if line.strip().startswith('{'):
                return json.loads(line)
            
            # 일반 로그 파싱
            parsed = {}
            for key, pattern in self.patterns.items():
                match = re.search(pattern, line)
                if match:
                    parsed[key] = match.group(1)
            
            return parsed
            
        except Exception:
            return {}
    
    def analyze_logs(self, start_time: datetime, end_time: datetime) -> Dict:
        """로그 분석"""
        results = {
            'summary': {},
            'events': defaultdict(int),
            'errors': defaultdict(int),
            'performance': {},
            'anomalies': []
        }
        
        with open(self.log_path, 'r') as f:
            for line in f:
                log_entry = self.parse_log_line(line)
                
                if not log_entry:
                    continue
                
                # 시간 필터링
                if 'timestamp' in log_entry:
                    log_time = datetime.fromisoformat(
                        log_entry['timestamp'].replace('Z', '+00:00')
                    )
                    if not (start_time <= log_time <= end_time):
                        continue
                
                # 이벤트 집계
                if 'event_type' in log_entry:
                    results['events'][log_entry['event_type']] += 1
                
                # 에러 집계
                if log_entry.get('level') == 'ERROR':
                    error_type = log_entry.get('error_type', 'unknown')
                    results['errors'][error_type] += 1
                
                # 성능 데이터 수집
                if 'duration_ms' in log_entry:
                    operation = log_entry.get('operation', 'unknown')
                    if operation not in results['performance']:
                        results['performance'][operation] = []
                    results['performance'][operation].append(
                        float(log_entry['duration_ms'])
                    )
        
        # 요약 통계 계산
        results['summary'] = self._calculate_summary(results)
        
        # 이상 탐지
        results['anomalies'] = self._detect_anomalies(results)
        
        return results
    
    def _calculate_summary(self, results: Dict) -> Dict:
        """요약 통계 계산"""
        summary = {
            'total_events': sum(results['events'].values()),
            'total_errors': sum(results['errors'].values()),
            'event_breakdown': dict(results['events']),
            'error_breakdown': dict(results['errors']),
            'performance_summary': {}
        }
        
        # 성능 요약
        for operation, durations in results['performance'].items():
            if durations:
                summary['performance_summary'][operation] = {
                    'avg_ms': sum(durations) / len(durations),
                    'min_ms': min(durations),
                    'max_ms': max(durations),
                    'p95_ms': pd.Series(durations).quantile(0.95)
                }
        
        return summary
    
    def _detect_anomalies(self, results: Dict) -> List[Dict]:
        """이상 탐지"""
        anomalies = []
        
        # 높은 에러율 감지
        total_events = sum(results['events'].values())
        total_errors = sum(results['errors'].values())
        
        if total_events > 0:
            error_rate = total_errors / total_events
            if error_rate > 0.05:  # 5% 이상
                anomalies.append({
                    'type': 'high_error_rate',
                    'severity': 'high',
                    'value': error_rate,
                    'threshold': 0.05
                })
        
        # 느린 응답 감지
        for operation, durations in results['performance'].items():
            if durations:
                p95 = pd.Series(durations).quantile(0.95)
                if p95 > 1000:  # 1초 이상
                    anomalies.append({
                        'type': 'slow_response',
                        'severity': 'medium',
                        'operation': operation,
                        'p95_ms': p95,
                        'threshold_ms': 1000
                    })
        
        return anomalies
    
    def generate_report(self, analysis_results: Dict) -> str:
        """분석 리포트 생성"""
        report = []
        report.append("=" * 50)
        report.append("광고 시스템 로그 분석 리포트")
        report.append("=" * 50)
        
        # 요약
        summary = analysis_results['summary']
        report.append(f"\n총 이벤트 수: {summary['total_events']:,}")
        report.append(f"총 에러 수: {summary['total_errors']:,}")
        
        # 이벤트 분석
        report.append("\n이벤트 타입별 분포:")
        for event_type, count in summary['event_breakdown'].items():
            report.append(f"  - {event_type}: {count:,}")
        
        # 에러 분석
        if summary['error_breakdown']:
            report.append("\n에러 타입별 분포:")
            for error_type, count in summary['error_breakdown'].items():
                report.append(f"  - {error_type}: {count:,}")
        
        # 성능 분석
        if summary['performance_summary']:
            report.append("\n성능 메트릭:")
            for op, metrics in summary['performance_summary'].items():
                report.append(f"  {op}:")
                report.append(f"    - 평균: {metrics['avg_ms']:.2f}ms")
                report.append(f"    - P95: {metrics['p95_ms']:.2f}ms")
        
        # 이상 감지
        if analysis_results['anomalies']:
            report.append("\n⚠️  감지된 이상:")
            for anomaly in analysis_results['anomalies']:
                report.append(f"  - {anomaly['type']} ({anomaly['severity']})")
        
        return '\n'.join(report)
```

## 🚀 프로젝트: 통합 로깅 및 모니터링 시스템

### 프로젝트 구조
```
ad_logging_system/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── logger.py
│   ├── handlers.py
│   └── formatters.py
├── collectors/
│   ├── __init__.py
│   ├── event_collector.py
│   ├── metric_collector.py
│   └── error_collector.py
├── analyzers/
│   ├── __init__.py
│   ├── real_time_analyzer.py
│   ├── batch_analyzer.py
│   └── anomaly_detector.py
├── exporters/
│   ├── __init__.py
│   ├── elasticsearch_exporter.py
│   ├── prometheus_exporter.py
│   └── s3_exporter.py
└── dashboard/
    ├── __init__.py
    ├── api.py
    └── visualizations.py
```

### 통합 로깅 시스템 구현

```python
# core/logger.py
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager
import aioredis

class AdLoggingSystem:
    """광고 시스템 통합 로깅"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.loggers = {}
        self.handlers = []
        self.redis_client = None
        self._setup_logging()
    
    def _setup_logging(self):
        """로깅 시스템 초기화"""
        # 루트 로거 설정
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # 핸들러 추가
        self._add_console_handler()
        self._add_file_handler()
        self._add_structured_handler()
        
        if self.config.get('enable_remote_logging'):
            self._add_remote_handler()
    
    def _add_structured_handler(self):
        """구조화된 로깅 핸들러"""
        from pythonjsonlogger import jsonlogger
        
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s',
            timestamp=True
        )
        handler.setFormatter(formatter)
        
        self.handlers.append(handler)
        logging.getLogger().addHandler(handler)
    
    def get_logger(self, name: str, **default_fields) -> 'ContextualLogger':
        """컨텍스트 로거 생성"""
        if name not in self.loggers:
            self.loggers[name] = ContextualLogger(name, default_fields)
        return self.loggers[name]
    
    async def setup_redis(self):
        """Redis 연결 설정"""
        self.redis_client = await aioredis.create_redis_pool(
            self.config['redis_url']
        )
    
    async def log_event_async(self, event_type: str, data: Dict[str, Any]):
        """비동기 이벤트 로깅"""
        if not self.redis_client:
            await self.setup_redis()
        
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': event_type,
            'data': data
        }
        
        # Redis에 이벤트 저장
        await self.redis_client.lpush(
            f"logs:{event_type}",
            json.dumps(event)
        )
        
        # 스트림으로 발행
        await self.redis_client.xadd(
            'log_stream',
            {'event': json.dumps(event)}
        )

class ContextualLogger:
    """컨텍스트 정보를 포함하는 로거"""
    
    def __init__(self, name: str, default_fields: Dict[str, Any] = None):
        self.logger = logging.getLogger(name)
        self.default_fields = default_fields or {}
        self.context_stack = []
    
    @asynccontextmanager
    async def context(self, **fields):
        """임시 컨텍스트 추가"""
        self.context_stack.append(fields)
        try:
            yield self
        finally:
            self.context_stack.pop()
    
    def _merge_context(self, **fields) -> Dict[str, Any]:
        """컨텍스트 병합"""
        merged = self.default_fields.copy()
        
        # 스택의 모든 컨텍스트 병합
        for context in self.context_stack:
            merged.update(context)
        
        # 현재 필드 병합
        merged.update(fields)
        
        return merged
    
    def debug(self, message: str, **fields):
        context = self._merge_context(**fields)
        self.logger.debug(message, extra={'context': context})
    
    def info(self, message: str, **fields):
        context = self._merge_context(**fields)
        self.logger.info(message, extra={'context': context})
    
    def warning(self, message: str, **fields):
        context = self._merge_context(**fields)
        self.logger.warning(message, extra={'context': context})
    
    def error(self, message: str, exception: Exception = None, **fields):
        context = self._merge_context(**fields)
        
        if exception:
            context['exception'] = {
                'type': type(exception).__name__,
                'message': str(exception),
                'traceback': traceback.format_exc()
            }
        
        self.logger.error(message, extra={'context': context}, exc_info=exception)

# 광고 캠페인 로깅 예시
class CampaignLogger:
    """캠페인 전용 로거"""
    
    def __init__(self, logging_system: AdLoggingSystem):
        self.logging_system = logging_system
        self.logger = logging_system.get_logger(
            'campaign',
            service='campaign_manager'
        )
    
    async def log_campaign_created(self, campaign_id: str, 
                                  campaign_data: Dict[str, Any]):
        """캠페인 생성 로깅"""
        async with self.logger.context(campaign_id=campaign_id):
            self.logger.info(
                "Campaign created",
                action='create_campaign',
                campaign_name=campaign_data['name'],
                budget=campaign_data['budget'],
                start_date=campaign_data['start_date'],
                end_date=campaign_data['end_date']
            )
            
            # 이벤트 스트림에도 전송
            await self.logging_system.log_event_async(
                'campaign_created',
                {
                    'campaign_id': campaign_id,
                    **campaign_data
                }
            )
    
    async def log_campaign_performance(self, campaign_id: str,
                                     metrics: Dict[str, Any]):
        """캠페인 성과 로깅"""
        async with self.logger.context(
            campaign_id=campaign_id,
            metric_type='performance'
        ):
            self.logger.info(
                "Campaign performance update",
                impressions=metrics['impressions'],
                clicks=metrics['clicks'],
                conversions=metrics['conversions'],
                spend=metrics['spend'],
                ctr=metrics['ctr'],
                roas=metrics['roas']
            )
            
            # 성과가 목표치 이하인 경우 경고
            if metrics['roas'] < 1.0:
                self.logger.warning(
                    "Campaign underperforming",
                    roas=metrics['roas'],
                    target_roas=1.0
                )

# 실시간 로그 모니터링
class LogMonitor:
    """실시간 로그 모니터링"""
    
    def __init__(self, logging_system: AdLoggingSystem):
        self.logging_system = logging_system
        self.monitors = []
        self.alerts = []
    
    def add_monitor(self, monitor_func, name: str):
        """모니터 추가"""
        self.monitors.append({
            'name': name,
            'func': monitor_func,
            'active': True
        })
    
    async def start_monitoring(self):
        """모니터링 시작"""
        redis = await aioredis.create_redis_pool(
            self.logging_system.config['redis_url']
        )
        
        try:
            # 로그 스트림 구독
            stream_key = 'log_stream'
            last_id = '0'
            
            while True:
                # 스트림에서 로그 읽기
                messages = await redis.xread(
                    [stream_key],
                    latest_ids=[last_id],
                    count=100,
                    timeout=1000
                )
                
                for stream, stream_messages in messages:
                    for message_id, data in stream_messages:
                        last_id = message_id
                        
                        # 각 모니터 실행
                        event = json.loads(data[b'event'])
                        await self._process_event(event)
                
        finally:
            redis.close()
            await redis.wait_closed()
    
    async def _process_event(self, event: Dict[str, Any]):
        """이벤트 처리"""
        for monitor in self.monitors:
            if monitor['active']:
                try:
                    alert = await monitor['func'](event)
                    if alert:
                        await self._handle_alert(alert)
                except Exception as e:
                    print(f"Monitor error: {monitor['name']} - {e}")
    
    async def _handle_alert(self, alert: Dict[str, Any]):
        """알림 처리"""
        self.alerts.append(alert)
        
        # 알림 전송 (Slack, Email 등)
        if alert['severity'] == 'critical':
            await self._send_critical_alert(alert)
    
    async def _send_critical_alert(self, alert: Dict[str, Any]):
        """심각한 알림 전송"""
        # Slack 웹훅 호출 등
        pass

# 사용 예시
async def main():
    # 로깅 시스템 초기화
    config = {
        'redis_url': 'redis://localhost',
        'enable_remote_logging': True
    }
    
    logging_system = AdLoggingSystem(config)
    await logging_system.setup_redis()
    
    # 캠페인 로거 생성
    campaign_logger = CampaignLogger(logging_system)
    
    # 캠페인 생성 로깅
    await campaign_logger.log_campaign_created(
        'camp_123',
        {
            'name': '여름 세일 캠페인',
            'budget': 1000000,
            'start_date': '2024-06-01',
            'end_date': '2024-08-31'
        }
    )
    
    # 성과 로깅
    await campaign_logger.log_campaign_performance(
        'camp_123',
        {
            'impressions': 100000,
            'clicks': 2500,
            'conversions': 125,
            'spend': 500000,
            'ctr': 0.025,
            'roas': 1.5
        }
    )
    
    # 로그 모니터링 시작
    monitor = LogMonitor(logging_system)
    
    # 에러율 모니터 추가
    async def error_rate_monitor(event):
        if event['type'] == 'error':
            # 에러율 계산 로직
            return {
                'type': 'high_error_rate',
                'severity': 'warning',
                'message': 'Error rate exceeded threshold'
            }
        return None
    
    monitor.add_monitor(error_rate_monitor, 'error_rate')
    
    # 모니터링 시작
    await monitor.start_monitoring()

if __name__ == '__main__':
    asyncio.run(main())
```

## 📝 과제

### 과제 1: 분산 로깅 시스템
여러 서버에서 수집된 로그를 중앙화하는 시스템 구현:
- Fluentd/Logstash 연동
- 로그 집계 및 검색
- 실시간 대시보드

### 과제 2: 로그 기반 이상 탐지
머신러닝을 활용한 로그 이상 탐지 시스템:
- 정상 패턴 학습
- 실시간 이상 감지
- 자동 알림

### 과제 3: 성능 프로파일링 시스템
상세한 성능 프로파일링 및 분석:
- 함수별 실행 시간 추적
- 병목 지점 자동 감지
- 최적화 제안

### 과제 4: 컴플라이언스 로깅
규정 준수를 위한 감사 로깅 시스템:
- 개인정보 접근 로깅
- 로그 무결성 보장
- 보관 정책 자동화

## 🔗 참고 자료
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Structured Logging in Python](https://www.structlog.org/)
- [ELK Stack Tutorial](https://www.elastic.co/guide/index.html)
- [Distributed Tracing with OpenTelemetry](https://opentelemetry.io/docs/python/)

---

다음 장: [Chapter 06: Error Handling →](../06_error_handling/README.md)