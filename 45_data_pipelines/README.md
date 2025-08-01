# 45. Data Pipelines - 데이터 파이프라인

## 📚 과정 소개
Apache Airflow, DBT, Kafka를 활용한 대규모 광고 데이터 파이프라인을 구축합니다. 실시간 스트리밍부터 배치 처리까지 완전 자동화된 데이터 워크플로우를 개발합니다.

## 🎯 학습 목표
- Airflow를 활용한 ETL 파이프라인 구축
- DBT로 데이터 변환 및 모델링
- Kafka를 통한 실시간 데이터 스트리밍
- 데이터 품질 관리 및 모니터링

## 📖 주요 내용

### Apache Airflow 광고 데이터 파이프라인
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.S3_hook import S3Hook
import pandas as pd
import requests
import json

# DAG 기본 설정
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

dag = DAG(
    'ad_data_pipeline',
    default_args=default_args,
    description='광고 데이터 ETL 파이프라인',
    schedule_interval='0 2 * * *',  # 매일 새벽 2시
    max_active_runs=1,
    tags=['advertising', 'etl', 'daily']
)

def extract_google_ads_data(**context):
    """Google Ads 데이터 추출"""
    from google.ads.googleads.client import GoogleAdsClient
    
    # 어제 날짜
    execution_date = context['execution_date']
    yesterday = execution_date - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    
    # Google Ads 클라이언트 초기화
    client = GoogleAdsClient.load_from_storage("google-ads.yaml")
    
    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            segments.date
        FROM campaign
        WHERE segments.date = '{date_str}'
    """
    
    ga_service = client.get_service("GoogleAdsService")
    
    results = []
    search_request = client.get_type("SearchGoogleAdsRequest")
    search_request.customer_id = "1234567890"
    search_request.query = query
    
    response = ga_service.search(request=search_request)
    
    for row in response:
        results.append({
            'date': date_str,
            'platform': 'google_ads',
            'campaign_id': row.campaign.id,
            'campaign_name': row.campaign.name,
            'impressions': row.metrics.impressions,
            'clicks': row.metrics.clicks,
            'cost': row.metrics.cost_micros / 1000000,
            'conversions': row.metrics.conversions
        })
    
    # S3에 원본 데이터 저장
    s3_hook = S3Hook('aws_default')
    df = pd.DataFrame(results)
    
    s3_key = f"raw/google_ads/{date_str}/campaign_data.parquet"
    s3_hook.load_string(
        df.to_parquet(),
        key=s3_key,
        bucket_name='ad-data-lake'
    )
    
    return s3_key

def extract_facebook_ads_data(**context):
    """Facebook Ads 데이터 추출"""
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    
    execution_date = context['execution_date']
    yesterday = execution_date - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    
    # Facebook API 초기화
    FacebookAdsApi.init(access_token='YOUR_ACCESS_TOKEN')
    
    account = AdAccount('act_1234567890')
    campaigns = account.get_campaigns(fields=[
        'id', 'name', 'status'
    ])
    
    results = []
    
    for campaign in campaigns:
        insights = campaign.get_insights(
            fields=['impressions', 'clicks', 'spend', 'actions'],
            params={
                'time_range': {
                    'since': date_str,
                    'until': date_str
                }
            }
        )
        
        for insight in insights:
            conversions = 0
            if insight.get('actions'):
                for action in insight['actions']:
                    if action['action_type'] == 'purchase':
                        conversions = int(action['value'])
                        break
            
            results.append({
                'date': date_str,
                'platform': 'facebook_ads',
                'campaign_id': campaign['id'],
                'campaign_name': campaign['name'],
                'impressions': int(insight.get('impressions', 0)),
                'clicks': int(insight.get('clicks', 0)),
                'cost': float(insight.get('spend', 0)),
                'conversions': conversions
            })
    
    # S3 저장
    s3_hook = S3Hook('aws_default')
    df = pd.DataFrame(results)
    
    s3_key = f"raw/facebook_ads/{date_str}/campaign_data.parquet"
    s3_hook.load_string(
        df.to_parquet(),
        key=s3_key,
        bucket_name='ad-data-lake'
    )
    
    return s3_key

def transform_and_load_data(**context):
    """데이터 변환 및 적재"""
    execution_date = context['execution_date']
    yesterday = execution_date - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    
    s3_hook = S3Hook('aws_default')
    postgres_hook = PostgresHook('postgres_default')
    
    # Google Ads 데이터 로드
    google_key = f"raw/google_ads/{date_str}/campaign_data.parquet"
    google_data = s3_hook.read_key(google_key, 'ad-data-lake')
    google_df = pd.read_parquet(google_data)
    
    # Facebook Ads 데이터 로드
    facebook_key = f"raw/facebook_ads/{date_str}/campaign_data.parquet"
    facebook_data = s3_hook.read_key(facebook_key, 'ad-data-lake')
    facebook_df = pd.read_parquet(facebook_data)
    
    # 데이터 통합
    combined_df = pd.concat([google_df, facebook_df], ignore_index=True)
    
    # 데이터 변환
    combined_df['ctr'] = combined_df['clicks'] / combined_df['impressions'].replace(0, 1)
    combined_df['cpc'] = combined_df['cost'] / combined_df['clicks'].replace(0, 1)
    combined_df['cvr'] = combined_df['conversions'] / combined_df['clicks'].replace(0, 1)
    combined_df['cpa'] = combined_df['cost'] / combined_df['conversions'].replace(0, 1)
    
    # PostgreSQL에 적재
    combined_df.to_sql(
        'daily_campaign_metrics',
        postgres_hook.get_sqlalchemy_engine(),
        if_exists='append',
        index=False
    )
    
    return len(combined_df)

def validate_data_quality(**context):
    """데이터 품질 검증"""
    execution_date = context['execution_date']
    yesterday = execution_date - timedelta(days=1)
    
    postgres_hook = PostgresHook('postgres_default')
    
    # 데이터 존재 여부 확인
    count_query = f"""
        SELECT COUNT(*) 
        FROM daily_campaign_metrics 
        WHERE date = '{yesterday.strftime('%Y-%m-%d')}'
    """
    
    record_count = postgres_hook.get_first(count_query)[0]
    
    if record_count == 0:
        raise ValueError("No data found for yesterday")
    
    # 데이터 품질 검사
    quality_checks = [
        ("CTR 범위 확인", "SELECT COUNT(*) FROM daily_campaign_metrics WHERE ctr < 0 OR ctr > 1"),
        ("비용 음수 확인", "SELECT COUNT(*) FROM daily_campaign_metrics WHERE cost < 0"),
        ("중복 데이터 확인", """
            SELECT COUNT(*) FROM (
                SELECT campaign_id, platform, date, COUNT(*) as cnt
                FROM daily_campaign_metrics 
                WHERE date = %s
                GROUP BY campaign_id, platform, date
                HAVING COUNT(*) > 1
            ) duplicates
        """)
    ]
    
    for check_name, query in quality_checks:
        if "중복" in check_name:
            result = postgres_hook.get_first(query, parameters=[yesterday.strftime('%Y-%m-%d')])[0]
        else:
            result = postgres_hook.get_first(query)[0]
        
        if result > 0:
            raise ValueError(f"Data quality check failed: {check_name}")
    
    print(f"Data quality validation passed. Total records: {record_count}")

# Task 정의
extract_google_task = PythonOperator(
    task_id='extract_google_ads_data',
    python_callable=extract_google_ads_data,
    dag=dag
)

extract_facebook_task = PythonOperator(
    task_id='extract_facebook_ads_data',
    python_callable=extract_facebook_ads_data,
    dag=dag
)

transform_load_task = PythonOperator(
    task_id='transform_and_load_data',
    python_callable=transform_and_load_data,
    dag=dag
)

validate_task = PythonOperator(
    task_id='validate_data_quality',
    python_callable=validate_data_quality,
    dag=dag
)

# DBT 실행
dbt_run_task = BashOperator(
    task_id='run_dbt_models',
    bash_command='cd /opt/dbt && dbt run --profiles-dir .',
    dag=dag
)

# 알림 Task
notify_success_task = BashOperator(
    task_id='notify_success',
    bash_command='echo "Pipeline completed successfully" | mail -s "Ad Data Pipeline Success" data-team@company.com',
    dag=dag
)

# Task 의존성
[extract_google_task, extract_facebook_task] >> transform_load_task >> validate_task >> dbt_run_task >> notify_success_task
```

### DBT 데이터 모델링
```sql
-- models/staging/stg_campaign_metrics.sql
-- 스테이징 레이어: 원본 데이터 정제

{{ config(materialized='view') }}

WITH source_data AS (
    SELECT *
    FROM {{ source('raw', 'daily_campaign_metrics') }}
    WHERE date >= '{{ var("start_date") }}'
)

SELECT
    date,
    platform,
    campaign_id,
    campaign_name,
    impressions,
    clicks,
    cost,
    conversions,
    
    -- 계산된 지표들
    CASE 
        WHEN impressions > 0 THEN clicks::float / impressions 
        ELSE 0 
    END AS ctr,
    
    CASE 
        WHEN clicks > 0 THEN cost / clicks 
        ELSE 0 
    END AS cpc,
    
    CASE 
        WHEN clicks > 0 THEN conversions::float / clicks 
        ELSE 0 
    END AS cvr,
    
    CASE 
        WHEN conversions > 0 THEN cost / conversions 
        ELSE 0 
    END AS cpa,
    
    -- 데이터 품질 플래그
    CASE 
        WHEN impressions = 0 OR clicks > impressions THEN 'anomaly'
        WHEN ctr > 0.5 THEN 'high_ctr'
        ELSE 'normal'
    END AS data_quality_flag,
    
    -- 메타데이터
    CURRENT_TIMESTAMP AS processed_at
    
FROM source_data

-- 데이터 품질 테스트
WHERE impressions >= 0 
  AND clicks >= 0 
  AND cost >= 0 
  AND conversions >= 0
```

```sql
-- models/marts/campaign_performance_summary.sql
-- 마트 레이어: 비즈니스 로직이 적용된 최종 테이블

{{ config(
    materialized='table',
    indexes=[
      {'columns': ['date'], 'type': 'btree'},
      {'columns': ['platform', 'campaign_id'], 'type': 'btree'}
    ]
) }}

WITH daily_metrics AS (
    SELECT * FROM {{ ref('stg_campaign_metrics') }}
),

campaign_totals AS (
    SELECT
        date,
        platform,
        campaign_id,
        campaign_name,
        SUM(impressions) AS total_impressions,
        SUM(clicks) AS total_clicks,
        SUM(cost) AS total_cost,
        SUM(conversions) AS total_conversions
    FROM daily_metrics
    GROUP BY 1, 2, 3, 4
),

performance_metrics AS (
    SELECT
        *,
        -- 성과 지표 계산
        CASE 
            WHEN total_impressions > 0 
            THEN total_clicks::float / total_impressions 
            ELSE 0 
        END AS ctr,
        
        CASE 
            WHEN total_clicks > 0 
            THEN total_cost / total_clicks 
            ELSE 0 
        END AS cpc,
        
        CASE 
            WHEN total_clicks > 0 
            THEN total_conversions::float / total_clicks 
            ELSE 0 
        END AS cvr,
        
        CASE 
            WHEN total_conversions > 0 
            THEN total_cost / total_conversions 
            ELSE 0 
        END AS cpa,
        
        -- 효율성 점수 (0-100)
        LEAST(100, GREATEST(0, 
            (total_conversions::float / NULLIF(total_cost, 0) * 1000) * 10
        )) AS efficiency_score
        
    FROM campaign_totals
),

-- 벤치마크 계산
benchmark AS (
    SELECT
        date,
        platform,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ctr) AS median_ctr,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cpc) AS median_cpc,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cvr) AS median_cvr,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cpa) AS median_cpa
    FROM performance_metrics
    GROUP BY 1, 2
)

SELECT
    pm.*,
    b.median_ctr,
    b.median_cpc,
    b.median_cvr,
    b.median_cpa,
    
    -- 벤치마크 대비 성과
    CASE 
        WHEN pm.ctr > b.median_ctr * 1.2 THEN 'above_benchmark'
        WHEN pm.ctr < b.median_ctr * 0.8 THEN 'below_benchmark'
        ELSE 'at_benchmark'
    END AS ctr_performance,
    
    CASE 
        WHEN pm.cpa < b.median_cpa * 0.8 THEN 'above_benchmark'
        WHEN pm.cpa > b.median_cpa * 1.2 THEN 'below_benchmark'
        ELSE 'at_benchmark'
    END AS cpa_performance
    
FROM performance_metrics pm
LEFT JOIN benchmark b ON pm.date = b.date AND pm.platform = b.platform
```

### Kafka 실시간 스트리밍
```python
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json
import time
from typing import Dict
import asyncio
import aioredis

class AdEventStreamer:
    """광고 이벤트 실시간 스트리밍"""
    
    def __init__(self, bootstrap_servers=['localhost:9092']):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.consumer = None
        
    def initialize_producer(self):
        """프로듀서 초기화"""
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',  # 모든 replica에서 확인
            retries=3,
            batch_size=16384,
            linger_ms=10,  # 배치 대기시간
            compression_type='gzip'
        )
    
    async def stream_ad_events(self, event_generator):
        """광고 이벤트 스트리밍"""
        if not self.producer:
            self.initialize_producer()
        
        async for event in event_generator:
            try:
                # 파티션 키 생성 (campaign_id 기반)
                partition_key = str(event.get('campaign_id', 'default'))
                
                # 이벤트 전송
                future = self.producer.send(
                    'ad-events',
                    key=partition_key,
                    value=event,
                    timestamp_ms=int(time.time() * 1000)
                )
                
                # 비동기 전송 결과 확인
                record_metadata = future.get(timeout=10)
                
                print(f"Event sent to partition {record_metadata.partition}, "
                      f"offset {record_metadata.offset}")
                
            except KafkaError as e:
                print(f"Failed to send event: {e}")
            
            await asyncio.sleep(0.001)  # 1ms 대기
    
    def initialize_consumer(self, topics=['ad-events'], group_id='ad-processor'):
        """컨슈머 초기화"""
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            auto_commit_interval_ms=5000,
            max_poll_records=100
        )
    
    async def process_ad_events(self):
        """광고 이벤트 처리"""
        if not self.consumer:
            self.initialize_consumer()
        
        redis = await aioredis.create_redis_pool('redis://localhost')
        
        try:
            for message in self.consumer:
                event = message.value
                event_type = event.get('event_type')
                
                if event_type == 'impression':
                    await self._process_impression(event, redis)
                elif event_type == 'click':
                    await self._process_click(event, redis)
                elif event_type == 'conversion':
                    await self._process_conversion(event, redis)
                
                # 처리 결과 로깅
                print(f"Processed {event_type} for campaign {event.get('campaign_id')}")
                
        except Exception as e:
            print(f"Error processing events: {e}")
        finally:
            redis.close()
            await redis.wait_closed()
    
    async def _process_impression(self, event: Dict, redis):
        """노출 이벤트 처리"""
        campaign_id = event['campaign_id']
        
        # Redis에 실시간 카운터 업데이트
        await redis.hincrby(f"campaign:{campaign_id}:daily", 'impressions', 1)
        await redis.hincrby(f"campaign:{campaign_id}:hourly", 
                           f"impressions:{time.strftime('%H')}", 1)
        
        # 시간별 트렌드 저장
        timestamp = int(time.time())
        await redis.zadd(f"campaign:{campaign_id}:impression_timeline", 
                        timestamp, timestamp)
    
    async def _process_click(self, event: Dict, redis):
        """클릭 이벤트 처리"""
        campaign_id = event['campaign_id']
        
        await redis.hincrby(f"campaign:{campaign_id}:daily", 'clicks', 1)
        await redis.hincrby(f"campaign:{campaign_id}:hourly", 
                           f"clicks:{time.strftime('%H')}", 1)
        
        # CTR 실시간 계산
        impressions = await redis.hget(f"campaign:{campaign_id}:daily", 'impressions')
        clicks = await redis.hget(f"campaign:{campaign_id}:daily", 'clicks')
        
        if impressions and clicks:
            ctr = int(clicks) / int(impressions)
            await redis.hset(f"campaign:{campaign_id}:daily", 'ctr', ctr)
    
    async def _process_conversion(self, event: Dict, redis):
        """전환 이벤트 처리"""
        campaign_id = event['campaign_id']
        conversion_value = event.get('value', 0)
        
        await redis.hincrby(f"campaign:{campaign_id}:daily", 'conversions', 1)
        await redis.hincrbyfloat(f"campaign:{campaign_id}:daily", 'revenue', conversion_value)
        
        # ROAS 계산
        revenue = await redis.hget(f"campaign:{campaign_id}:daily", 'revenue')
        cost = await redis.hget(f"campaign:{campaign_id}:daily", 'cost')
        
        if revenue and cost and float(cost) > 0:
            roas = float(revenue) / float(cost)
            await redis.hset(f"campaign:{campaign_id}:daily", 'roas', roas)

# 이벤트 생성기 예시
async def generate_ad_events():
    """광고 이벤트 생성 (시뮬레이션)"""
    import random
    
    campaigns = ['camp_001', 'camp_002', 'camp_003']
    
    while True:
        # 이벤트 타입 결정 (노출 80%, 클릭 15%, 전환 5%)
        rand = random.random()
        if rand < 0.8:
            event_type = 'impression'
        elif rand < 0.95:
            event_type = 'click'
        else:
            event_type = 'conversion'
        
        event = {
            'event_type': event_type,
            'campaign_id': random.choice(campaigns),
            'user_id': f"user_{random.randint(1, 10000)}",
            'timestamp': time.time(),
            'device': random.choice(['mobile', 'desktop', 'tablet']),
            'geo': random.choice(['KR', 'US', 'JP'])
        }
        
        if event_type == 'conversion':
            event['value'] = random.uniform(1000, 50000)
        
        yield event
        
        await asyncio.sleep(random.uniform(0.01, 0.1))  # 10-100ms 간격
```

### 데이터 파이프라인 모니터링
```python
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

class PipelineMonitor:
    """데이터 파이프라인 모니터링 대시보드"""
    
    def __init__(self):
        self.setup_dashboard()
    
    def setup_dashboard(self):
        """대시보드 설정"""
        st.set_page_config(
            page_title="Ad Data Pipeline Monitor",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("🚀 광고 데이터 파이프라인 모니터링")
        
        # 사이드바
        st.sidebar.header("설정")
        self.selected_date = st.sidebar.date_input(
            "날짜 선택",
            value=datetime.now().date() - timedelta(days=1)
        )
        
        self.refresh_interval = st.sidebar.selectbox(
            "새로고침 간격",
            [30, 60, 300, 600],
            index=1
        )
    
    def show_pipeline_status(self):
        """파이프라인 상태 표시"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Airflow DAG 실행",
                "성공",
                delta="100%",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "데이터 품질",
                "양호",
                delta="99.5%",
                delta_color="normal"
            )
        
        with col3:
            st.metric(
                "실시간 스트림",
                "정상",
                delta="1.2M events/hr",
                delta_color="normal"
            )
        
        with col4:
            st.metric(
                "DBT 모델",
                "최신",
                delta="15 models",
                delta_color="normal"
            )
    
    def show_data_volume_chart(self):
        """데이터 볼륨 차트"""
        st.subheader("📈 일별 데이터 볼륨")
        
        # 샘플 데이터 생성
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=30),
            end=datetime.now(),
            freq='D'
        )
        
        volume_data = pd.DataFrame({
            'date': dates,
            'google_ads': np.random.randint(100000, 500000, len(dates)),
            'facebook_ads': np.random.randint(80000, 400000, len(dates)),
            'other_platforms': np.random.randint(50000, 200000, len(dates))
        })
        
        fig = px.area(
            volume_data,
            x='date',
            y=['google_ads', 'facebook_ads', 'other_platforms'],
            title="플랫폼별 일별 레코드 수"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def show_pipeline_performance(self):
        """파이프라인 성능 지표"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⏱️ 파이프라인 실행 시간")
            
            # 실행 시간 트렌드
            execution_times = pd.DataFrame({
                'date': pd.date_range(start=datetime.now() - timedelta(days=7), 
                                    end=datetime.now(), freq='D'),
                'extraction': np.random.normal(15, 3, 8),
                'transformation': np.random.normal(25, 5, 8),
                'loading': np.random.normal(10, 2, 8)
            })
            
            fig = px.line(
                execution_times,
                x='date',
                y=['extraction', 'transformation', 'loading'],
                title="단계별 실행 시간 (분)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎯 데이터 품질 점수")
            
            quality_scores = {
                'Completeness': 98.5,
                'Accuracy': 97.2,
                'Consistency': 99.1,
                'Timeliness': 96.8
            }
            
            fig = go.Figure(data=go.Scatterpolar(
                r=list(quality_scores.values()),
                theta=list(quality_scores.keys()),
                fill='toself'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def show_error_monitoring(self):
        """에러 모니터링"""
        st.subheader("🚨 에러 및 알림")
        
        # 최근 에러 로그
        error_logs = pd.DataFrame({
            'timestamp': [
                datetime.now() - timedelta(hours=2),
                datetime.now() - timedelta(hours=5),
                datetime.now() - timedelta(hours=8)
            ],
            'component': ['Facebook API', 'DBT Transform', 'Kafka Consumer'],
            'severity': ['WARNING', 'ERROR', 'INFO'],
            'message': [
                'API rate limit approaching',
                'Model test failed: duplicate records detected',
                'Consumer lag detected on partition 2'
            ]
        })
        
        st.dataframe(error_logs, use_container_width=True)
    
    def run(self):
        """대시보드 실행"""
        self.show_pipeline_status()
        st.divider()
        
        self.show_data_volume_chart()
        st.divider()
        
        self.show_pipeline_performance()
        st.divider()
        
        self.show_error_monitoring()
        
        # 자동 새로고침
        time.sleep(self.refresh_interval)
        st.experimental_rerun()

if __name__ == "__main__":
    monitor = PipelineMonitor()
    monitor.run()
```

## 🚀 프로젝트
1. **완전 자동화 광고 데이터 파이프라인**
2. **실시간 스트리밍 분석 시스템**
3. **데이터 품질 모니터링 플랫폼**
4. **크로스 플랫폼 데이터 통합 허브**