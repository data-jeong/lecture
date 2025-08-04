# 23. Hadoop Ecosystem - 하둡 생태계

## 📚 과정 소개
광고 빅데이터 처리를 위한 Hadoop 생태계를 마스터합니다. HDFS, MapReduce, Hive, HBase를 활용한 대규모 광고 로그 분석과 실시간 데이터 파이프라인 구축을 학습합니다.

## 🎯 학습 목표
- 대용량 광고 로그 데이터 저장 및 처리
- Hive를 통한 광고 성과 분석
- HBase 실시간 광고 서빙 시스템
- Sqoop을 통한 데이터 파이프라인 구축

## 📖 주요 내용

### Hadoop 기반 광고 데이터 처리
```python
import os
import pandas as pd
import numpy as np
from hdfs import InsecureClient
from pyhive import hive
import happybase
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AdLog:
    """광고 로그 데이터"""
    timestamp: datetime
    user_id: str
    campaign_id: str
    ad_id: str
    event_type: str  # impression, click, conversion
    device_type: str
    os: str
    browser: str
    ip_address: str
    country: str
    city: str
    cost: float
    revenue: float = 0.0

class HDFSAdDataManager:
    """HDFS 광고 데이터 관리자"""
    
    def __init__(self, hdfs_url: str = 'http://localhost:9870'):
        self.client = InsecureClient(hdfs_url)
        self.base_path = '/ad_data'
        self._setup_directories()
        
    def _setup_directories(self):
        """HDFS 디렉토리 구조 설정"""
        directories = [
            f'{self.base_path}/raw_logs',
            f'{self.base_path}/processed',
            f'{self.base_path}/campaigns',
            f'{self.base_path}/users',
            f'{self.base_path}/reports',
            f'{self.base_path}/staging'
        ]
        
        for directory in directories:
            try:
                self.client.makedirs(directory)
                logger.info(f"Created directory: {directory}")
            except Exception as e:
                logger.debug(f"Directory {directory} already exists or error: {e}")
    
    def upload_ad_logs(self, local_file_path: str, 
                      partition_date: str = None) -> str:
        """광고 로그 HDFS 업로드"""
        if partition_date is None:
            partition_date = datetime.now().strftime('%Y/%m/%d')
        
        hdfs_path = f'{self.base_path}/raw_logs/date={partition_date}'
        
        try:
            self.client.makedirs(hdfs_path)
        except:
            pass  # 디렉토리 이미 존재
        
        file_name = os.path.basename(local_file_path)
        hdfs_file_path = f'{hdfs_path}/{file_name}'
        
        with open(local_file_path, 'rb') as local_file:
            self.client.write(hdfs_file_path, local_file)
        
        logger.info(f"Uploaded {local_file_path} to {hdfs_file_path}")
        return hdfs_file_path
    
    def create_partitioned_table_data(self, logs: List[AdLog]):
        """파티션된 테이블 데이터 생성"""
        # 날짜별로 그룹핑
        partitioned_data = {}
        
        for log in logs:
            date_key = log.timestamp.strftime('%Y/%m/%d')
            if date_key not in partitioned_data:
                partitioned_data[date_key] = []
            
            log_dict = {
                'timestamp': log.timestamp.isoformat(),
                'user_id': log.user_id,
                'campaign_id': log.campaign_id,
                'ad_id': log.ad_id,
                'event_type': log.event_type,
                'device_type': log.device_type,
                'os': log.os,
                'browser': log.browser,
                'ip_address': log.ip_address,
                'country': log.country,
                'city': log.city,
                'cost': log.cost,
                'revenue': log.revenue
            }
            partitioned_data[date_key].append(log_dict)
        
        # 각 파티션별로 JSON 파일 저장
        for date_key, logs_data in partitioned_data.items():
            hdfs_path = f'{self.base_path}/processed/date={date_key}'
            try:
                self.client.makedirs(hdfs_path)
            except:
                pass
            
            file_path = f'{hdfs_path}/ad_logs.json'
            json_data = '\n'.join([json.dumps(log) for log in logs_data])
            
            self.client.write(file_path, json_data, encoding='utf-8')
            logger.info(f"Created partitioned data: {file_path}")
    
    def list_partitions(self, table_type: str = 'raw_logs') -> List[str]:
        """파티션 목록 조회"""
        base_path = f'{self.base_path}/{table_type}'
        try:
            partitions = []
            for item in self.client.list(base_path):
                if item.startswith('date='):
                    partitions.append(item)
            return sorted(partitions)
        except Exception as e:
            logger.error(f"Error listing partitions: {e}")
            return []

class HiveAdAnalyzer:
    """Hive 광고 분석기"""
    
    def __init__(self, host: str = 'localhost', port: int = 10000,
                 database: str = 'ad_analytics'):
        self.host = host
        self.port = port
        self.database = database
        self.connection = None
        self._connect()
        self._setup_database()
    
    def _connect(self):
        """Hive 연결"""
        try:
            self.connection = hive.Connection(
                host=self.host,
                port=self.port,
                database=self.database
            )
            logger.info(f"Connected to Hive at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Hive: {e}")
    
    def _setup_database(self):
        """데이터베이스 및 테이블 설정"""
        queries = [
            f"CREATE DATABASE IF NOT EXISTS {self.database}",
            f"USE {self.database}",
            """
            CREATE TABLE IF NOT EXISTS ad_logs_external (
                timestamp STRING,
                user_id STRING,
                campaign_id STRING,
                ad_id STRING,
                event_type STRING,
                device_type STRING,
                os STRING,
                browser STRING,
                ip_address STRING,
                country STRING,
                city STRING,
                cost DOUBLE,
                revenue DOUBLE
            )
            PARTITIONED BY (date STRING)
            STORED AS TEXTFILE
            LOCATION '/ad_data/processed'
            """,
            """
            CREATE TABLE IF NOT EXISTS campaign_performance (
                campaign_id STRING,
                date STRING,
                impressions BIGINT,
                clicks BIGINT,
                conversions BIGINT,
                cost DOUBLE,
                revenue DOUBLE,
                ctr DOUBLE,
                cvr DOUBLE,
                roas DOUBLE
            )
            STORED AS PARQUET
            """,
            """
            CREATE TABLE IF NOT EXISTS user_segments (
                user_id STRING,
                segment STRING,
                last_activity STRING,
                total_conversions BIGINT,
                total_revenue DOUBLE,
                avg_session_duration DOUBLE,
                device_preference STRING
            )
            STORED AS PARQUET
            """
        ]
        
        for query in queries:
            try:
                self.execute_query(query)
            except Exception as e:
                logger.error(f"Error executing setup query: {e}")
    
    def execute_query(self, query: str) -> List[Dict]:
        """쿼리 실행"""
        if not self.connection:
            self._connect()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                columns = [desc[0] for desc in cursor.description]
                results = cursor.fetchall()
                return [dict(zip(columns, row)) for row in results]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return []
    
    def analyze_campaign_performance(self, start_date: str, end_date: str) -> List[Dict]:
        """캠페인 성과 분석"""
        query = f"""
        SELECT 
            campaign_id,
            COUNT(CASE WHEN event_type = 'impression' THEN 1 END) as impressions,
            COUNT(CASE WHEN event_type = 'click' THEN 1 END) as clicks,
            COUNT(CASE WHEN event_type = 'conversion' THEN 1 END) as conversions,
            SUM(cost) as total_cost,
            SUM(revenue) as total_revenue,
            COUNT(CASE WHEN event_type = 'click' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN event_type = 'impression' THEN 1 END), 0) as ctr,
            COUNT(CASE WHEN event_type = 'conversion' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN event_type = 'click' THEN 1 END), 0) as cvr,
            SUM(revenue) / NULLIF(SUM(cost), 0) as roas
        FROM ad_logs_external
        WHERE date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY campaign_id
        ORDER BY total_revenue DESC
        """
        
        return self.execute_query(query)
    
    def analyze_user_behavior(self, date_range: int = 30) -> List[Dict]:
        """사용자 행동 분석"""
        query = f"""
        WITH user_stats AS (
            SELECT 
                user_id,
                COUNT(DISTINCT campaign_id) as campaigns_engaged,
                COUNT(CASE WHEN event_type = 'impression' THEN 1 END) as impressions,
                COUNT(CASE WHEN event_type = 'click' THEN 1 END) as clicks,
                COUNT(CASE WHEN event_type = 'conversion' THEN 1 END) as conversions,
                SUM(revenue) as total_revenue,
                COUNT(DISTINCT device_type) as device_variety,
                MAX(timestamp) as last_activity
            FROM ad_logs_external
            WHERE date >= date_sub(current_date(), {date_range})
            GROUP BY user_id
        )
        SELECT 
            user_id,
            campaigns_engaged,
            impressions,
            clicks,
            conversions,
            total_revenue,
            CASE 
                WHEN conversions >= 5 AND total_revenue >= 500 THEN 'High Value'
                WHEN conversions >= 2 AND total_revenue >= 100 THEN 'Medium Value'
                WHEN clicks >= 10 THEN 'Active Browser'
                WHEN impressions >= 50 THEN 'Aware User'
                ELSE 'Low Engagement'
            END as user_segment,
            last_activity
        FROM user_stats
        ORDER BY total_revenue DESC
        """
        
        return self.execute_query(query)
    
    def create_daily_performance_report(self, target_date: str):
        """일별 성과 리포트 생성"""
        insert_query = f"""
        INSERT OVERWRITE TABLE campaign_performance
        PARTITION (date = '{target_date}')
        SELECT 
            campaign_id,
            COUNT(CASE WHEN event_type = 'impression' THEN 1 END) as impressions,
            COUNT(CASE WHEN event_type = 'click' THEN 1 END) as clicks,
            COUNT(CASE WHEN event_type = 'conversion' THEN 1 END) as conversions,
            SUM(cost) as cost,
            SUM(revenue) as revenue,
            COUNT(CASE WHEN event_type = 'click' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN event_type = 'impression' THEN 1 END), 0) as ctr,
            COUNT(CASE WHEN event_type = 'conversion' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN event_type = 'click' THEN 1 END), 0) as cvr,
            SUM(revenue) / NULLIF(SUM(cost), 0) as roas
        FROM ad_logs_external
        WHERE date = '{target_date}'
        GROUP BY campaign_id
        """
        
        self.execute_query(insert_query)
        logger.info(f"Daily performance report created for {target_date}")

class HBaseAdServingSystem:
    """HBase 광고 서빙 시스템"""
    
    def __init__(self, host: str = 'localhost', port: int = 9090):
        self.connection = happybase.Connection(host=host, port=port)
        self.tables = {
            'user_profiles': 'user_profiles',
            'campaign_configs': 'campaign_configs',
            'real_time_stats': 'real_time_stats',
            'ad_inventory': 'ad_inventory'
        }
        self._setup_tables()
    
    def _setup_tables(self):
        """HBase 테이블 설정"""
        table_schemas = {
            'user_profiles': {
                'demographics': dict(),
                'interests': dict(),
                'behavior': dict(),
                'segments': dict()
            },
            'campaign_configs': {
                'basic': dict(),
                'targeting': dict(), 
                'budget': dict(),
                'performance': dict()
            },
            'real_time_stats': {
                'hourly': dict(),
                'daily': dict(),
                'cumulative': dict()
            },
            'ad_inventory': {
                'creative': dict(),
                'metadata': dict(),
                'performance': dict()
            }
        }
        
        for table_name, column_families in table_schemas.items():
            try:
                if table_name.encode() not in self.connection.tables():
                    self.connection.create_table(table_name, column_families)
                    logger.info(f"Created HBase table: {table_name}")
            except Exception as e:
                logger.error(f"Error creating table {table_name}: {e}")
    
    def store_user_profile(self, user_id: str, profile_data: Dict[str, Any]):
        """사용자 프로필 저장"""
        table = self.connection.table('user_profiles')
        
        row_data = {}
        
        # 인구통계학적 정보
        if 'demographics' in profile_data:
            for key, value in profile_data['demographics'].items():
                row_data[f'demographics:{key}'.encode()] = str(value).encode()
        
        # 관심사
        if 'interests' in profile_data:
            for i, interest in enumerate(profile_data['interests']):
                row_data[f'interests:interest_{i}'.encode()] = interest.encode()
        
        # 행동 패턴
        if 'behavior' in profile_data:
            for key, value in profile_data['behavior'].items():
                row_data[f'behavior:{key}'.encode()] = str(value).encode()
        
        # 세그먼트 정보
        if 'segment' in profile_data:
            row_data[b'segments:current'] = profile_data['segment'].encode()
            row_data[b'segments:updated'] = datetime.now().isoformat().encode()
        
        table.put(user_id.encode(), row_data)
        logger.info(f"Stored user profile for: {user_id}")
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """사용자 프로필 조회"""
        table = self.connection.table('user_profiles')
        
        try:
            row = table.row(user_id.encode())
            if not row:
                return {}
            
            profile = {
                'demographics': {},
                'interests': [],
                'behavior': {},
                'segment': None
            }
            
            for key, value in row.items():
                key_str = key.decode()
                value_str = value.decode()
                
                if key_str.startswith('demographics:'):
                    field = key_str.split(':', 1)[1]
                    profile['demographics'][field] = value_str
                elif key_str.startswith('interests:'):
                    profile['interests'].append(value_str)
                elif key_str.startswith('behavior:'):
                    field = key_str.split(':', 1)[1]
                    profile['behavior'][field] = value_str
                elif key_str == 'segments:current':
                    profile['segment'] = value_str
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
            return {}
    
    def update_real_time_stats(self, campaign_id: str, event_type: str, 
                              value: float = 1.0, hour: int = None):
        """실시간 통계 업데이트"""
        if hour is None:
            hour = datetime.now().hour
        
        table = self.connection.table('real_time_stats')
        row_key = f"{campaign_id}_{datetime.now().strftime('%Y%m%d')}"
        
        # 원자적 증가 연산
        try:
            # 시간별 통계
            hourly_key = f'hourly:{event_type}_{hour:02d}'.encode()
            table.counter_inc(row_key.encode(), hourly_key, int(value))
            
            # 일별 누적 통계
            daily_key = f'daily:{event_type}'.encode()
            table.counter_inc(row_key.encode(), daily_key, int(value))
            
            # 전체 누적 통계
            cumulative_key = f'cumulative:{event_type}'.encode()
            table.counter_inc(row_key.encode(), cumulative_key, int(value))
            
        except Exception as e:
            logger.error(f"Error updating real-time stats: {e}")
    
    def get_campaign_stats(self, campaign_id: str, date: str = None) -> Dict[str, int]:
        """캠페인 통계 조회"""
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        
        table = self.connection.table('real_time_stats')
        row_key = f"{campaign_id}_{date}"
        
        try:
            row = table.row(row_key.encode())
            stats = {}
            
            for key, value in row.items():
                key_str = key.decode()
                stats[key_str] = int.from_bytes(value, byteorder='big', signed=True)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting campaign stats: {e}")
            return {}

class MapReduceAdProcessor:
    """MapReduce 광고 데이터 처리"""
    
    def __init__(self, hadoop_home: str = '/usr/local/hadoop'):
        self.hadoop_home = hadoop_home
        self.streaming_jar = f"{hadoop_home}/share/hadoop/tools/lib/hadoop-streaming-*.jar"
        
    def run_daily_aggregation(self, input_path: str, output_path: str, date: str):
        """일별 집계 MapReduce 작업"""
        
        # Mapper 스크립트 생성
        mapper_script = """#!/usr/bin/env python3
import sys
import json
from datetime import datetime

for line in sys.stdin:
    try:
        log = json.loads(line.strip())
        campaign_id = log.get('campaign_id', 'unknown')
        event_type = log.get('event_type', 'unknown')
        cost = float(log.get('cost', 0))
        revenue = float(log.get('revenue', 0))
        
        # 키: campaign_id, 값: event_type,cost,revenue
        key = campaign_id
        value = f"{event_type},{cost},{revenue}"
        print(f"{key}\\t{value}")
        
    except Exception as e:
        continue
"""
        
        # Reducer 스크립트 생성
        reducer_script = """#!/usr/bin/env python3
import sys
from collections import defaultdict

current_campaign = None
stats = defaultdict(lambda: {'count': 0, 'cost': 0.0, 'revenue': 0.0})

for line in sys.stdin:
    try:
        campaign_id, value = line.strip().split('\\t')
        event_type, cost, revenue = value.split(',')
        cost = float(cost)
        revenue = float(revenue)
        
        if current_campaign != campaign_id:
            if current_campaign:
                # 이전 캠페인 결과 출력
                output_stats(current_campaign, stats)
            
            current_campaign = campaign_id
            stats = defaultdict(lambda: {'count': 0, 'cost': 0.0, 'revenue': 0.0})
        
        stats[event_type]['count'] += 1
        stats[event_type]['cost'] += cost
        stats[event_type]['revenue'] += revenue
        
    except Exception as e:
        continue

# 마지막 캠페인 처리
if current_campaign:
    output_stats(current_campaign, stats)

def output_stats(campaign_id, stats):
    impressions = stats['impression']['count']
    clicks = stats['click']['count'] 
    conversions = stats['conversion']['count']
    total_cost = sum(s['cost'] for s in stats.values())
    total_revenue = sum(s['revenue'] for s in stats.values())
    
    ctr = (clicks / impressions * 100) if impressions > 0 else 0
    cvr = (conversions / clicks * 100) if clicks > 0 else 0
    roas = (total_revenue / total_cost) if total_cost > 0 else 0
    
    result = f"{campaign_id},{impressions},{clicks},{conversions},{total_cost:.2f},{total_revenue:.2f},{ctr:.2f},{cvr:.2f},{roas:.2f}"
    print(result)
"""
        
        # 스크립트 파일 저장
        with open('/tmp/mapper.py', 'w') as f:
            f.write(mapper_script)
        with open('/tmp/reducer.py', 'w') as f:
            f.write(reducer_script)
        
        # 실행 권한 부여
        os.chmod('/tmp/mapper.py', 0o755)
        os.chmod('/tmp/reducer.py', 0o755)
        
        # MapReduce 작업 실행
        cmd = [
            'hadoop', 'jar', self.streaming_jar,
            '-files', '/tmp/mapper.py,/tmp/reducer.py',
            '-mapper', 'mapper.py',
            '-reducer', 'reducer.py',
            '-input', input_path,
            '-output', output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"MapReduce job completed successfully")
                logger.info(f"Output: {result.stdout}")
            else:
                logger.error(f"MapReduce job failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Error running MapReduce job: {e}")

class SqoopDataImporter:
    """Sqoop 데이터 임포트"""
    
    def __init__(self, mysql_host: str = 'localhost', 
                 mysql_user: str = 'root', mysql_password: str = 'password'):
        self.mysql_host = mysql_host
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        
    def import_campaign_data(self, database: str, table: str, 
                           hdfs_target: str = '/ad_data/campaigns'):
        """캠페인 데이터 임포트"""
        cmd = [
            'sqoop', 'import',
            '--connect', f'jdbc:mysql://{self.mysql_host}/{database}',
            '--username', self.mysql_user,
            '--password', self.mysql_password,
            '--table', table,
            '--target-dir', hdfs_target,
            '--split-by', 'campaign_id',
            '--fields-terminated-by', '\\t',
            '--null-string', '\\\\N',
            '--null-non-string', '\\\\N'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Sqoop import completed: {table}")
            else:
                logger.error(f"Sqoop import failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Error running Sqoop import: {e}")
    
    def export_to_mysql(self, hdfs_source: str, database: str, table: str):
        """HDFS에서 MySQL로 데이터 익스포트"""
        cmd = [
            'sqoop', 'export',
            '--connect', f'jdbc:mysql://{self.mysql_host}/{database}',
            '--username', self.mysql_user,
            '--password', self.mysql_password,
            '--table', table,
            '--export-dir', hdfs_source,
            '--fields-terminated-by', '\\t',
            '--update-mode', 'allowinsert',
            '--update-key', 'campaign_id,date'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Sqoop export completed: {table}")
            else:
                logger.error(f"Sqoop export failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Error running Sqoop export: {e}")

# 사용 예시 및 통합 파이프라인
def example_hadoop_ad_pipeline():
    """Hadoop 광고 데이터 파이프라인 예시"""
    print("=== Hadoop 광고 데이터 파이프라인 시작 ===")
    
    # 1. 샘플 광고 로그 데이터 생성
    sample_logs = []
    campaigns = ['camp_001', 'camp_002', 'camp_003']
    events = ['impression', 'click', 'conversion']
    devices = ['mobile', 'desktop', 'tablet']
    countries = ['KR', 'US', 'JP', 'CN']
    
    np.random.seed(42)
    
    for i in range(10000):
        log = AdLog(
            timestamp=datetime.now() - timedelta(days=np.random.randint(0, 30)),
            user_id=f'user_{np.random.randint(1, 1000):05d}',
            campaign_id=np.random.choice(campaigns),
            ad_id=f'ad_{np.random.randint(1, 100):03d}',
            event_type=np.random.choice(events, p=[0.7, 0.25, 0.05]),
            device_type=np.random.choice(devices),
            os=np.random.choice(['iOS', 'Android', 'Windows', 'MacOS']),
            browser=np.random.choice(['Chrome', 'Safari', 'Firefox', 'Edge']),
            ip_address=f'{np.random.randint(1,255)}.{np.random.randint(1,255)}.{np.random.randint(1,255)}.{np.random.randint(1,255)}',
            country=np.random.choice(countries),
            city=np.random.choice(['Seoul', 'New York', 'Tokyo', 'Beijing']),
            cost=np.random.uniform(0.1, 5.0),
            revenue=np.random.uniform(0, 50) if np.random.random() < 0.1 else 0.0
        )
        sample_logs.append(log)
    
    try:
        # 2. HDFS 데이터 관리
        print("\n--- HDFS 데이터 업로드 ---")
        hdfs_manager = HDFSAdDataManager()
        hdfs_manager.create_partitioned_table_data(sample_logs)
        
        partitions = hdfs_manager.list_partitions('processed')
        print(f"생성된 파티션: {len(partitions)}개")
        
    except Exception as e:
        print(f"HDFS 작업 중 오류: {e}")
    
    try:
        # 3. Hive 분석
        print("\n--- Hive 데이터 분석 ---")
        hive_analyzer = HiveAdAnalyzer()
        
        # 최근 7일간 캠페인 성과 분석
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        performance_results = hive_analyzer.analyze_campaign_performance(start_date, end_date)
        print(f"캠페인 성과 분석 결과: {len(performance_results)}개 캠페인")
        
        # 사용자 행동 분석
        user_behavior = hive_analyzer.analyze_user_behavior(30)
        print(f"사용자 행동 분석 결과: {len(user_behavior)}명")
        
    except Exception as e:
        print(f"Hive 분석 중 오류: {e}")
    
    try:
        # 4. HBase 실시간 데이터
        print("\n--- HBase 실시간 데이터 저장 ---")
        hbase_system = HBaseAdServingSystem()
        
        # 샘플 사용자 프로필 저장
        sample_profile = {
            'demographics': {'age': 28, 'gender': 'M', 'income': 'high'},
            'interests': ['technology', 'gaming', 'sports'],
            'behavior': {'session_duration': 300, 'pages_per_session': 5},
            'segment': 'high_value'
        }
        
        hbase_system.store_user_profile('user_00001', sample_profile)
        
        # 실시간 통계 업데이트
        for i in range(100):
            campaign_id = np.random.choice(campaigns)
            event_type = np.random.choice(events, p=[0.7, 0.25, 0.05])
            hbase_system.update_real_time_stats(campaign_id, event_type)
        
        # 통계 조회
        stats = hbase_system.get_campaign_stats('camp_001')
        print(f"실시간 통계 업데이트 완료: {len(stats)}개 지표")
        
    except Exception as e:
        print(f"HBase 작업 중 오류: {e}")
    
    # 5. 결과 요약
    print("\n=== 파이프라인 완료 ===")
    print("✅ HDFS에 파티션된 데이터 저장")
    print("✅ Hive로 배치 분석 수행") 
    print("✅ HBase에 실시간 데이터 저장")
    print("✅ 통합 광고 데이터 파이프라인 구축 완료")
    
    return {
        'logs_processed': len(sample_logs),
        'partitions_created': len(partitions) if 'partitions' in locals() else 0,
        'campaigns_analyzed': len(performance_results) if 'performance_results' in locals() else 0,
        'users_analyzed': len(user_behavior) if 'user_behavior' in locals() else 0
    }

if __name__ == "__main__":
    results = example_hadoop_ad_pipeline()
    print(f"Hadoop 광고 데이터 파이프라인 완료! 처리된 로그: {results['logs_processed']}개")
```

## 🚀 프로젝트
1. **대용량 광고 로그 처리 시스템**
2. **실시간 광고 서빙 플랫폼**
3. **Hive 기반 광고 분석 대시보드**
4. **통합 광고 데이터 파이프라인**