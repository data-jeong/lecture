# 08. ORM & Database - ORM과 데이터베이스

## 📚 과정 소개
SQLAlchemy, PostgreSQL, DuckDB를 활용한 대규모 광고 데이터 관리를 마스터합니다. 고성능 쿼리 최적화부터 데이터 모델링까지 포괄적으로 다룹니다.

## 🎯 학습 목표
- 광고 도메인 데이터 모델링
- SQLAlchemy ORM 고급 활용
- 대용량 데이터 쿼리 최적화
- 실시간 분석 데이터베이스 설계

## 📖 주요 내용

### 광고 도메인 데이터 모델
```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from datetime import datetime
import uuid
from typing import List, Dict, Optional

Base = declarative_base()

class Advertiser(Base):
    """광고주 모델"""
    __tablename__ = 'advertisers'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    industry = Column(String(50))
    monthly_budget = Column(Float, default=0)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    campaigns = relationship("Campaign", back_populates="advertiser")
    
    __table_args__ = (
        Index('idx_advertiser_status', 'status'),
        Index('idx_advertiser_industry', 'industry'),
    )

class Campaign(Base):
    """캠페인 모델"""
    __tablename__ = 'campaigns'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    advertiser_id = Column(UUID(as_uuid=True), ForeignKey('advertisers.id'), nullable=False)
    name = Column(String(200), nullable=False)
    objective = Column(String(50))  # awareness, consideration, conversion
    budget_type = Column(String(20))  # daily, lifetime
    budget_amount = Column(Float, nullable=False)
    bid_strategy = Column(String(30))  # cpc, cpm, cpa, target_cpa
    target_cpa = Column(Float)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    status = Column(String(20), default='draft')  # draft, active, paused, completed
    
    # 타겟팅 정보
    targeting_config = Column(JSONB)
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    advertiser = relationship("Advertiser", back_populates="campaigns")
    ad_groups = relationship("AdGroup", back_populates="campaign")
    campaign_metrics = relationship("CampaignMetrics", back_populates="campaign")
    
    __table_args__ = (
        Index('idx_campaign_advertiser_status', 'advertiser_id', 'status'),
        Index('idx_campaign_dates', 'start_date', 'end_date'),
        Index('idx_campaign_objective', 'objective'),
    )

class AdGroup(Base):
    """광고 그룹 모델"""
    __tablename__ = 'ad_groups'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('campaigns.id'), nullable=False)
    name = Column(String(200), nullable=False)
    bid_amount = Column(Float)
    status = Column(String(20), default='active')
    
    # 키워드 및 오디언스 타겟팅
    keywords = Column(ARRAY(String))
    negative_keywords = Column(ARRAY(String))
    audience_segments = Column(JSONB)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    campaign = relationship("Campaign", back_populates="ad_groups")
    ads = relationship("Ad", back_populates="ad_group")
    
    __table_args__ = (
        Index('idx_adgroup_campaign_status', 'campaign_id', 'status'),
    )

class Ad(Base):
    """광고 모델"""
    __tablename__ = 'ads'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ad_group_id = Column(UUID(as_uuid=True), ForeignKey('ad_groups.id'), nullable=False)
    name = Column(String(200), nullable=False)
    ad_type = Column(String(30))  # text, image, video, carousel
    
    # 크리에이티브 내용
    headline = Column(String(100))
    description = Column(Text)
    image_url = Column(String(500))
    video_url = Column(String(500))
    landing_page_url = Column(String(500), nullable=False)
    
    # 상태 및 승인
    status = Column(String(20), default='under_review')
    approval_status = Column(String(20), default='pending')
    disapproval_reason = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    ad_group = relationship("AdGroup", back_populates="ads")
    
    __table_args__ = (
        Index('idx_ad_adgroup_status', 'ad_group_id', 'status'),
        Index('idx_ad_type', 'ad_type'),
    )

class CampaignMetrics(Base):
    """캠페인 성과 지표"""
    __tablename__ = 'campaign_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('campaigns.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    
    # 기본 지표
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    conversions = Column(Integer, default=0)
    conversion_value = Column(Float, default=0.0)
    
    # 계산된 지표
    ctr = Column(Float, default=0.0)  # Click Through Rate
    cpc = Column(Float, default=0.0)  # Cost Per Click
    cpm = Column(Float, default=0.0)  # Cost Per Mille
    cpa = Column(Float, default=0.0)  # Cost Per Acquisition
    roas = Column(Float, default=0.0)  # Return on Ad Spend
    
    # 디바이스별 세분화
    desktop_impressions = Column(Integer, default=0)
    mobile_impressions = Column(Integer, default=0)
    tablet_impressions = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    campaign = relationship("Campaign", back_populates="campaign_metrics")
    
    __table_args__ = (
        Index('idx_metrics_campaign_date', 'campaign_id', 'date'),
        Index('idx_metrics_date', 'date'),
        UniqueConstraint('campaign_id', 'date', name='uq_campaign_date'),
    )

class UserEvent(Base):
    """사용자 이벤트 로그"""
    __tablename__ = 'user_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), nullable=False)
    session_id = Column(String(100))
    event_type = Column(String(50), nullable=False)  # impression, click, conversion
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 광고 관련 정보
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('campaigns.id'))
    ad_id = Column(UUID(as_uuid=True), ForeignKey('ads.id'))
    
    # 컨텍스트 정보
    device_type = Column(String(20))
    browser = Column(String(50))
    os = Column(String(50))
    country = Column(String(10))
    city = Column(String(100))
    
    # 추가 속성
    properties = Column(JSONB)
    
    __table_args__ = (
        Index('idx_user_events_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_user_events_campaign', 'campaign_id'),
        Index('idx_user_events_type_timestamp', 'event_type', 'timestamp'),
    )

class DatabaseManager:
    """데이터베이스 관리자"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            echo=False  # 프로덕션에서는 False
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """테이블 생성"""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        """세션 생성"""
        return self.SessionLocal()
    
    def create_campaign_with_structure(self, advertiser_data: Dict, 
                                     campaign_data: Dict,
                                     ad_groups_data: List[Dict]) -> str:
        """캠페인 전체 구조 생성"""
        session = self.get_session()
        
        try:
            # 광고주 생성 또는 조회
            advertiser = session.query(Advertiser).filter_by(
                email=advertiser_data['email']
            ).first()
            
            if not advertiser:
                advertiser = Advertiser(**advertiser_data)
                session.add(advertiser)
                session.flush()
            
            # 캠페인 생성
            campaign_data['advertiser_id'] = advertiser.id
            campaign = Campaign(**campaign_data)
            session.add(campaign)
            session.flush()
            
            # 광고 그룹들 생성
            for ag_data in ad_groups_data:
                ag_data['campaign_id'] = campaign.id
                ad_group = AdGroup(**ag_data)
                session.add(ad_group)
            
            session.commit()
            return str(campaign.id)
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_campaign_performance(self, campaign_id: str, 
                               start_date: datetime, 
                               end_date: datetime) -> Dict:
        """캠페인 성과 조회"""
        session = self.get_session()
        
        try:
            # 기본 성과 지표 조회
            metrics = session.query(CampaignMetrics).filter(
                CampaignMetrics.campaign_id == campaign_id,
                CampaignMetrics.date >= start_date,
                CampaignMetrics.date <= end_date
            ).all()
            
            # 집계 계산
            total_metrics = {
                'impressions': sum(m.impressions for m in metrics),
                'clicks': sum(m.clicks for m in metrics),
                'cost': sum(m.cost for m in metrics),
                'conversions': sum(m.conversions for m in metrics),
                'conversion_value': sum(m.conversion_value for m in metrics)
            }
            
            # 계산된 지표
            if total_metrics['impressions'] > 0:
                total_metrics['ctr'] = total_metrics['clicks'] / total_metrics['impressions']
                total_metrics['cpm'] = (total_metrics['cost'] / total_metrics['impressions']) * 1000
            
            if total_metrics['clicks'] > 0:
                total_metrics['cpc'] = total_metrics['cost'] / total_metrics['clicks']
            
            if total_metrics['conversions'] > 0:
                total_metrics['cpa'] = total_metrics['cost'] / total_metrics['conversions']
            
            if total_metrics['cost'] > 0:
                total_metrics['roas'] = total_metrics['conversion_value'] / total_metrics['cost']
            
            return total_metrics
            
        finally:
            session.close()
    
    def bulk_insert_events(self, events_data: List[Dict]):
        """이벤트 대량 삽입"""
        session = self.get_session()
        
        try:
            # SQLAlchemy Core를 사용한 대량 삽입
            session.execute(
                UserEvent.__table__.insert(),
                events_data
            )
            session.commit()
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

class AnalyticsQueries:
    """분석 쿼리 클래스"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
    def get_top_performing_campaigns(self, metric: str = 'roas', 
                                   limit: int = 10) -> List[Dict]:
        """최고 성과 캠페인 조회"""
        session = self.db.get_session()
        
        try:
            # 서브쿼리로 캠페인별 집계
            from sqlalchemy import func, desc
            
            subquery = session.query(
                CampaignMetrics.campaign_id,
                func.sum(CampaignMetrics.impressions).label('total_impressions'),
                func.sum(CampaignMetrics.clicks).label('total_clicks'),
                func.sum(CampaignMetrics.cost).label('total_cost'),
                func.sum(CampaignMetrics.conversions).label('total_conversions'),
                func.sum(CampaignMetrics.conversion_value).label('total_value')
            ).group_by(CampaignMetrics.campaign_id).subquery()
            
            # 계산된 지표와 함께 조회
            query = session.query(
                Campaign.name,
                subquery.c.total_impressions,
                subquery.c.total_clicks,
                subquery.c.total_cost,
                subquery.c.total_conversions,
                subquery.c.total_value,
                (subquery.c.total_value / subquery.c.total_cost).label('roas'),
                (subquery.c.total_clicks.cast(Float) / subquery.c.total_impressions).label('ctr')
            ).join(
                subquery, Campaign.id == subquery.c.campaign_id
            ).filter(
                subquery.c.total_cost > 0
            )
            
            if metric == 'roas':
                query = query.order_by(desc('roas'))
            elif metric == 'ctr':
                query = query.order_by(desc('ctr'))
            
            results = query.limit(limit).all()
            
            return [
                {
                    'campaign_name': r.name,
                    'impressions': r.total_impressions,
                    'clicks': r.total_clicks,
                    'cost': r.total_cost,
                    'conversions': r.total_conversions,
                    'conversion_value': r.total_value,
                    'roas': float(r.roas) if r.roas else 0,
                    'ctr': float(r.ctr) if r.ctr else 0
                }
                for r in results
            ]
            
        finally:
            session.close()
    
    def get_user_journey_analysis(self, user_id: str) -> List[Dict]:
        """사용자 여정 분석"""
        session = self.db.get_session()
        
        try:
            events = session.query(UserEvent).filter(
                UserEvent.user_id == user_id
            ).order_by(UserEvent.timestamp).all()
            
            journey = []
            for event in events:
                journey.append({
                    'timestamp': event.timestamp,
                    'event_type': event.event_type,
                    'campaign_id': str(event.campaign_id) if event.campaign_id else None,
                    'device_type': event.device_type,
                    'properties': event.properties
                })
            
            return journey
            
        finally:
            session.close()
    
    def get_cohort_analysis(self, start_date: datetime, 
                          periods: int = 12) -> Dict:
        """코호트 분석"""
        session = self.db.get_session()
        
        try:
            from sqlalchemy import text
            
            # PostgreSQL의 고급 기능 사용
            query = text("""
                WITH user_cohorts AS (
                    SELECT 
                        user_id,
                        DATE_TRUNC('month', MIN(timestamp)) as cohort_month,
                        MIN(timestamp) as first_event
                    FROM user_events 
                    WHERE event_type = 'conversion'
                    AND timestamp >= :start_date
                    GROUP BY user_id
                ),
                user_activities AS (
                    SELECT 
                        ue.user_id,
                        uc.cohort_month,
                        DATE_TRUNC('month', ue.timestamp) as activity_month,
                        EXTRACT(EPOCH FROM (
                            DATE_TRUNC('month', ue.timestamp) - uc.cohort_month
                        )) / (30 * 24 * 60 * 60) as period_number
                    FROM user_events ue
                    JOIN user_cohorts uc ON ue.user_id = uc.user_id
                    WHERE ue.event_type = 'conversion'
                )
                SELECT 
                    cohort_month,
                    period_number,
                    COUNT(DISTINCT user_id) as users
                FROM user_activities
                WHERE period_number >= 0 AND period_number < :periods
                GROUP BY cohort_month, period_number
                ORDER BY cohort_month, period_number
            """)
            
            results = session.execute(query, {
                'start_date': start_date,
                'periods': periods
            })
            
            cohort_data = {}
            for row in results:
                cohort_key = row.cohort_month.strftime('%Y-%m')
                if cohort_key not in cohort_data:
                    cohort_data[cohort_key] = {}
                cohort_data[cohort_key][int(row.period_number)] = row.users
            
            return cohort_data
            
        finally:
            session.close()

# DuckDB 통합 (고속 분석용)
class DuckDBAnalytics:
    """DuckDB를 활용한 고속 분석"""
    
    def __init__(self, db_path: str = ":memory:"):
        import duckdb
        self.conn = duckdb.connect(db_path)
        
    def load_data_from_postgres(self, postgres_url: str):
        """PostgreSQL에서 데이터 로드"""
        self.conn.execute(f"""
            INSTALL postgres;
            LOAD postgres;
            
            CREATE TABLE campaign_metrics AS 
            SELECT * FROM postgres_scan('{postgres_url}', 'public', 'campaign_metrics');
            
            CREATE TABLE user_events AS 
            SELECT * FROM postgres_scan('{postgres_url}', 'public', 'user_events');
        """)
    
    def fast_aggregation_analysis(self) -> Dict:
        """고속 집계 분석"""
        # 캠페인별 성과 집계
        campaign_performance = self.conn.execute("""
            SELECT 
                campaign_id,
                SUM(impressions) as total_impressions,
                SUM(clicks) as total_clicks,
                SUM(cost) as total_cost,
                SUM(conversions) as total_conversions,
                AVG(ctr) as avg_ctr,
                AVG(roas) as avg_roas
            FROM campaign_metrics
            GROUP BY campaign_id
            ORDER BY total_cost DESC
            LIMIT 20
        """).fetchall()
        
        # 시간별 트렌드 분석
        hourly_trends = self.conn.execute("""
            SELECT 
                EXTRACT(hour FROM timestamp) as hour,
                COUNT(*) as event_count,
                COUNT(DISTINCT user_id) as unique_users
            FROM user_events
            WHERE DATE(timestamp) = CURRENT_DATE
            GROUP BY hour
            ORDER BY hour
        """).fetchall()
        
        return {
            'campaign_performance': campaign_performance,
            'hourly_trends': hourly_trends
        }
    
    def attribution_analysis(self) -> List[Dict]:
        """어트리뷰션 분석"""
        results = self.conn.execute("""
            WITH user_journeys AS (
                SELECT 
                    user_id,
                    campaign_id,
                    event_type,
                    timestamp,
                    LAG(campaign_id) OVER (
                        PARTITION BY user_id 
                        ORDER BY timestamp
                    ) as prev_campaign,
                    LEAD(event_type) OVER (
                        PARTITION BY user_id 
                        ORDER BY timestamp
                    ) as next_event
                FROM user_events
                WHERE campaign_id IS NOT NULL
            ),
            conversions_with_journey AS (
                SELECT 
                    user_id,
                    campaign_id,
                    COUNT(*) OVER (
                        PARTITION BY user_id 
                        ORDER BY timestamp 
                        ROWS UNBOUNDED PRECEDING
                    ) as touchpoint_position
                FROM user_journeys
                WHERE next_event = 'conversion'
            )
            SELECT 
                campaign_id,
                touchpoint_position,
                COUNT(*) as conversion_count
            FROM conversions_with_journey
            GROUP BY campaign_id, touchpoint_position
            ORDER BY campaign_id, touchpoint_position
        """).fetchall()
        
        return [
            {
                'campaign_id': str(r[0]),
                'touchpoint_position': r[1],
                'conversion_count': r[2]
            }
            for r in results
        ]

# 사용 예시
def example_usage():
    """사용 예시"""
    # 데이터베이스 초기화
    db_manager = DatabaseManager("postgresql://user:pass@localhost/addb")
    db_manager.create_tables()
    
    # 캠페인 생성
    campaign_id = db_manager.create_campaign_with_structure(
        advertiser_data={
            'name': '테크 스타트업',
            'email': 'contact@techstartup.com',
            'industry': 'technology',
            'monthly_budget': 100000
        },
        campaign_data={
            'name': '여름 프로모션 캠페인',
            'objective': 'conversion',
            'budget_type': 'daily',
            'budget_amount': 1000,
            'bid_strategy': 'target_cpa',
            'target_cpa': 50,
            'start_date': datetime(2024, 6, 1),
            'end_date': datetime(2024, 8, 31)
        },
        ad_groups_data=[
            {
                'name': '키워드 타겟팅 그룹',
                'bid_amount': 2.5,
                'keywords': ['기술', '스타트업', '혁신']
            }
        ]
    )
    
    # 분석 수행
    analytics = AnalyticsQueries(db_manager)
    top_campaigns = analytics.get_top_performing_campaigns()
    
    return {
        'campaign_id': campaign_id,
        'top_campaigns': top_campaigns
    }
```

## 🚀 프로젝트
1. **광고 플랫폼 완전한 데이터 모델**
2. **실시간 성과 분석 시스템**
3. **대용량 이벤트 처리 파이프라인**
4. **고속 분석을 위한 DuckDB 통합**