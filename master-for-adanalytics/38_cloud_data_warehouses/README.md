# 38. Cloud Data Warehouses - 클라우드 데이터 웨어하우스

## 📚 과정 소개
BigQuery, Snowflake, Redshift 등 클라우드 데이터 웨어하우스를 활용한 대규모 광고 데이터 분석을 마스터합니다.

## 🎯 학습 목표
- 페타바이트급 광고 데이터 처리
- 실시간 데이터 파이프라인 구축
- 비용 최적화 전략
- 고급 분석 쿼리 작성

## 📖 주요 내용

### BigQuery 광고 분석
```sql
-- BigQuery ML을 활용한 CTR 예측 모델
CREATE OR REPLACE MODEL `project.dataset.ctr_prediction_model`
OPTIONS(
    model_type='BOOSTED_TREE_CLASSIFIER',
    input_label_cols=['clicked'],
    enable_global_explain=TRUE,
    data_split_method='AUTO_SPLIT'
) AS
SELECT
    -- 사용자 특성
    user_id,
    device_category,
    geo_country,
    EXTRACT(HOUR FROM event_timestamp) as hour_of_day,
    EXTRACT(DAYOFWEEK FROM event_timestamp) as day_of_week,
    
    -- 광고 특성
    ad_id,
    ad_category,
    ad_position,
    
    -- 컨텍스트
    page_category,
    session_duration,
    page_views_count,
    
    -- 타겟 변수
    IF(event_name = 'ad_click', 1, 0) as clicked
FROM
    `project.dataset.events_*`
WHERE
    _TABLE_SUFFIX BETWEEN '20240101' AND '20240630'
    AND event_name IN ('ad_impression', 'ad_click')
;

-- 모델 평가
SELECT
    *
FROM
    ML.EVALUATE(MODEL `project.dataset.ctr_prediction_model`,
        (SELECT * FROM `project.dataset.test_data`)
    );

-- 예측 수행
SELECT
    user_id,
    ad_id,
    predicted_clicked_probs[OFFSET(1)].prob as click_probability
FROM
    ML.PREDICT(MODEL `project.dataset.ctr_prediction_model`,
        (SELECT * FROM `project.dataset.new_impressions`)
    )
WHERE
    predicted_clicked_probs[OFFSET(1)].prob > 0.7;
```

### Snowflake 고급 기능
```sql
-- Snowflake Streams와 Tasks로 실시간 집계
CREATE OR REPLACE STREAM campaign_events_stream 
ON TABLE raw_events;

CREATE OR REPLACE TASK aggregate_campaign_metrics
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = '1 MINUTE'
WHEN
    SYSTEM$STREAM_HAS_DATA('campaign_events_stream')
AS
    MERGE INTO campaign_metrics target
    USING (
        SELECT
            campaign_id,
            COUNT_IF(event_type = 'impression') as impressions,
            COUNT_IF(event_type = 'click') as clicks,
            COUNT_IF(event_type = 'conversion') as conversions,
            SUM(CASE WHEN event_type = 'conversion' 
                THEN revenue ELSE 0 END) as total_revenue
        FROM campaign_events_stream
        GROUP BY campaign_id
    ) source
    ON target.campaign_id = source.campaign_id
    WHEN MATCHED THEN UPDATE SET
        target.impressions = target.impressions + source.impressions,
        target.clicks = target.clicks + source.clicks,
        target.conversions = target.conversions + source.conversions,
        target.total_revenue = target.total_revenue + source.total_revenue,
        target.last_updated = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN INSERT
        (campaign_id, impressions, clicks, conversions, total_revenue)
    VALUES
        (source.campaign_id, source.impressions, source.clicks, 
         source.conversions, source.total_revenue);
```

### 비용 최적화 전략
1. **파티셔닝 & 클러스터링**
2. **쿼리 최적화**
3. **결과 캐싱**
4. **스토리지 최적화**

## 🚀 핵심 프로젝트
1. **실시간 광고 대시보드 (BigQuery + Looker)**
2. **멀티클라우드 데이터 레이크**
3. **비용 모니터링 시스템**
4. **자동화된 데이터 파이프라인**