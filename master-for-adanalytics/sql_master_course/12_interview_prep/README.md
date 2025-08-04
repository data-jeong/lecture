# Chapter 12: 데이터 분석가 인터뷰 대비

## 학습 목표
- 데이터 분석가 인터뷰의 SQL 문제 유형 파악
- 실무에서 자주 사용되는 분석 패턴 마스터
- 복잡한 비즈니스 문제를 SQL로 해결하는 능력 배양
- 인터뷰 상황에서의 문제 해결 접근법 학습
- 코딩 테스트와 실무 면접 완벽 대비

## 목차

### 1. 인터뷰 준비 전략
- 데이터 분석가 채용 프로세스 이해
- SQL 코딩 테스트 준비 방법
- 실무 면접에서의 SQL 질문 유형
- 문제 해결 접근법과 시간 관리

### 2. 핵심 분석 패턴
- 코호트 분석 (Cohort Analysis)
- 퍼널 분석 (Funnel Analysis)
- 리텐션 분석 (Retention Analysis)
- RFM 고객 세그멘테이션
- A/B 테스트 데이터 분석

### 3. 고급 분석 기법
- 시계열 분석
- 이상치 탐지
- 상관관계 분석
- 예측 모델링을 위한 데이터 준비
- 통계적 가설 검정

### 4. 실무 케이스 스터디
- 전자상거래 데이터 분석
- 구독 서비스 지표 분석
- 마케팅 캠페인 효과 측정
- 사용자 행동 분석
- 매출 성장 동인 분석

### 5. 인터뷰 실전 문제
- 기업별 기출 문제 유형
- 시간 제한 하에서의 문제 해결
- 코드 리뷰와 최적화
- 결과 해석과 비즈니스 인사이트 도출

## 핵심 분석 패턴 예제

### 1. 코호트 분석
```sql
-- 월별 신규 고객 코호트의 리텐션율 계산
WITH cohorts AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', MIN(order_date)) as cohort_month
    FROM orders
    GROUP BY customer_id
),
cohort_data AS (
    SELECT 
        c.cohort_month,
        DATE_TRUNC('month', o.order_date) as order_month,
        COUNT(DISTINCT o.customer_id) as customers
    FROM cohorts c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.cohort_month, DATE_TRUNC('month', o.order_date)
)
SELECT 
    cohort_month,
    order_month,
    customers,
    ROUND(customers * 100.0 / FIRST_VALUE(customers) 
          OVER (PARTITION BY cohort_month ORDER BY order_month), 2) as retention_rate
FROM cohort_data
ORDER BY cohort_month, order_month;
```

### 2. 퍼널 분석
```sql
-- 웹사이트 구매 퍼널 분석
WITH funnel_steps AS (
    SELECT 
        'Page View' as step, 1 as step_order, COUNT(*) as users
    FROM page_views
    WHERE page_type = 'product'
    
    UNION ALL
    
    SELECT 
        'Add to Cart' as step, 2 as step_order, COUNT(DISTINCT user_id) as users
    FROM cart_events
    WHERE event_type = 'add'
    
    UNION ALL
    
    SELECT 
        'Checkout' as step, 3 as step_order, COUNT(DISTINCT customer_id) as users
    FROM orders
)
SELECT 
    step,
    users,
    LAG(users) OVER (ORDER BY step_order) as prev_step_users,
    ROUND(users * 100.0 / LAG(users) OVER (ORDER BY step_order), 2) as conversion_rate
FROM funnel_steps
ORDER BY step_order;
```

### 3. RFM 분석
```sql
-- RFM 고객 세그멘테이션
WITH customer_rfm AS (
    SELECT 
        customer_id,
        MAX(order_date) as last_order_date,
        COUNT(*) as frequency,
        SUM(total_amount) as monetary,
        CURRENT_DATE - MAX(order_date) as recency_days
    FROM orders
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days) as r_score,
        NTILE(5) OVER (ORDER BY frequency DESC) as f_score,
        NTILE(5) OVER (ORDER BY monetary DESC) as m_score
    FROM customer_rfm
)
SELECT 
    customer_id,
    r_score || f_score || m_score as rfm_score,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        ELSE 'Others'
    END as customer_segment
FROM rfm_scores;
```

## 실전 인터뷰 문제

### Level 1: 기초 분석 (exercises/01_basic_analysis.sql)
1. 월별 매출 증감률 계산
2. 상위 10% 고객 식별
3. 제품별 재구매율 계산
4. 계절성 트렌드 분석
5. 고객 획득 비용 계산

### Level 2: 중급 분석 (exercises/02_intermediate_analysis.sql)
1. 완전한 코호트 분석 구현
2. 복잡한 퍼널 분석
3. 고객 생애 가치 예측
4. 마케팅 채널 어트리뷰션
5. 재고 최적화 분석

### Level 3: 고급 분석 (exercises/03_advanced_analysis.sql)
1. 다차원 고객 세그멘테이션
2. 예측 모델링을 위한 피처 엔지니어링
3. 이상치 탐지 알고리즘
4. 네트워크 분석 (추천 시스템)
5. 실시간 대시보드 쿼리

### Level 4: 실무 케이스 (exercises/04_case_studies.sql)
1. Netflix 시청 패턴 분석
2. Uber 수요 예측 모델링
3. Amazon 추천 시스템 데이터 준비
4. Facebook 사용자 참여도 분석
5. Airbnb 가격 최적화 분석

## 인터뷰 팁과 전략

### 문제 해결 접근법
1. **문제 이해**: 요구사항을 정확히 파악
2. **데이터 탐색**: 테이블 구조와 데이터 특성 분석
3. **단계별 해결**: 복잡한 문제를 작은 단위로 분해
4. **검증**: 결과의 타당성 확인
5. **최적화**: 성능과 가독성 개선

### 코딩 테스트 전략
- 시간 관리: 쉬운 문제부터 해결
- 코드 품질: 주석과 가독성 고려
- 예외 처리: 엣지 케이스 고려
- 테스트: 샘플 데이터로 검증

### 실무 면접 대비
- 비즈니스 맥락 이해
- 결과 해석과 인사이트 도출
- 데이터 품질 이슈 고려
- 확장성과 유지보수성 고려

## 기업별 기출 문제 모음

### Tech 기업 (exercises/05_tech_companies.sql)
- Google: 사용자 행동 분석
- Facebook: 소셜 네트워크 분석
- Amazon: 추천 시스템 데이터
- Netflix: 콘텐츠 성과 분석
- Uber: 운영 최적화 분석

### 금융 기업 (exercises/06_finance_companies.sql)
- 신용 리스크 분석
- 거래 패턴 분석
- 사기 탐지 모델링
- 포트폴리오 성과 분석
- 고객 이탈 예측

### 컨설팅 기업 (exercises/07_consulting_firms.sql)
- McKinsey: 비즈니스 성과 분석
- BCG: 시장 분석 모델링
- Bain: 운영 효율성 분석
- Deloitte: 재무 분석
- PwC: 리스크 분석

## 최종 모의면접

### 종합 평가 문제 (exercises/08_final_assessment.sql)
1. 90분 제한 종합 문제
2. 실무 시나리오 기반 분석
3. 코드 리뷰와 최적화
4. 프레젠테이션 준비
5. 질의응답 대비

## 성공 사례와 커리어 가이드

### 인터뷰 성공 사례
- 합격자 인터뷰와 팁
- 실패 사례에서 배우는 교훈
- 기업별 채용 프로세스 분석

### 커리어 발전 방향
- 데이터 분석가에서 데이터 사이언티스트로
- 비즈니스 분석가 vs 기술 분석가
- 관리자 트랙 vs 전문가 트랙
- 프리랜서와 컨설턴트 기회

이 章을 완료하면 데이터 분석가 인터뷰에 완벽하게 준비된 상태가 됩니다!