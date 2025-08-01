-- Chapter 09: 데이터베이스 설계 실습 문제

-- 문제 1: 온라인 서점 시스템 설계
-- 요구사항 분석 후 ER 다이어그램을 작성하고 테이블로 구현하세요.
-- 엔티티: 고객, 도서, 주문, 저자, 출판사, 리뷰

-- 문제 2: 정규화 적용
-- 아래 비정규화된 테이블을 3NF까지 정규화하세요.

CREATE TABLE unnormalized_orders (
    order_id INT,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    customer_address TEXT,
    product_name VARCHAR(200),
    product_category VARCHAR(50),
    quantity INT,
    unit_price DECIMAL(10,2),
    order_date DATE
);

-- 문제 3: 다대다 관계 해결
-- 학생-강의 시스템에서 다대다 관계를 해결하는 중간 테이블 설계

-- 문제 4: 계층 구조 설계
-- 조직도나 카테고리 트리 구조를 관계형 DB로 설계

-- 문제 5: 이력 관리 설계
-- 직원의 부서 이동 이력을 관리하는 테이블 설계