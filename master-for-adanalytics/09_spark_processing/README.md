# 09. Spark Processing - 스파크 처리

## 📚 과정 소개
Apache Spark를 활용한 대규모 광고 데이터 분산 처리를 마스터합니다. 실시간 스트리밍 분석부터 머신러닝 파이프라인까지 광고 플랫폼의 빅데이터 처리를 학습합니다.

## 🎯 학습 목표
- 대규모 광고 로그 분산 처리
- 실시간 스트리밍 데이터 분석
- Spark ML을 활용한 광고 최적화
- 고성능 ETL 파이프라인 구축

## 📖 주요 내용

### Spark 기본 광고 데이터 처리
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from typing import Dict, List
import logging

class SparkAdProcessor:
    """Spark 광고 데이터 처리기"""
    
    def __init__(self, app_name: str = "AdPlatformSpark"):
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        
    def load_ad_logs(self, path: str, format: str = "parquet") -> DataFrame:
        """광고 로그 데이터 로드"""
        if format == "json":
            return self.spark.read.json(path)
        elif format == "csv":
            return self.spark.read.option("header", "true").csv(path)
        else:
            return self.spark.read.parquet(path)
    
    def create_sample_ad_data(self, num_records: int = 1000000) -> DataFrame:
        """샘플 광고 데이터 생성"""
        # 스키마 정의
        schema = StructType([
            StructField("user_id", StringType(), True),
            StructField("campaign_id", StringType(), True),
            StructField("ad_id", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("event_type", StringType(), True),  # impression, click, conversion
            StructField("device_type", StringType(), True),
            StructField("os", StringType(), True),
            StructField("browser", StringType(), True),
            StructField("country", StringType(), True),
            StructField("city", StringType(), True),
            StructField("age_group", StringType(), True),
            StructField("gender", StringType(), True),
            StructField("bid_price", DoubleType(), True),
            StructField("cost", DoubleType(), True),
            StructField("revenue", DoubleType(), True)
        ])
        
        # 샘플 데이터 생성을 위한 SQL
        sample_data_sql = f"""
        SELECT 
            concat('user_', cast(rand() * 100000 as int)) as user_id,
            concat('campaign_', cast(rand() * 1000 as int)) as campaign_id,
            concat('ad_', cast(rand() * 10000 as int)) as ad_id,
            current_timestamp() - interval cast(rand() * 30 as int) day - 
                interval cast(rand() * 24 as int) hour as timestamp,
            case when rand() < 0.7 then 'impression'
                 when rand() < 0.95 then 'click'
                 else 'conversion' end as event_type,
            case when rand() < 0.6 then 'mobile'
                 when rand() < 0.85 then 'desktop'
                 else 'tablet' end as device_type,
            case when rand() < 0.5 then 'iOS'
                 when rand() < 0.8 then 'Android'
                 else 'Windows' end as os,
            case when rand() < 0.4 then 'Chrome'
                 when rand() < 0.7 then 'Safari'
                 else 'Firefox' end as browser,
            case when rand() < 0.3 then 'KR'
                 when rand() < 0.5 then 'US'
                 when rand() < 0.7 then 'JP'
                 else 'CN' end as country,
            case when rand() < 0.2 then 'Seoul'
                 when rand() < 0.3 then 'New York'
                 when rand() < 0.4 then 'Tokyo'
                 else 'Beijing' end as city,
            case when rand() < 0.25 then '18-24'
                 when rand() < 0.5 then '25-34'
                 when rand() < 0.75 then '35-44'
                 else '45+' end as age_group,
            case when rand() < 0.5 then 'M' else 'F' end as gender,
            round(rand() * 5, 2) as bid_price,
            round(rand() * 2, 3) as cost,
            case when rand() < 0.1 then round(rand() * 100, 2) else 0.0 end as revenue
        FROM range({num_records})
        """
        
        return self.spark.sql(sample_data_sql)
    
    def calculate_campaign_performance(self, df: DataFrame) -> DataFrame:
        """캠페인 성과 계산"""
        # 이벤트별 집계
        performance = df.groupBy("campaign_id", "event_type") \
            .agg(
                count("*").alias("event_count"),
                sum("cost").alias("total_cost"),
                sum("revenue").alias("total_revenue"),
                avg("bid_price").alias("avg_bid_price")
            )
        
        # 피벗하여 가로로 정렬
        performance_pivot = performance.groupBy("campaign_id") \
            .pivot("event_type", ["impression", "click", "conversion"]) \
            .agg(
                first("event_count").alias("count"),
                first("total_cost").alias("cost"),
                first("total_revenue").alias("revenue")
            )
        
        # 성과 지표 계산
        performance_metrics = performance_pivot.select(
            col("campaign_id"),
            coalesce(col("impression_count"), lit(0)).alias("impressions"),
            coalesce(col("click_count"), lit(0)).alias("clicks"),
            coalesce(col("conversion_count"), lit(0)).alias("conversions"),
            coalesce(col("impression_cost"), lit(0.0)).alias("impression_cost"),
            coalesce(col("click_cost"), lit(0.0)).alias("click_cost"),
            coalesce(col("conversion_cost"), lit(0.0)).alias("conversion_cost"),
            coalesce(col("conversion_revenue"), lit(0.0)).alias("total_revenue")
        ).withColumn("total_cost", 
            col("impression_cost") + col("click_cost") + col("conversion_cost")
        ).withColumn("ctr", 
            when(col("impressions") > 0, col("clicks") / col("impressions")).otherwise(0)
        ).withColumn("cvr",
            when(col("clicks") > 0, col("conversions") / col("clicks")).otherwise(0)
        ).withColumn("cpc",
            when(col("clicks") > 0, col("total_cost") / col("clicks")).otherwise(0)
        ).withColumn("cpa",
            when(col("conversions") > 0, col("total_cost") / col("conversions")).otherwise(0)
        ).withColumn("roas",
            when(col("total_cost") > 0, col("total_revenue") / col("total_cost")).otherwise(0)
        )
        
        return performance_metrics
    
    def user_behavior_analysis(self, df: DataFrame) -> DataFrame:
        """사용자 행동 분석"""
        # 사용자별 세션 분석
        window_spec = Window.partitionBy("user_id").orderBy("timestamp")
        
        user_sessions = df.withColumn(
            "session_id",
            concat(
                col("user_id"), 
                lit("_"),
                date_format(col("timestamp"), "yyyyMMdd"),
                lit("_"),
                when(
                    lag("timestamp").over(window_spec).isNull() |
                    (col("timestamp").cast("long") - lag("timestamp").over(window_spec).cast("long") > 1800),
                    monotonically_increasing_id()
                ).otherwise(lag("session_id").over(window_spec))
            )
        )
        
        # 사용자별 행동 패턴 분석
        user_behavior = user_sessions.groupBy("user_id") \
            .agg(
                countDistinct("session_id").alias("session_count"),
                count("*").alias("total_events"),
                sum(when(col("event_type") == "impression", 1).otherwise(0)).alias("impressions"),
                sum(when(col("event_type") == "click", 1).otherwise(0)).alias("clicks"),
                sum(when(col("event_type") == "conversion", 1).otherwise(0)).alias("conversions"),
                countDistinct("campaign_id").alias("campaigns_engaged"),
                countDistinct("ad_id").alias("ads_seen"),
                sum("cost").alias("total_cost_generated"),
                sum("revenue").alias("total_revenue_generated"),
                first("device_type").alias("primary_device"),
                first("country").alias("country"),
                first("age_group").alias("age_group"),
                first("gender").alias("gender")
            )
        
        # 사용자 세그먼트 분류
        user_segments = user_behavior.withColumn(
            "user_segment",
            when((col("conversions") > 5) & (col("total_revenue_generated") > 100), "High Value")
            .when((col("conversions") > 0) & (col("clicks") > 10), "Active Converter")
            .when(col("clicks") > 20, "Active Clicker")
            .when(col("impressions") > 50, "Viewer")
            .otherwise("Low Engagement")
        )
        
        return user_segments
    
    def real_time_attribution_analysis(self, df: DataFrame) -> DataFrame:
        """실시간 어트리뷰션 분석"""
        # 전환 경로 분석을 위한 윈도우 함수
        conversion_window = Window.partitionBy("user_id") \
            .orderBy("timestamp") \
            .rangeBetween(-3600, 0)  # 1시간 이내 터치포인트
        
        # 전환 이벤트에 대한 어트리뷰션
        conversions = df.filter(col("event_type") == "conversion")
        
        # 전환 전 터치포인트 수집
        attribution_data = df.alias("events") \
            .join(conversions.alias("conv"), ["user_id"]) \
            .filter(
                (col("events.timestamp") <= col("conv.timestamp")) &
                (col("events.timestamp") >= col("conv.timestamp") - expr("interval 24 hours"))
            ) \
            .select(
                col("conv.user_id"),
                col("conv.timestamp").alias("conversion_time"),
                col("conv.campaign_id").alias("conversion_campaign"),
                col("conv.revenue").alias("conversion_revenue"),
                col("events.campaign_id").alias("touchpoint_campaign"),
                col("events.ad_id").alias("touchpoint_ad"),
                col("events.event_type").alias("touchpoint_type"),
                col("events.timestamp").alias("touchpoint_time"),
                ((col("conv.timestamp").cast("long") - col("events.timestamp").cast("long")) / 3600).alias("hours_before_conversion")
            )
        
        # First Touch Attribution
        first_touch = attribution_data \
            .withColumn("rn", row_number().over(Window.partitionBy("user_id", "conversion_time").orderBy("touchpoint_time"))) \
            .filter(col("rn") == 1) \
            .groupBy("touchpoint_campaign") \
            .agg(
                count("*").alias("first_touch_conversions"),
                sum("conversion_revenue").alias("first_touch_revenue")
            )
        
        # Last Touch Attribution
        last_touch = attribution_data \
            .withColumn("rn", row_number().over(Window.partitionBy("user_id", "conversion_time").orderBy(desc("touchpoint_time")))) \
            .filter(col("rn") == 1) \
            .groupBy("touchpoint_campaign") \
            .agg(
                count("*").alias("last_touch_conversions"),
                sum("conversion_revenue").alias("last_touch_revenue")
            )
        
        # Linear Attribution (균등 분배)
        linear_attribution = attribution_data \
            .withColumn("touchpoint_count", count("*").over(Window.partitionBy("user_id", "conversion_time"))) \
            .withColumn("linear_conversion_credit", lit(1.0) / col("touchpoint_count")) \
            .withColumn("linear_revenue_credit", col("conversion_revenue") / col("touchpoint_count")) \
            .groupBy("touchpoint_campaign") \
            .agg(
                sum("linear_conversion_credit").alias("linear_conversions"),
                sum("linear_revenue_credit").alias("linear_revenue")
            )
        
        # 결과 병합
        attribution_results = first_touch \
            .join(last_touch, "touchpoint_campaign", "full_outer") \
            .join(linear_attribution, "touchpoint_campaign", "full_outer") \
            .fillna(0)
        
        return attribution_results

class SparkStreamingProcessor:
    """Spark 스트리밍 처리기"""
    
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("AdStreamingProcessor") \
            .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
            .getOrCreate()
    
    def process_real_time_bids(self, kafka_servers: str, topic: str):
        """실시간 입찰 데이터 처리"""
        # Kafka에서 스트리밍 데이터 읽기
        bid_stream = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafka_servers) \
            .option("subscribe", topic) \
            .option("startingOffsets", "latest") \
            .load()
        
        # JSON 파싱
        bid_schema = StructType([
            StructField("bid_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("campaign_id", StringType(), True),
            StructField("bid_price", DoubleType(), True),
            StructField("device_type", StringType(), True),
            StructField("timestamp", TimestampType(), True)
        ])
        
        parsed_bids = bid_stream.select(
            from_json(col("value").cast("string"), bid_schema).alias("data")
        ).select("data.*")
        
        # 실시간 집계
        bid_aggregates = parsed_bids \
            .withWatermark("timestamp", "10 minutes") \
            .groupBy(
                window(col("timestamp"), "1 minute"),
                col("campaign_id")
            ) \
            .agg(
                count("*").alias("bid_count"),
                avg("bid_price").alias("avg_bid_price"),
                max("bid_price").alias("max_bid_price"),
                min("bid_price").alias("min_bid_price")
            )
        
        # 스트리밍 쿼리 시작
        query = bid_aggregates.writeStream \
            .outputMode("append") \
            .format("console") \
            .trigger(processingTime='10 seconds') \
            .start()
        
        return query
    
    def detect_ad_fraud(self, stream_df: DataFrame) -> DataFrame:
        """실시간 광고 사기 탐지"""
        # 윈도우 기반 사기 패턴 탐지
        fraud_detection = stream_df \
            .withWatermark("timestamp", "5 minutes") \
            .groupBy(
                window(col("timestamp"), "1 minute"),
                col("user_id"),
                col("campaign_id")
            ) \
            .agg(
                count("*").alias("event_count"),
                countDistinct("ad_id").alias("unique_ads"),
                avg("bid_price").alias("avg_bid_price")
            ) \
            .withColumn(
                "fraud_score",
                when(col("event_count") > 100, 0.9)  # 1분에 100번 이상 이벤트
                .when(col("unique_ads") < 2, 0.7)     # 다양성 부족
                .when(col("avg_bid_price") > 10, 0.6) # 비정상적 고가 입찰
                .otherwise(0.1)
            ) \
            .filter(col("fraud_score") > 0.5)
        
        return fraud_detection

class SparkMLAdOptimizer:
    """Spark ML을 활용한 광고 최적화"""
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
    
    def build_ctr_prediction_model(self, df: DataFrame):
        """CTR 예측 모델 구축"""
        from pyspark.ml.feature import StringIndexer, OneHotEncoder
        from pyspark.ml.regression import LinearRegression
        from pyspark.ml import Pipeline
        
        # 범주형 변수 인덱싱
        categorical_cols = ["device_type", "os", "browser", "country", "age_group", "gender"]
        indexers = [StringIndexer(inputCol=col, outputCol=f"{col}_index") for col in categorical_cols]
        
        # 원핫 인코딩
        encoders = [OneHotEncoder(inputCol=f"{col}_index", outputCol=f"{col}_encoded") 
                   for col in categorical_cols]
        
        # 특성 벡터 생성
        feature_cols = [f"{col}_encoded" for col in categorical_cols] + ["bid_price"]
        assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
        
        # 정규화
        scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
        
        # 선형 회귀 모델
        lr = LinearRegression(featuresCol="scaled_features", labelCol="ctr")
        
        # 파이프라인 구성
        pipeline = Pipeline(stages=indexers + encoders + [assembler, scaler, lr])
        
        # CTR 계산 (클릭 이벤트 비율)
        training_data = df.withColumn("ctr", 
            when(col("event_type") == "click", 1.0).otherwise(0.0))
        
        # 모델 훈련
        model = pipeline.fit(training_data)
        
        return model
    
    def audience_segmentation_kmeans(self, df: DataFrame, k: int = 5):
        """K-means를 활용한 오디언스 세분화"""
        # 사용자별 특성 집계
        user_features = df.groupBy("user_id") \
            .agg(
                count("*").alias("total_events"),
                sum(when(col("event_type") == "impression", 1).otherwise(0)).alias("impressions"),
                sum(when(col("event_type") == "click", 1).otherwise(0)).alias("clicks"),
                sum(when(col("event_type") == "conversion", 1).otherwise(0)).alias("conversions"),
                avg("bid_price").alias("avg_bid_price"),
                sum("cost").alias("total_cost"),
                sum("revenue").alias("total_revenue"),
                countDistinct("campaign_id").alias("campaigns_engaged")
            ) \
            .fillna(0)
        
        # 특성 벡터 생성
        feature_cols = ["total_events", "impressions", "clicks", "conversions", 
                       "avg_bid_price", "total_cost", "total_revenue", "campaigns_engaged"]
        assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
        
        # 정규화
        scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
        
        # K-means 클러스터링
        kmeans = KMeans(k=k, seed=42, featuresCol="scaled_features")
        
        # 파이프라인 실행
        pipeline = Pipeline(stages=[assembler, scaler, kmeans])
        model = pipeline.fit(user_features)
        
        # 클러스터 할당
        clustered_users = model.transform(user_features)
        
        # 클러스터별 특성 분석
        cluster_analysis = clustered_users.groupBy("prediction") \
            .agg(
                count("*").alias("cluster_size"),
                avg("total_events").alias("avg_total_events"),
                avg("impressions").alias("avg_impressions"),
                avg("clicks").alias("avg_clicks"),
                avg("conversions").alias("avg_conversions"),
                avg("total_revenue").alias("avg_revenue")
            )
        
        return model, clustered_users, cluster_analysis
    
    def recommend_ads_als(self, df: DataFrame):
        """ALS를 활용한 광고 추천"""
        # 사용자-광고 상호작용 매트릭스 생성
        user_ad_interactions = df.filter(col("event_type").isin(["click", "conversion"])) \
            .groupBy("user_id", "ad_id") \
            .agg(
                count("*").alias("interaction_count"),
                sum(when(col("event_type") == "conversion", 2).otherwise(1)).alias("rating")
            )
        
        # 사용자와 광고 ID를 숫자로 변환
        user_indexer = StringIndexer(inputCol="user_id", outputCol="user_index")
        ad_indexer = StringIndexer(inputCol="ad_id", outputCol="ad_index")
        
        indexed_data = user_indexer.fit(user_ad_interactions).transform(user_ad_interactions)
        indexed_data = ad_indexer.fit(indexed_data).transform(indexed_data)
        
        # ALS 모델
        als = ALS(
            maxIter=10,
            regParam=0.1,
            userCol="user_index",
            itemCol="ad_index", 
            ratingCol="rating",
            coldStartStrategy="drop"
        )
        
        # 훈련/테스트 분할
        train, test = indexed_data.randomSplit([0.8, 0.2], seed=42)
        
        # 모델 훈련
        model = als.fit(train)
        
        # 예측 및 평가
        predictions = model.transform(test)
        evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction")
        rmse = evaluator.evaluate(predictions)
        
        # 사용자별 상위 N개 광고 추천
        user_recommendations = model.recommendForAllUsers(10)
        
        return model, rmse, user_recommendations

# 사용 예시
def example_spark_ad_processing():
    """Spark 광고 처리 예시"""
    # Spark 처리기 초기화
    processor = SparkAdProcessor()
    
    # 샘플 데이터 생성
    print("샘플 광고 데이터 생성 중...")
    ad_data = processor.create_sample_ad_data(1000000)
    
    # 데이터 캐싱
    ad_data.cache()
    print(f"총 {ad_data.count():,} 개의 광고 이벤트 생성됨")
    
    # 캠페인 성과 분석
    print("캠페인 성과 분석 중...")
    campaign_performance = processor.calculate_campaign_performance(ad_data)
    campaign_performance.show(20)
    
    # 사용자 행동 분석
    print("사용자 행동 분석 중...")
    user_behavior = processor.user_behavior_analysis(ad_data)
    user_behavior.groupBy("user_segment").count().show()
    
    # 어트리뷰션 분석
    print("어트리뷰션 분석 중...")
    attribution = processor.real_time_attribution_analysis(ad_data)
    attribution.show()
    
    # ML 최적화
    print("ML 모델 구축 중...")
    ml_optimizer = SparkMLAdOptimizer(processor.spark)
    
    # CTR 예측 모델
    ctr_model = ml_optimizer.build_ctr_prediction_model(ad_data)
    
    # 오디언스 세분화
    kmeans_model, clustered_users, cluster_analysis = ml_optimizer.audience_segmentation_kmeans(ad_data)
    print("클러스터 분석 결과:")
    cluster_analysis.show()
    
    # 결과 저장
    campaign_performance.write.mode("overwrite").parquet("campaign_performance.parquet")
    user_behavior.write.mode("overwrite").parquet("user_behavior.parquet")
    
    # 스파크 세션 종료
    processor.spark.stop()
    
    return {
        "campaign_performance": campaign_performance.count(),
        "user_segments": user_behavior.groupBy("user_segment").count().collect(),
        "attribution_campaigns": attribution.count()
    }

if __name__ == "__main__":
    results = example_spark_ad_processing()
    print("Spark 광고 처리 완료!")
```

## 🚀 프로젝트
1. **대규모 광고 로그 분석 시스템**
2. **실시간 입찰 스트리밍 처리**
3. **ML 기반 광고 최적화 엔진**
4. **분산 ETL 파이프라인**