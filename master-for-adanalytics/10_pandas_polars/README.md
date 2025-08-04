# 10. Pandas & Polars - 판다스와 폴라스

## 📚 과정 소개
대규모 광고 데이터 처리를 위한 Pandas와 고성능 Polars 라이브러리를 마스터합니다. 메모리 효율적인 데이터 분석부터 병렬 처리까지 실무 기법을 학습합니다.

## 🎯 학습 목표
- 대용량 광고 데이터 처리 최적화
- Pandas vs Polars 성능 비교
- 메모리 효율적인 데이터 분석
- 실시간 스트리밍 데이터 처리

## 📖 주요 내용

### Pandas 고급 활용
```python
import pandas as pd
import numpy as np
import polars as pl
import time
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

class AdDataProcessor:
    """광고 데이터 처리 클래스"""
    
    def __init__(self):
        self.campaign_data = None
        self.performance_data = None
        
    def load_large_dataset(self, file_path: str, chunk_size: int = 10000) -> pd.DataFrame:
        """대용량 데이터셋 청크 단위 로딩"""
        chunks = []
        
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            # 청크별 전처리
            processed_chunk = self.preprocess_chunk(chunk)
            chunks.append(processed_chunk)
            
        return pd.concat(chunks, ignore_index=True)
    
    def preprocess_chunk(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터 청크 전처리"""
        # 데이터 타입 최적화
        df = self.optimize_dtypes(df)
        
        # 결측값 처리
        df = self.handle_missing_values(df)
        
        # 파생 변수 생성
        df = self.create_derived_features(df)
        
        return df
    
    def optimize_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터 타입 최적화로 메모리 사용량 감소"""
        # 정수형 최적화
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
        
        # 실수형 최적화  
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        # 카테고리형 변환
        categorical_cols = ['campaign_type', 'device_type', 'platform', 'country']
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].astype('category')
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """결측값 처리"""
        # 수치형 변수: 0으로 채우기
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        # 범주형 변수: 'unknown'으로 채우기
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        df[categorical_cols] = df[categorical_cols].fillna('unknown')
        
        return df
    
    def create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """파생 변수 생성"""
        if all(col in df.columns for col in ['clicks', 'impressions', 'cost', 'conversions']):
            # 성과 지표 계산
            df['ctr'] = df['clicks'] / df['impressions'].replace(0, np.nan)
            df['cpc'] = df['cost'] / df['clicks'].replace(0, np.nan)
            df['cvr'] = df['conversions'] / df['clicks'].replace(0, np.nan)
            df['cpa'] = df['cost'] / df['conversions'].replace(0, np.nan)
            
            # 효율성 점수
            df['efficiency_score'] = (df['conversions'] / (df['cost'] + 1)) * 100
        
        return df
    
    def advanced_groupby_operations(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """고급 그룹별 연산"""
        results = {}
        
        # 캠페인별 일별 성과 트렌드
        daily_performance = (df.groupby(['campaign_id', 'date'])
                           .agg({
                               'impressions': 'sum',
                               'clicks': 'sum', 
                               'cost': 'sum',
                               'conversions': 'sum'
                           })
                           .reset_index())
        
        # 롤링 평균 계산
        daily_performance['impressions_7d_avg'] = (daily_performance
                                                 .groupby('campaign_id')['impressions']
                                                 .rolling(window=7, min_periods=1)
                                                 .mean()
                                                 .reset_index(drop=True))
        
        results['daily_performance'] = daily_performance
        
        # 디바이스별 성과 비교
        device_performance = (df.groupby('device_type')
                            .agg({
                                'impressions': 'sum',
                                'clicks': 'sum',
                                'cost': 'sum',
                                'conversions': 'sum',
                                'ctr': 'mean',
                                'cvr': 'mean'
                            })
                            .round(4))
        
        results['device_performance'] = device_performance
        
        # 상위 성과 캠페인
        top_campaigns = (df.groupby('campaign_id')
                        .agg({
                            'cost': 'sum',
                            'conversions': 'sum',
                            'cpa': 'mean'
                        })
                        .assign(roas=lambda x: x['conversions'] * 100 / x['cost'])
                        .sort_values('roas', ascending=False)
                        .head(10))
        
        results['top_campaigns'] = top_campaigns
        
        return results
    
    def cohort_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """코호트 분석"""
        # 첫 구매 월을 기준으로 코호트 생성
        df['order_period'] = pd.to_datetime(df['date']).dt.to_period('M')
        df['cohort_group'] = df.groupby('customer_id')['order_period'].transform('min')
        
        # 기간 번호 계산
        def get_period_number(df):
            return (df['order_period'] - df['cohort_group']).apply(attrgetter('n'))
        
        df['period_number'] = get_period_number(df)
        
        # 코호트 테이블 생성
        cohort_data = df.groupby(['cohort_group', 'period_number'])['customer_id'].nunique().reset_index()
        cohort_counts = cohort_data.pivot(index='cohort_group', 
                                         columns='period_number', 
                                         values='customer_id')
        
        # 코호트 크기
        cohort_sizes = df.groupby('cohort_group')['customer_id'].nunique()
        
        # 유지율 계산
        cohort_table = cohort_counts.divide(cohort_sizes, axis=0)
        
        return cohort_table

class PolarsProcessor:
    """Polars를 활용한 고성능 데이터 처리"""
    
    def __init__(self):
        self.df = None
        
    def load_and_process(self, file_path: str) -> pl.DataFrame:
        """Polars로 대용량 데이터 로딩 및 처리"""
        # LazyFrame으로 로딩 (지연 평가)
        lazy_df = (pl.scan_csv(file_path)
                  .with_columns([
                      # 데이터 타입 변환
                      pl.col("date").str.strptime(pl.Date, format="%Y-%m-%d"),
                      pl.col("impressions").cast(pl.Int32),
                      pl.col("clicks").cast(pl.Int32),
                      pl.col("cost").cast(pl.Float32),
                      pl.col("conversions").cast(pl.Int16)
                  ])
                  .with_columns([
                      # 파생 변수 생성
                      (pl.col("clicks") / pl.col("impressions")).alias("ctr"),
                      (pl.col("cost") / pl.col("clicks")).alias("cpc"),
                      (pl.col("conversions") / pl.col("clicks")).alias("cvr"),
                      (pl.col("cost") / pl.col("conversions")).alias("cpa")
                  ])
                  .filter(
                      # 필터링
                      (pl.col("impressions") > 0) &
                      (pl.col("cost") > 0)
                  ))
        
        # 실행 및 결과 반환
        self.df = lazy_df.collect()
        return self.df
    
    def advanced_aggregations(self) -> Dict[str, pl.DataFrame]:
        """고급 집계 연산"""
        results = {}
        
        # 캠페인별 성과 요약
        campaign_summary = (self.df
                           .group_by("campaign_id")
                           .agg([
                               pl.col("impressions").sum().alias("total_impressions"),
                               pl.col("clicks").sum().alias("total_clicks"),
                               pl.col("cost").sum().alias("total_cost"),
                               pl.col("conversions").sum().alias("total_conversions"),
                               pl.col("ctr").mean().alias("avg_ctr"),
                               pl.col("cpa").mean().alias("avg_cpa")
                           ])
                           .with_columns([
                               (pl.col("total_conversions") * 100 / pl.col("total_cost")).alias("roas")
                           ])
                           .sort("roas", descending=True))
        
        results['campaign_summary'] = campaign_summary
        
        # 시간별 트렌드 분석
        time_trends = (self.df
                      .with_columns([
                          pl.col("date").dt.year().alias("year"),
                          pl.col("date").dt.month().alias("month"),
                          pl.col("date").dt.weekday().alias("weekday")
                      ])
                      .group_by(["year", "month", "weekday"])
                      .agg([
                          pl.col("impressions").sum(),
                          pl.col("clicks").sum(),
                          pl.col("cost").sum(),
                          pl.col("ctr").mean()
                      ]))
        
        results['time_trends'] = time_trends
        
        # 디바이스별 성과 분석
        device_analysis = (self.df
                          .group_by("device_type")
                          .agg([
                              pl.col("impressions").sum(),
                              pl.col("clicks").sum(),
                              pl.col("cost").sum(),
                              pl.col("conversions").sum(),
                              pl.col("ctr").mean(),
                              pl.col("cvr").mean()
                          ])
                          .with_columns([
                              (pl.col("clicks") / pl.col("impressions")).alias("overall_ctr"),
                              (pl.col("conversions") / pl.col("clicks")).alias("overall_cvr")
                          ]))
        
        results['device_analysis'] = device_analysis
        
        return results
    
    def window_functions(self) -> pl.DataFrame:
        """윈도우 함수 활용"""
        result = (self.df
                 .sort(["campaign_id", "date"])
                 .with_columns([
                     # 캠페인별 누적 비용
                     pl.col("cost").cumsum().over("campaign_id").alias("cumulative_cost"),
                     
                     # 7일 이동 평균
                     pl.col("impressions").rolling_mean(window_size=7).over("campaign_id").alias("impressions_7d_avg"),
                     
                     # 전일 대비 변화율
                     (pl.col("clicks") / pl.col("clicks").shift(1).over("campaign_id") - 1).alias("clicks_change_rate"),
                     
                     # 캠페인별 순위
                     pl.col("conversions").rank(method="dense", descending=True).over("campaign_id").alias("conversion_rank")
                 ]))
        
        return result
    
    def performance_benchmark(self, pandas_df: pd.DataFrame) -> Dict[str, float]:
        """Pandas vs Polars 성능 비교"""
        results = {}
        
        # Pandas 성능 측정
        start_time = time.time()
        pandas_result = (pandas_df.groupby('campaign_id')
                        .agg({
                            'impressions': 'sum',
                            'clicks': 'sum',
                            'cost': 'sum'
                        }))
        pandas_time = time.time() - start_time
        results['pandas_time'] = pandas_time
        
        # Polars 성능 측정
        start_time = time.time()
        polars_result = (self.df
                        .group_by("campaign_id")
                        .agg([
                            pl.col("impressions").sum(),
                            pl.col("clicks").sum(),
                            pl.col("cost").sum()
                        ]))
        polars_time = time.time() - start_time
        results['polars_time'] = polars_time
        
        results['speedup'] = pandas_time / polars_time
        
        return results

class StreamingDataProcessor:
    """실시간 스트리밍 데이터 처리"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.buffer = []
        self.metrics = {
            'total_impressions': 0,
            'total_clicks': 0,
            'total_cost': 0.0,
            'running_ctr': 0.0
        }
    
    def process_stream_batch(self, batch_data: List[Dict]) -> Dict:
        """스트림 배치 처리"""
        # 배치를 Polars DataFrame으로 변환
        batch_df = pl.DataFrame(batch_data)
        
        # 실시간 지표 계산
        batch_metrics = (batch_df
                        .select([
                            pl.col("impressions").sum().alias("impressions"),
                            pl.col("clicks").sum().alias("clicks"), 
                            pl.col("cost").sum().alias("cost")
                        ])
                        .to_dicts()[0])
        
        # 누적 지표 업데이트
        self.metrics['total_impressions'] += batch_metrics['impressions']
        self.metrics['total_clicks'] += batch_metrics['clicks']
        self.metrics['total_cost'] += batch_metrics['cost']
        
        # 실시간 CTR 계산
        if self.metrics['total_impressions'] > 0:
            self.metrics['running_ctr'] = self.metrics['total_clicks'] / self.metrics['total_impressions']
        
        # 이상 감지
        anomalies = self.detect_anomalies(batch_df)
        
        return {
            'batch_size': len(batch_data),
            'batch_metrics': batch_metrics,
            'running_metrics': self.metrics.copy(),
            'anomalies': anomalies
        }
    
    def detect_anomalies(self, df: pl.DataFrame) -> List[Dict]:
        """이상 징후 감지"""
        anomalies = []
        
        # CTR 이상 감지
        avg_ctr = df.select(pl.col("clicks") / pl.col("impressions")).mean().item()
        if avg_ctr > 0.1:  # 10% 이상의 CTR
            anomalies.append({
                'type': 'high_ctr',
                'value': avg_ctr,
                'threshold': 0.1
            })
        
        # 비정상적으로 높은 비용
        high_cost_records = df.filter(pl.col("cost") > 10000).height
        if high_cost_records > 0:
            anomalies.append({
                'type': 'high_cost',
                'count': high_cost_records,
                'threshold': 10000
            })
        
        return anomalies
    
    def sliding_window_analysis(self, new_data: Dict) -> Dict:
        """슬라이딩 윈도우 분석"""
        # 버퍼에 새 데이터 추가
        self.buffer.append(new_data)
        
        # 윈도우 크기 유지
        if len(self.buffer) > self.window_size:
            self.buffer.pop(0)
        
        # 윈도우 데이터 분석
        if len(self.buffer) >= 10:  # 최소 10개 데이터
            window_df = pl.DataFrame(self.buffer)
            
            # 트렌드 분석
            trend_analysis = (window_df
                             .with_row_count("index")
                             .select([
                                 pl.corr("index", "impressions").alias("impression_trend"),
                                 pl.corr("index", "clicks").alias("click_trend"),
                                 pl.corr("index", "cost").alias("cost_trend")
                             ])
                             .to_dicts()[0])
            
            return {
                'window_size': len(self.buffer),
                'trends': trend_analysis,
                'latest_ctr': new_data.get('clicks', 0) / max(new_data.get('impressions', 1), 1)
            }
        
        return {'window_size': len(self.buffer), 'status': 'insufficient_data'}

# 사용 예시
def performance_comparison_demo():
    """성능 비교 데모"""
    # 샘플 데이터 생성
    np.random.seed(42)
    n_records = 100000
    
    data = {
        'campaign_id': np.random.choice(['camp_1', 'camp_2', 'camp_3'], n_records),
        'date': pd.date_range('2024-01-01', periods=n_records, freq='1min'),
        'impressions': np.random.randint(100, 1000, n_records),
        'clicks': np.random.randint(5, 100, n_records),
        'cost': np.random.uniform(10, 500, n_records),
        'conversions': np.random.randint(0, 10, n_records),
        'device_type': np.random.choice(['mobile', 'desktop', 'tablet'], n_records)
    }
    
    # Pandas DataFrame
    pandas_df = pd.DataFrame(data)
    
    # Polars 처리
    polars_processor = PolarsProcessor()
    
    # CSV로 저장 후 Polars로 로딩 (실제 시나리오)
    pandas_df.to_csv('sample_data.csv', index=False)
    polars_df = polars_processor.load_and_process('sample_data.csv')
    
    # 성능 비교
    benchmark_results = polars_processor.performance_benchmark(pandas_df)
    
    print(f"성능 비교 결과:")
    print(f"Pandas 처리 시간: {benchmark_results['pandas_time']:.4f}초")
    print(f"Polars 처리 시간: {benchmark_results['polars_time']:.4f}초")
    print(f"Polars 성능 향상: {benchmark_results['speedup']:.2f}배")
    
    return benchmark_results

if __name__ == "__main__":
    results = performance_comparison_demo()
```

## 🚀 프로젝트
1. **대용량 광고 데이터 처리 파이프라인**
2. **실시간 성과 모니터링 시스템**
3. **메모리 최적화 분석 도구**
4. **고성능 코호트 분석 플랫폼**