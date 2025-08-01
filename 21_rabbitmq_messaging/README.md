# 21. RabbitMQ Messaging - 래빗MQ 메시징

## 📚 과정 소개
RabbitMQ를 활용한 광고 플랫폼의 비동기 메시징 시스템을 마스터합니다. 실시간 입찰, 이벤트 처리, 마이크로서비스 간 통신을 위한 메시지 큐 아키텍처를 학습합니다.

## 🎯 학습 목표
- 광고 플랫폼 메시징 아키텍처 설계
- 실시간 입찰 메시지 처리
- 이벤트 기반 캠페인 관리
- 메시지 큐 모니터링 및 최적화

## 📖 주요 내용

### RabbitMQ 기반 광고 메시징 시스템
```python
import pika
import json
import uuid
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from contextlib import contextmanager
import asyncio
import aio_pika
from concurrent.futures import ThreadPoolExecutor

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """메시지 타입"""
    BID_REQUEST = "bid_request"
    BID_RESPONSE = "bid_response"
    IMPRESSION = "impression"
    CLICK = "click"
    CONVERSION = "conversion"
    CAMPAIGN_UPDATE = "campaign_update"
    BUDGET_ALERT = "budget_alert"
    PERFORMANCE_UPDATE = "performance_update"

@dataclass
class AdMessage:
    """광고 메시지 기본 구조"""
    message_id: str
    message_type: MessageType
    timestamp: datetime
    data: Dict[str, Any]
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None

@dataclass
class BidRequest:
    """입찰 요청"""
    request_id: str
    user_id: str
    device_type: str
    location: Dict[str, float]  # lat, lng
    interests: List[str]
    floor_price: float
    timeout_ms: int = 120

@dataclass
class BidResponse:
    """입찰 응답"""
    request_id: str
    campaign_id: str
    ad_id: str
    bid_price: float
    creative_url: str
    landing_page: str

@dataclass
class AdEvent:
    """광고 이벤트"""
    event_id: str
    event_type: str  # impression, click, conversion
    user_id: str
    campaign_id: str
    ad_id: str
    timestamp: datetime
    value: float = 0.0

class RabbitMQConnection:
    """RabbitMQ 연결 관리"""
    
    def __init__(self, host: str = 'localhost', port: int = 5672,
                 username: str = 'guest', password: str = 'guest',
                 virtual_host: str = '/'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.virtual_host = virtual_host
        self.connection = None
        self.channel = None
        
    def connect(self):
        """연결 설정"""
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.virtual_host,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
        
    def disconnect(self):
        """연결 해제"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Disconnected from RabbitMQ")
    
    @contextmanager
    def get_channel(self):
        """채널 컨텍스트 매니저"""
        if not self.connection or self.connection.is_closed:
            self.connect()
        
        try:
            yield self.channel
        except Exception as e:
            logger.error(f"Channel error: {e}")
            raise
        
class AdExchangeMessaging:
    """광고 거래소 메시징 시스템"""
    
    def __init__(self, rabbitmq_config: Dict[str, Any]):
        self.connection = RabbitMQConnection(**rabbitmq_config)
        self.exchanges = {}
        self.queues = {}
        self.setup_infrastructure()
        
    def setup_infrastructure(self):
        """메시징 인프라 설정"""
        with self.connection.get_channel() as channel:
            # Exchange 설정
            exchanges = {
                'ad.bidding': {'type': 'direct', 'durable': True},
                'ad.events': {'type': 'topic', 'durable': True},
                'ad.campaigns': {'type': 'fanout', 'durable': True},
                'ad.alerts': {'type': 'direct', 'durable': True}
            }
            
            for exchange_name, config in exchanges.items():
                channel.exchange_declare(
                    exchange=exchange_name,
                    exchange_type=config['type'],
                    durable=config['durable']
                )
                self.exchanges[exchange_name] = config
                logger.info(f"Exchange '{exchange_name}' declared")
            
            # Queue 설정
            queues = {
                'bid.requests': {
                    'exchange': 'ad.bidding',
                    'routing_key': 'bid.request',
                    'durable': True,
                    'arguments': {'x-message-ttl': 120000}  # 2분 TTL
                },
                'bid.responses': {
                    'exchange': 'ad.bidding',
                    'routing_key': 'bid.response',
                    'durable': True,
                    'arguments': {'x-message-ttl': 120000}
                },
                'ad.impressions': {
                    'exchange': 'ad.events',
                    'routing_key': 'event.impression',
                    'durable': True
                },
                'ad.clicks': {
                    'exchange': 'ad.events',
                    'routing_key': 'event.click',
                    'durable': True
                },
                'ad.conversions': {
                    'exchange': 'ad.events',
                    'routing_key': 'event.conversion',
                    'durable': True
                },
                'campaign.updates': {
                    'exchange': 'ad.campaigns',
                    'routing_key': '',
                    'durable': True
                },
                'budget.alerts': {
                    'exchange': 'ad.alerts',
                    'routing_key': 'alert.budget',
                    'durable': True
                }
            }
            
            for queue_name, config in queues.items():
                channel.queue_declare(
                    queue=queue_name,
                    durable=config['durable'],
                    arguments=config.get('arguments', {})
                )
                
                channel.queue_bind(
                    exchange=config['exchange'],
                    queue=queue_name,
                    routing_key=config['routing_key']
                )
                
                self.queues[queue_name] = config
                logger.info(f"Queue '{queue_name}' declared and bound")
    
    def publish_message(self, exchange: str, routing_key: str, 
                       message: AdMessage, properties: Optional[Dict] = None):
        """메시지 발행"""
        with self.connection.get_channel() as channel:
            # 메시지 속성 설정
            msg_properties = pika.BasicProperties(
                message_id=message.message_id,
                timestamp=int(message.timestamp.timestamp()),
                correlation_id=message.correlation_id,
                reply_to=message.reply_to,
                delivery_mode=2,  # 영구 저장
                content_type='application/json'
            )
            
            if properties:
                for key, value in properties.items():
                    setattr(msg_properties, key, value)
            
            # 메시지 직렬화
            message_body = json.dumps({
                'message_id': message.message_id,
                'message_type': message.message_type.value,
                'timestamp': message.timestamp.isoformat(),
                'data': message.data,
                'correlation_id': message.correlation_id,
                'reply_to': message.reply_to
            })
            
            # 메시지 발행
            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message_body,
                properties=msg_properties
            )
            
            logger.info(f"Message published to {exchange}/{routing_key}")
    
    def consume_messages(self, queue: str, callback: Callable,
                        auto_ack: bool = False, prefetch_count: int = 10):
        """메시지 소비"""
        with self.connection.get_channel() as channel:
            channel.basic_qos(prefetch_count=prefetch_count)
            
            def wrapper(ch, method, properties, body):
                try:
                    # 메시지 역직렬화
                    message_data = json.loads(body)
                    message = AdMessage(
                        message_id=message_data['message_id'],
                        message_type=MessageType(message_data['message_type']),
                        timestamp=datetime.fromisoformat(message_data['timestamp']),
                        data=message_data['data'],
                        correlation_id=message_data.get('correlation_id'),
                        reply_to=message_data.get('reply_to')
                    )
                    
                    # 콜백 실행
                    result = callback(message)
                    
                    # 수동 ACK
                    if not auto_ack:
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        
                    return result
                    
                except Exception as e:
                    logger.error(f"Message processing error: {e}")
                    if not auto_ack:
                        ch.basic_nack(
                            delivery_tag=method.delivery_tag,
                            requeue=True
                        )
            
            channel.basic_consume(
                queue=queue,
                on_message_callback=wrapper,
                auto_ack=auto_ack
            )
            
            logger.info(f"Started consuming from queue: {queue}")
            channel.start_consuming()

class BiddingEngine:
    """실시간 입찰 엔진"""
    
    def __init__(self, messaging: AdExchangeMessaging):
        self.messaging = messaging
        self.active_campaigns = {}
        self.bid_responses = {}
        
    def start_bidding_service(self):
        """입찰 서비스 시작"""
        logger.info("Starting bidding service...")
        
        # 입찰 요청 처리
        threading.Thread(
            target=self._process_bid_requests,
            daemon=True
        ).start()
        
        # 입찰 응답 처리
        threading.Thread(
            target=self._process_bid_responses,
            daemon=True
        ).start()
    
    def _process_bid_requests(self):
        """입찰 요청 처리"""
        def handle_bid_request(message: AdMessage):
            bid_request_data = message.data
            bid_request = BidRequest(**bid_request_data)
            
            logger.info(f"Processing bid request: {bid_request.request_id}")
            
            # 입찰 로직 실행
            bid_response = self._generate_bid(bid_request)
            
            if bid_response:
                # 입찰 응답 발행
                response_message = AdMessage(
                    message_id=str(uuid.uuid4()),
                    message_type=MessageType.BID_RESPONSE,
                    timestamp=datetime.now(),
                    data=asdict(bid_response),
                    correlation_id=message.correlation_id
                )
                
                self.messaging.publish_message(
                    exchange='ad.bidding',
                    routing_key='bid.response',
                    message=response_message
                )
                
                logger.info(f"Bid response sent for request: {bid_request.request_id}")
        
        self.messaging.consume_messages(
            queue='bid.requests',
            callback=handle_bid_request
        )
    
    def _process_bid_responses(self):
        """입찰 응답 처리"""
        def handle_bid_response(message: AdMessage):
            bid_response_data = message.data
            bid_response = BidResponse(**bid_response_data)
            
            logger.info(f"Received bid response: {bid_response.request_id}")
            
            # 입찰 응답 저장
            self.bid_responses[bid_response.request_id] = bid_response
            
            # 입찰 성공 시 추가 처리
            self._process_successful_bid(bid_response)
        
        self.messaging.consume_messages(
            queue='bid.responses',
            callback=handle_bid_response
        )
    
    def _generate_bid(self, bid_request: BidRequest) -> Optional[BidResponse]:
        """입찰 생성"""
        # 타겟팅 로직
        matching_campaigns = self._find_matching_campaigns(bid_request)
        
        if not matching_campaigns:
            return None
        
        # 최고 입찰가 선택
        best_campaign = max(matching_campaigns, key=lambda c: c['bid_price'])
        
        if best_campaign['bid_price'] < bid_request.floor_price:
            return None
        
        return BidResponse(
            request_id=bid_request.request_id,
            campaign_id=best_campaign['campaign_id'],
            ad_id=best_campaign['ad_id'],
            bid_price=best_campaign['bid_price'],
            creative_url=best_campaign['creative_url'],
            landing_page=best_campaign['landing_page']
        )
    
    def _find_matching_campaigns(self, bid_request: BidRequest) -> List[Dict]:
        """매칭되는 캠페인 찾기"""
        # 간단한 매칭 로직 (실제로는 더 복잡)
        matching_campaigns = []
        
        for campaign_id, campaign in self.active_campaigns.items():
            # 타겟팅 조건 확인
            if self._is_campaign_match(campaign, bid_request):
                matching_campaigns.append(campaign)
        
        return matching_campaigns
    
    def _is_campaign_match(self, campaign: Dict, bid_request: BidRequest) -> bool:
        """캠페인 매칭 여부 확인"""
        # 지역 타겟팅
        if 'target_locations' in campaign:
            if not self._is_location_match(campaign['target_locations'], bid_request.location):
                return False
        
        # 관심사 타겟팅
        if 'target_interests' in campaign:
            if not set(campaign['target_interests']) & set(bid_request.interests):
                return False
        
        # 예산 확인
        if campaign.get('daily_budget', 0) <= campaign.get('spent_budget', 0):
            return False
        
        return True
    
    def _is_location_match(self, target_locations: List[Dict], 
                          user_location: Dict[str, float]) -> bool:
        """지역 매칭 확인"""
        # 간단한 거리 계산
        for target in target_locations:
            distance = self._calculate_distance(
                user_location['lat'], user_location['lng'],
                target['lat'], target['lng']
            )
            if distance <= target.get('radius', 10):  # 기본 10km
                return True
        return False
    
    def _calculate_distance(self, lat1: float, lng1: float, 
                           lat2: float, lng2: float) -> float:
        """두 지점 간 거리 계산 (km)"""
        import math
        
        R = 6371  # 지구 반지름 (km)
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlng/2) * math.sin(dlng/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def _process_successful_bid(self, bid_response: BidResponse):
        """성공한 입찰 처리"""
        # 예산 차감
        campaign = self.active_campaigns.get(bid_response.campaign_id)
        if campaign:
            campaign['spent_budget'] = campaign.get('spent_budget', 0) + bid_response.bid_price
            
            # 예산 경고 확인
            if campaign['spent_budget'] >= campaign['daily_budget'] * 0.9:
                self._send_budget_alert(bid_response.campaign_id, campaign)

    def _send_budget_alert(self, campaign_id: str, campaign: Dict):
        """예산 경고 발송"""
        alert_message = AdMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.BUDGET_ALERT,
            timestamp=datetime.now(),
            data={
                'campaign_id': campaign_id,
                'spent_budget': campaign['spent_budget'],
                'daily_budget': campaign['daily_budget'],
                'alert_type': 'budget_warning'
            }
        )
        
        self.messaging.publish_message(
            exchange='ad.alerts',
            routing_key='alert.budget',
            message=alert_message
        )

class EventTracker:
    """광고 이벤트 추적기"""
    
    def __init__(self, messaging: AdExchangeMessaging):
        self.messaging = messaging
        self.event_handlers = {
            'impression': self._handle_impression,
            'click': self._handle_click,
            'conversion': self._handle_conversion
        }
        
    def start_event_tracking(self):
        """이벤트 추적 시작"""
        logger.info("Starting event tracking service...")
        
        # 각 이벤트 타입별 처리
        for event_type in ['impressions', 'clicks', 'conversions']:
            threading.Thread(
                target=self._track_events,
                args=(f'ad.{event_type}',),
                daemon=True
            ).start()
    
    def track_ad_event(self, event: AdEvent):
        """광고 이벤트 추적"""
        message = AdMessage(
            message_id=str(uuid.uuid4()),
            message_type=getattr(MessageType, event.event_type.upper()),
            timestamp=event.timestamp,
            data=asdict(event)
        )
        
        routing_key = f'event.{event.event_type}'
        
        self.messaging.publish_message(
            exchange='ad.events',
            routing_key=routing_key,
            message=message
        )
        
        logger.info(f"Tracked {event.event_type} event: {event.event_id}")
    
    def _track_events(self, queue_name: str):
        """이벤트 추적 처리"""
        def handle_event(message: AdMessage):
            event_data = message.data
            event = AdEvent(**event_data)
            
            # 이벤트 타입별 처리
            handler = self.event_handlers.get(event.event_type)
            if handler:
                handler(event)
            
            # 실시간 성과 업데이트
            self._update_performance_metrics(event)
        
        self.messaging.consume_messages(
            queue=queue_name,
            callback=handle_event
        )
    
    def _handle_impression(self, event: AdEvent):
        """노출 이벤트 처리"""
        logger.info(f"Impression tracked: {event.campaign_id}")
        # 노출 수 증가, 빈도 캡 확인 등
        
    def _handle_click(self, event: AdEvent):
        """클릭 이벤트 처리"""
        logger.info(f"Click tracked: {event.campaign_id}")
        # CTR 계산, 클릭 사기 탐지 등
        
    def _handle_conversion(self, event: AdEvent):
        """전환 이벤트 처리"""
        logger.info(f"Conversion tracked: {event.campaign_id}, value: {event.value}")
        # ROI 계산, 어트리뷰션 분석 등
    
    def _update_performance_metrics(self, event: AdEvent):
        """실시간 성과 지표 업데이트"""
        performance_update = AdMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.PERFORMANCE_UPDATE,
            timestamp=datetime.now(),
            data={
                'campaign_id': event.campaign_id,
                'event_type': event.event_type,
                'timestamp': event.timestamp.isoformat(),
                'value': event.value
            }
        )
        
        self.messaging.publish_message(
            exchange='ad.campaigns',
            routing_key='',
            message=performance_update
        )

class CampaignManager:
    """캠페인 관리자"""
    
    def __init__(self, messaging: AdExchangeMessaging):
        self.messaging = messaging
        self.campaigns = {}
        
    def start_campaign_management(self):
        """캠페인 관리 시작"""
        logger.info("Starting campaign management service...")
        
        threading.Thread(
            target=self._process_campaign_updates,
            daemon=True
        ).start()
        
        threading.Thread(
            target=self._process_budget_alerts,
            daemon=True
        ).start()
    
    def update_campaign(self, campaign_id: str, updates: Dict[str, Any]):
        """캠페인 업데이트"""
        message = AdMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.CAMPAIGN_UPDATE,
            timestamp=datetime.now(),
            data={
                'campaign_id': campaign_id,
                'updates': updates,
                'updated_by': 'system'
            }
        )
        
        self.messaging.publish_message(
            exchange='ad.campaigns',
            routing_key='',
            message=message
        )
        
        logger.info(f"Campaign update sent: {campaign_id}")
    
    def _process_campaign_updates(self):
        """캠페인 업데이트 처리"""
        def handle_campaign_update(message: AdMessage):
            update_data = message.data
            campaign_id = update_data['campaign_id']
            updates = update_data['updates']
            
            # 캠페인 정보 업데이트
            if campaign_id in self.campaigns:
                self.campaigns[campaign_id].update(updates)
            else:
                self.campaigns[campaign_id] = updates
            
            logger.info(f"Campaign updated: {campaign_id}")
        
        self.messaging.consume_messages(
            queue='campaign.updates',
            callback=handle_campaign_update
        )
    
    def _process_budget_alerts(self):
        """예산 경고 처리"""
        def handle_budget_alert(message: AdMessage):
            alert_data = message.data
            campaign_id = alert_data['campaign_id']
            
            logger.warning(f"Budget alert for campaign: {campaign_id}")
            
            # 자동 캠페인 일시정지 (90% 이상 소진 시)
            if alert_data['spent_budget'] >= alert_data['daily_budget'] * 0.9:
                self.update_campaign(campaign_id, {'status': 'paused'})
                logger.info(f"Campaign auto-paused: {campaign_id}")
        
        self.messaging.consume_messages(
            queue='budget.alerts',
            callback=handle_budget_alert
        )

class MessageMonitor:
    """메시지 모니터링"""
    
    def __init__(self, messaging: AdExchangeMessaging):
        self.messaging = messaging
        self.metrics = {
            'messages_published': 0,
            'messages_consumed': 0,
            'errors': 0,
            'processing_times': []
        }
        
    def start_monitoring(self):
        """모니터링 시작"""
        logger.info("Starting message monitoring...")
        
        # 메트릭 리포트 스레드
        threading.Thread(
            target=self._report_metrics,
            daemon=True
        ).start()
    
    def _report_metrics(self):
        """메트릭 리포트"""
        while True:
            time.sleep(60)  # 1분마다 리포트
            
            if self.metrics['processing_times']:
                avg_processing_time = sum(self.metrics['processing_times']) / len(self.metrics['processing_times'])
                self.metrics['processing_times'] = []  # 리셋
            else:
                avg_processing_time = 0
            
            logger.info(f"Message Metrics - Published: {self.metrics['messages_published']}, "
                       f"Consumed: {self.metrics['messages_consumed']}, "
                       f"Errors: {self.metrics['errors']}, "
                       f"Avg Processing Time: {avg_processing_time:.2f}ms")

# 사용 예시
def example_rabbitmq_ad_platform():
    """RabbitMQ 광고 플랫폼 예시"""
    # RabbitMQ 설정
    rabbitmq_config = {
        'host': 'localhost',
        'port': 5672,
        'username': 'guest',
        'password': 'guest'
    }
    
    # 메시징 시스템 초기화
    messaging = AdExchangeMessaging(rabbitmq_config)
    
    # 입찰 엔진 시작
    bidding_engine = BiddingEngine(messaging)
    
    # 샘플 캠페인 설정
    bidding_engine.active_campaigns = {
        'campaign_1': {
            'campaign_id': 'campaign_1',
            'ad_id': 'ad_1',
            'bid_price': 2.5,
            'daily_budget': 1000,
            'spent_budget': 0,
            'creative_url': 'https://example.com/creative1.jpg',
            'landing_page': 'https://example.com/landing1',
            'target_interests': ['tech', 'gadgets'],
            'target_locations': [{'lat': 37.5665, 'lng': 126.9780, 'radius': 10}]
        }
    }
    
    # 이벤트 추적기 시작
    event_tracker = EventTracker(messaging)
    
    # 캠페인 관리자 시작
    campaign_manager = CampaignManager(messaging)
    
    # 모니터링 시작
    monitor = MessageMonitor(messaging)
    monitor.start_monitoring()
    
    # 샘플 입찰 요청 발송
    def send_sample_bid_request():
        bid_request = BidRequest(
            request_id=str(uuid.uuid4()),
            user_id='user_123',
            device_type='mobile',
            location={'lat': 37.5665, 'lng': 126.9780},
            interests=['tech', 'gaming'],
            floor_price=1.0
        )
        
        message = AdMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.BID_REQUEST,
            timestamp=datetime.now(),
            data=asdict(bid_request)
        )
        
        messaging.publish_message(
            exchange='ad.bidding',
            routing_key='bid.request',
            message=message
        )
        
        logger.info(f"Sample bid request sent: {bid_request.request_id}")
    
    # 샘플 광고 이벤트 발송
    def send_sample_ad_event():
        event = AdEvent(
            event_id=str(uuid.uuid4()),
            event_type='impression',
            user_id='user_123',
            campaign_id='campaign_1',
            ad_id='ad_1',
            timestamp=datetime.now()
        )
        
        event_tracker.track_ad_event(event)
    
    # 서비스 시작
    try:
        print("Starting ad platform services...")
        bidding_engine.start_bidding_service()
        event_tracker.start_event_tracking()
        campaign_manager.start_campaign_management()
        
        # 샘플 데이터 발송
        time.sleep(2)
        send_sample_bid_request()
        send_sample_ad_event()
        
        # 캠페인 업데이트 테스트
        time.sleep(1)
        campaign_manager.update_campaign('campaign_1', {'daily_budget': 1500})
        
        print("Services running... Press Ctrl+C to stop")
        
        # 계속 실행
        while True:
            time.sleep(10)
            send_sample_bid_request()
            send_sample_ad_event()
            
    except KeyboardInterrupt:
        print("Shutting down services...")
        messaging.connection.disconnect()

if __name__ == "__main__":
    example_rabbitmq_ad_platform()
```

## 🚀 프로젝트
1. **실시간 입찰 메시징 시스템**
2. **이벤트 기반 광고 추적**
3. **캠페인 관리 자동화**
4. **메시지 큐 모니터링 대시보드**