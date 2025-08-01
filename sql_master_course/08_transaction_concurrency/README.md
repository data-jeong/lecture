# Chapter 08: 트랜잭션과 동시성 제어

## 학습 목표
- ACID 속성의 이해와 실무 적용
- 트랜잭션 격리 수준별 특성 파악
- 잠금(Lock) 메커니즘과 데드락 해결
- MVCC (Multi-Version Concurrency Control) 이해
- 동시성 문제 해결 전략 수립

## 목차

### 1. 트랜잭션 기초
- 트랜잭션의 정의와 필요성
- ACID 속성 (Atomicity, Consistency, Isolation, Durability)
- BEGIN, COMMIT, ROLLBACK
- 트랜잭션 상태와 생명주기

### 2. 격리 수준 (Isolation Level)
- READ UNCOMMITTED
- READ COMMITTED
- REPEATABLE READ
- SERIALIZABLE
- 격리 수준별 발생 가능한 현상

### 3. 동시성 문제
- Dirty Read
- Non-Repeatable Read
- Phantom Read
- Lost Update

### 4. 잠금 메커니즘
- 공유 잠금 (Shared Lock)
- 배타적 잠금 (Exclusive Lock)
- 의도 잠금 (Intent Lock)
- 데드락과 해결 방법

### 5. MVCC 메커니즘
- 다중 버전 동시성 제어 원리
- 스냅샷 격리
- PostgreSQL과 MySQL의 MVCC 구현

### 6. 실무 동시성 제어
- 낙관적 잠금 vs 비관적 잠금
- 애플리케이션 레벨 동시성 제어
- 분산 트랜잭션
- 성능과 일관성의 트레이드오프

## 실습 문제

### 기초 문제 (exercises/01_transaction_basics.sql)
1. 기본 트랜잭션 사용법
2. ROLLBACK과 COMMIT 실습
3. 격리 수준 변경과 테스트
4. 동시성 문제 재현
5. 잠금 현상 관찰

### 중급 문제 (exercises/02_concurrency_control.sql)
1. 데드락 상황 생성과 해결
2. 격리 수준별 동작 차이 분석
3. 낙관적/비관적 잠금 구현
4. 배치 처리 트랜잭션 최적화
5. 동시 업데이트 처리 전략

### 고급 문제 (exercises/03_advanced_concurrency.sql)
1. 복잡한 비즈니스 로직 트랜잭션 설계
2. 분산 트랜잭션 시뮬레이션
3. 성능과 일관성 균형점 찾기
4. 대용량 처리 트랜잭션 설계
5. 실시간 시스템 동시성 제어

## 다음 단계
Chapter 08 완료 후 Chapter 09에서 데이터베이스 설계와 정규화를 학습합니다.