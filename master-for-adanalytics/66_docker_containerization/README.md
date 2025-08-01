# 66. Docker Containerization - 도커 컨테이너화

## 📚 과정 소개
광고 분석 시스템의 컨테이너화를 통해 일관된 개발/배포 환경을 구축합니다. Docker와 Kubernetes를 활용한 마이크로서비스 아키텍처를 학습합니다.

## 🎯 학습 목표
- Docker를 활용한 광고 시스템 컨테이너화
- Kubernetes로 대규모 배포 관리
- CI/CD 파이프라인 구축
- 프로덕션 환경 최적화

## 📖 커리큘럼

### Chapter 01-02: Docker Fundamentals
```dockerfile
# 광고 분석 API 서버 Dockerfile
FROM python:3.10-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY src/ ./src/
COPY config/ ./config/

# 환경 변수
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production

# 헬스체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 실행
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Chapter 03: Docker Compose
```yaml
# docker-compose.yml - 광고 분석 시스템
version: '3.8'

services:
  # API 서버
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/adanalytics
      - REDIS_URL=redis://redis:6379
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
    depends_on:
      - postgres
      - redis
      - kafka
    volumes:
      - ./data:/app/data
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # PostgreSQL 데이터베이스
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: adanalytics
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  # Redis 캐시
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Kafka 메시지 브로커
  kafka:
    image: confluentinc/cp-kafka:latest
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    depends_on:
      - zookeeper

  # Zookeeper
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  # Nginx 리버스 프록시
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - api

  # 모니터링 - Prometheus
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  # 모니터링 - Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### Chapter 04-05: Docker Networking & Volumes
- 커스텀 네트워크 구성
- 볼륨 관리 전략
- 데이터 영속성

### Chapter 06: Docker Registry
- 프라이빗 레지스트리 구축
- 이미지 버전 관리
- 보안 스캐닝

### Chapter 07: Multi-stage Builds
```dockerfile
# 멀티스테이지 빌드 예시
# Stage 1: 빌드 환경
FROM python:3.10 AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: 런타임 환경
FROM python:3.10-slim

# 빌드 단계에서 생성된 wheels 복사
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

WORKDIR /app
COPY . .

# 최종 이미지 크기 최소화
RUN find . -type d -name __pycache__ -exec rm -r {} + \
    && rm -rf /wheels /root/.cache/pip

CMD ["python", "app.py"]
```

### Chapter 08: Container Security
- 보안 스캐닝
- 시크릿 관리
- 런타임 보안

### Chapter 09-10: Docker Swarm & Kubernetes Basics
- Swarm 모드 클러스터
- K8s 기본 개념
- 서비스 배포

### Chapter 11-13: Kubernetes Deployments
```yaml
# ad-analytics-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ad-analytics-api
  labels:
    app: ad-analytics
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ad-analytics
  template:
    metadata:
      labels:
        app: ad-analytics
    spec:
      containers:
      - name: api
        image: ad-analytics:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ad-analytics-service
spec:
  selector:
    app: ad-analytics
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ad-analytics-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ad-analytics-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Chapter 14: Helm Charts
- 차트 작성
- 값 관리
- 배포 자동화

### Chapter 15: CI/CD with Docker
```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_REGISTRY: registry.example.com
  APP_NAME: ad-analytics

test:
  stage: test
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - pytest tests/
  coverage: '/TOTAL.+?(\d+\%)/'

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHA .
    - docker tag $DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHA $DOCKER_REGISTRY/$APP_NAME:latest
    - docker push $DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHA
    - docker push $DOCKER_REGISTRY/$APP_NAME:latest
  only:
    - main

deploy:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/$APP_NAME $APP_NAME=$DOCKER_REGISTRY/$APP_NAME:$CI_COMMIT_SHA
    - kubectl rollout status deployment/$APP_NAME
  only:
    - main
```

### Chapter 16-17: Monitoring & Logging
- 컨테이너 모니터링
- 중앙화된 로깅
- 성능 최적화

### Chapter 18: Microservices with Docker
```python
# 마이크로서비스 아키텍처 예시
# impression-service/app.py
from fastapi import FastAPI
from prometheus_client import Counter, Histogram
import redis
import asyncio

app = FastAPI()

# 메트릭
impression_counter = Counter('ad_impressions_total', 'Total ad impressions')
impression_latency = Histogram('impression_processing_seconds', 'Impression processing latency')

# Redis 연결
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

@app.post("/impression")
@impression_latency.time()
async def record_impression(ad_id: str, user_id: str):
    # 노출 기록
    impression_counter.inc()
    
    # Redis에 저장
    key = f"impression:{ad_id}:{user_id}"
    redis_client.setex(key, 3600, 1)  # 1시간 TTL
    
    # 비동기 처리
    asyncio.create_task(process_impression_async(ad_id, user_id))
    
    return {"status": "recorded"}

async def process_impression_async(ad_id: str, user_id: str):
    # Kafka로 이벤트 발행
    # ML 모델 업데이트
    # 실시간 집계 업데이트
    pass
```

### Chapter 19: Production Deployment
- 프로덕션 체크리스트
- 롤링 업데이트
- 블루-그린 배포

### Chapter 20: Docker Optimization
- 이미지 크기 최적화
- 빌드 캐시 활용
- 리소스 제한

## 🚀 핵심 프로젝트
1. **광고 분석 플랫폼 컨테이너화**
2. **마이크로서비스 기반 RTB 시스템**
3. **K8s 기반 자동 스케일링 시스템**
4. **CI/CD 파이프라인 구축**

## 💡 실전 베스트 프랙티스
```yaml
# docker-compose.override.yml (개발 환경)
version: '3.8'

services:
  api:
    build:
      context: ./api
      dockerfile: Dockerfile.dev
    volumes:
      - ./api:/app  # 코드 변경 시 자동 리로드
    environment:
      - APP_ENV=development
      - DEBUG=true
    command: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

  postgres:
    ports:
      - "5432:5432"  # 개발 시 직접 접근 가능
```

---

다음: [Chapter 01: Docker Fundamentals →](01_docker_fundamentals/README.md)