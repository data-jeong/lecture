# 42. CI/CD Automation - CI/CD 자동화

## 📚 과정 소개
광고 플랫폼을 위한 완전 자동화된 CI/CD 파이프라인을 구축합니다. GitHub Actions, GitLab CI, Jenkins를 활용한 배포 자동화와 품질 관리를 마스터합니다.

## 🎯 학습 목표
- 광고 시스템 CI/CD 파이프라인 설계
- 자동화된 테스트 및 품질 관리
- 무중단 배포 전략
- 모니터링 및 롤백 시스템

## 📖 주요 내용

### GitHub Actions 워크플로우
```yaml
# .github/workflows/ad-platform-ci.yml
name: Ad Platform CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'
  DOCKER_REGISTRY: ghcr.io
  IMAGE_NAME: ad-platform

jobs:
  # 코드 품질 검사
  quality-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        
    - name: Run linting
      run: |
        flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
        
    - name: Run type checking
      run: mypy src/
      
    - name: Run security scan
      run: |
        bandit -r src/ -f json -o bandit-report.json
        safety check --json --output safety-report.json
        
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          bandit-report.json
          safety-report.json

  # 단위 테스트
  unit-tests:
    runs-on: ubuntu-latest
    needs: quality-check
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: ad_platform_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
          
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
        
    - name: Run unit tests
      env:
        DATABASE_URL: postgresql://postgres:testpass@localhost:5432/ad_platform_test
        REDIS_URL: redis://localhost:6379/0
        ENVIRONMENT: test
      run: |
        pytest tests/unit/ -v --cov=src/ --cov-report=xml --cov-report=html
        
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        
    - name: Archive test results
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: |
          htmlcov/
          coverage.xml

  # 통합 테스트
  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: ad_platform_test
        ports:
          - 5432:5432
          
      redis:
        image: redis:6
        ports:
          - 6379:6379
          
    steps:
    - uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        
    - name: Build and start services
      run: |
        docker-compose -f docker-compose.test.yml up -d
        sleep 30  # 서비스 시작 대기
        
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v --tb=short
        
    - name: Run API tests
      run: |
        pytest tests/api/ -v --tb=short
        
    - name: Cleanup
      run: |
        docker-compose -f docker-compose.test.yml down

  # 성능 테스트
  performance-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
      
    - name: Set up Node.js for Artillery
      uses: actions/setup-node@v3
      with:
        node-version: ${{ env.NODE_VERSION }}
        
    - name: Install Artillery
      run: npm install -g artillery@latest
      
    - name: Build test environment
      run: |
        docker-compose -f docker-compose.test.yml up -d
        sleep 60  # 충분한 시작 시간
        
    - name: Run load tests
      run: |
        artillery run tests/performance/campaign-api-load-test.yml
        artillery run tests/performance/bidding-load-test.yml
        
    - name: Generate performance report
      run: |
        artillery report --output performance-report.html artillery_report_*.json
        
    - name: Upload performance reports
      uses: actions/upload-artifact@v3
      with:
        name: performance-reports
        path: performance-report.html

  # 도커 이미지 빌드
  build-image:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      image-digest: ${{ steps.build.outputs.digest }}
      
    steps:
    - uses: actions/checkout@v4
      
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.DOCKER_REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.DOCKER_REGISTRY }}/${{ github.repository }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
          
    - name: Build and push Docker image
      id: build
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        
    - name: Run vulnerability scan
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ steps.meta.outputs.tags }}
        format: 'sarif'
        output: 'trivy-results.sarif'
        
    - name: Upload vulnerability scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  # 스테이징 배포
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build-image
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging-api.adplatform.com
      
    steps:
    - uses: actions/checkout@v4
      
    - name: Set up Kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.28.0'
        
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ap-northeast-2
        
    - name: Update kubeconfig
      run: |
        aws eks update-kubeconfig --region ap-northeast-2 --name staging-cluster
        
    - name: Deploy to staging
      run: |
        helm upgrade --install ad-platform-staging ./helm/ad-platform \
          --namespace staging \
          --set image.tag=${{ github.sha }} \
          --set environment=staging \
          --set replicas=2 \
          --wait --timeout=300s
          
    - name: Run smoke tests
      run: |
        kubectl wait --for=condition=ready pod -l app=ad-platform -n staging --timeout=300s
        pytest tests/smoke/ --base-url=https://staging-api.adplatform.com
        
    - name: Notify deployment
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        channel: '#deployments'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}

  # 프로덕션 배포
  deploy-production:
    runs-on: ubuntu-latest
    needs: [build-image, performance-tests]
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://api.adplatform.com
      
    steps:
    - uses: actions/checkout@v4
      
    - name: Set up Kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.28.0'
        
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ap-northeast-2
        
    - name: Update kubeconfig
      run: |
        aws eks update-kubeconfig --region ap-northeast-2 --name production-cluster
        
    - name: Blue-Green Deployment
      run: |
        # 현재 버전 백업
        kubectl get deployment ad-platform -n production -o yaml > current-deployment.yaml
        
        # 새 버전 배포 (Green)
        helm upgrade ad-platform-green ./helm/ad-platform \
          --namespace production \
          --set image.tag=${{ github.sha }} \
          --set environment=production \
          --set service.name=ad-platform-green \
          --set replicas=5 \
          --wait --timeout=600s
          
    - name: Health check
      run: |
        # Green 환경 헬스체크
        kubectl wait --for=condition=ready pod -l app=ad-platform-green -n production --timeout=300s
        
        # API 헬스체크
        for i in {1..30}; do
          if curl -f http://ad-platform-green-service:8080/health; then
            echo "Health check passed"
            break
          fi
          sleep 10
        done
        
    - name: Switch traffic
      run: |
        # 트래픽을 Green으로 전환
        kubectl patch service ad-platform -n production -p '{"spec":{"selector":{"version":"green"}}}'
        
        # 구 버전 정리 (5분 후)
        sleep 300
        helm uninstall ad-platform-blue -n production || true
        
    - name: Post-deployment verification
      run: |
        pytest tests/smoke/ --base-url=https://api.adplatform.com
        
    - name: Notify production deployment
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        channel: '#production'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
        text: |
          🚀 Production deployment completed!
          Image: ${{ needs.build-image.outputs.image-tag }}
          Commit: ${{ github.sha }}
```

### GitLab CI 파이프라인
```yaml
# .gitlab-ci.yml
variables:
  DOCKER_REGISTRY: registry.gitlab.com
  PYTHON_VERSION: "3.11"
  POSTGRES_VERSION: "13"
  REDIS_VERSION: "6"

stages:
  - quality
  - test
  - build
  - deploy-staging
  - deploy-production

# 품질 검사
code-quality:
  stage: quality
  image: python:${PYTHON_VERSION}
  before_script:
    - pip install -r requirements-dev.txt
  script:
    - flake8 src/ --format=junit-xml --output-file=flake8-report.xml
    - pylint src/ --output-format=junit > pylint-report.xml
    - mypy src/ --junit-xml mypy-report.xml
  artifacts:
    reports:
      junit:
        - flake8-report.xml
        - pylint-report.xml
        - mypy-report.xml
    expire_in: 1 week
    
security-scan:
  stage: quality
  image: python:${PYTHON_VERSION}
  script:
    - pip install bandit safety
    - bandit -r src/ -f json -o bandit-report.json
    - safety check --json --output safety-report.json
  artifacts:
    paths:
      - bandit-report.json
      - safety-report.json
    expire_in: 1 week

# 테스트
unit-tests:
  stage: test
  image: python:${PYTHON_VERSION}
  services:
    - name: postgres:${POSTGRES_VERSION}
      alias: postgres
      variables:
        POSTGRES_DB: ad_platform_test
        POSTGRES_USER: test
        POSTGRES_PASSWORD: testpass
    - name: redis:${REDIS_VERSION}
      alias: redis
  variables:
    DATABASE_URL: postgresql://test:testpass@postgres:5432/ad_platform_test
    REDIS_URL: redis://redis:6379/0
  before_script:
    - pip install -r requirements.txt
    - pip install -r requirements-test.txt
  script:
    - pytest tests/unit/ --cov=src/ --cov-report=xml --cov-report=html --junitxml=unit-test-report.xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      junit: unit-test-report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - htmlcov/
    expire_in: 1 week

integration-tests:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker-compose -f docker-compose.test.yml up -d
    - sleep 30
  script:
    - docker-compose -f docker-compose.test.yml exec -T app pytest tests/integration/ --junitxml=integration-test-report.xml
  after_script:
    - docker-compose -f docker-compose.test.yml down
  artifacts:
    reports:
      junit: integration-test-report.xml
    expire_in: 1 week

# 도커 이미지 빌드
build-image:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker build -t $CI_REGISTRY_IMAGE:latest .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:latest
  only:
    - main
    - develop

# 스테이징 배포
deploy-staging:
  stage: deploy-staging
  image: 
    name: alpine/helm:latest
    entrypoint: [""]
  before_script:
    - apk add --no-cache curl
    - curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
    - chmod +x kubectl && mv kubectl /usr/local/bin/
  script:
    - echo $KUBE_CONFIG | base64 -d > kubeconfig
    - export KUBECONFIG=kubeconfig
    - helm upgrade --install ad-platform-staging ./helm/ad-platform 
        --namespace staging 
        --set image.tag=$CI_COMMIT_SHA 
        --set environment=staging
        --wait
  environment:
    name: staging
    url: https://staging-api.adplatform.com
  only:
    - develop

# 프로덕션 배포
deploy-production:
  stage: deploy-production
  image: 
    name: alpine/helm:latest
    entrypoint: [""]
  before_script:
    - apk add --no-cache curl
    - curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
    - chmod +x kubectl && mv kubectl /usr/local/bin/
  script:
    - echo $KUBE_CONFIG | base64 -d > kubeconfig
    - export KUBECONFIG=kubeconfig
    - helm upgrade --install ad-platform ./helm/ad-platform 
        --namespace production 
        --set image.tag=$CI_COMMIT_SHA 
        --set environment=production
        --set replicas=5
        --wait
  environment:
    name: production
    url: https://api.adplatform.com
  when: manual
  only:
    - main
```

### Jenkins 파이프라인
```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'your-registry.com'
        IMAGE_NAME = 'ad-platform'
        PYTHON_VERSION = '3.11'
        SLACK_CHANNEL = '#ci-cd'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                }
            }
        }
        
        stage('Quality Checks') {
            parallel {
                stage('Linting') {
                    steps {
                        sh '''
                            python -m venv venv
                            . venv/bin/activate
                            pip install -r requirements-dev.txt
                            flake8 src/ --format=junit-xml --output-file=flake8-report.xml
                        '''
                    }
                    post {
                        always {
                            publishTestResults testResultsPattern: 'flake8-report.xml'
                        }
                    }
                }
                
                stage('Type Checking') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            mypy src/ --junit-xml mypy-report.xml
                        '''
                    }
                    post {
                        always {
                            publishTestResults testResultsPattern: 'mypy-report.xml'
                        }
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            bandit -r src/ -f json -o bandit-report.json
                            safety check --json --output safety-report.json
                        '''
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
                        }
                    }
                }
            }
        }
        
        stage('Tests') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh '''
                            . venv/bin/activate
                            pip install -r requirements-test.txt
                            pytest tests/unit/ --cov=src/ --cov-report=xml --junitxml=unit-test-report.xml
                        '''
                    }
                    post {
                        always {
                            publishTestResults testResultsPattern: 'unit-test-report.xml'
                            publishCoverage adapters: [
                                coberturaAdapter('coverage.xml')
                            ], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                        }
                    }
                }
                
                stage('Integration Tests') {
                    steps {
                        sh '''
                            docker-compose -f docker-compose.test.yml up -d
                            sleep 30
                            docker-compose -f docker-compose.test.yml exec -T app pytest tests/integration/ --junitxml=integration-test-report.xml
                        '''
                    }
                    post {
                        always {
                            sh 'docker-compose -f docker-compose.test.yml down'
                            publishTestResults testResultsPattern: 'integration-test-report.xml'
                        }
                    }
                }
            }
        }
        
        stage('Build Image') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    def image = docker.build("${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.GIT_COMMIT_SHORT}")
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-registry-credentials') {
                        image.push()
                        image.push('latest')
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                script {
                    def deployScript = """
                        helm upgrade --install ad-platform-staging ./helm/ad-platform \\
                            --namespace staging \\
                            --set image.tag=${env.GIT_COMMIT_SHORT} \\
                            --set environment=staging \\
                            --wait
                    """
                    
                    withKubeConfig([credentialsId: 'staging-kubeconfig']) {
                        sh deployScript
                    }
                }
            }
            post {
                success {
                    slackSend(
                        channel: env.SLACK_CHANNEL,
                        color: 'good',
                        message: "✅ Staging deployment successful: ${env.BUILD_URL}"
                    )
                }
                failure {
                    slackSend(
                        channel: env.SLACK_CHANNEL,
                        color: 'danger',
                        message: "❌ Staging deployment failed: ${env.BUILD_URL}"
                    )
                }
            }
        }
        
        stage('Performance Tests') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    npm install -g artillery@latest
                    docker-compose -f docker-compose.test.yml up -d
                    sleep 60
                    artillery run tests/performance/load-test.yml
                '''
            }
            post {
                always {
                    sh 'docker-compose -f docker-compose.test.yml down'
                    archiveArtifacts artifacts: 'artillery_report_*.json', allowEmptyArchive: true
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // 수동 승인 단계
                    def userInput = input(
                        id: 'Proceed',
                        message: 'Deploy to production?',
                        parameters: [
                            choice(choices: ['Deploy', 'Abort'], description: 'Proceed with deployment?', name: 'action')
                        ]
                    )
                    
                    if (userInput == 'Deploy') {
                        def deployScript = """
                            # Blue-Green 배포
                            helm upgrade ad-platform ./helm/ad-platform \\
                                --namespace production \\
                                --set image.tag=${env.GIT_COMMIT_SHORT} \\
                                --set environment=production \\
                                --set replicas=5 \\
                                --wait --timeout=600s
                        """
                        
                        withKubeConfig([credentialsId: 'production-kubeconfig']) {
                            sh deployScript
                        }
                        
                        // 헬스체크
                        sh '''
                            kubectl wait --for=condition=ready pod -l app=ad-platform -n production --timeout=300s
                            curl -f https://api.adplatform.com/health || exit 1
                        '''
                    } else {
                        error('Deployment aborted by user')
                    }
                }
            }
            post {
                success {
                    slackSend(
                        channel: env.SLACK_CHANNEL,
                        color: 'good',
                        message: "🚀 Production deployment successful! Image: ${DOCKER_REGISTRY}/${IMAGE_NAME}:${env.GIT_COMMIT_SHORT}"
                    )
                }
                failure {
                    slackSend(
                        channel: env.SLACK_CHANNEL,
                        color: 'danger',
                        message: "💥 Production deployment failed: ${env.BUILD_URL}"
                    )
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
```

### 테스트 자동화
```python
# tests/conftest.py - pytest 설정
import pytest
import asyncio
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from src.main import app
from src.database import get_db, Base
from src.config import settings

# 테스트 데이터베이스 설정
TEST_DATABASE_URL = "postgresql://test:testpass@localhost:5432/ad_platform_test"

@pytest.fixture(scope="session")
def engine():
    """테스트 데이터베이스 엔진"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    """데이터베이스 세션"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    """테스트 클라이언트"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_campaign_data():
    """샘플 캠페인 데이터"""
    return {
        "name": "Test Campaign",
        "budget": 10000,
        "start_date": "2024-01-01T00:00:00",
        "end_date": "2024-12-31T23:59:59",
        "target_audience": {"age_range": [25, 45], "interests": ["technology"]}
    }

# tests/unit/test_campaign_service.py - 단위 테스트
import pytest
from unittest.mock import Mock, patch
from src.services.campaign_service import CampaignService
from src.models.campaign import Campaign

class TestCampaignService:
    
    @pytest.fixture
    def campaign_service(self, db_session):
        return CampaignService(db_session)
    
    def test_create_campaign(self, campaign_service, sample_campaign_data):
        """캠페인 생성 테스트"""
        campaign = campaign_service.create_campaign(sample_campaign_data)
        
        assert campaign.name == sample_campaign_data["name"]
        assert campaign.budget == sample_campaign_data["budget"]
        assert campaign.status == "draft"
    
    def test_update_campaign_budget(self, campaign_service, sample_campaign_data):
        """캠페인 예산 업데이트 테스트"""
        campaign = campaign_service.create_campaign(sample_campaign_data)
        
        updated_campaign = campaign_service.update_budget(campaign.id, 20000)
        
        assert updated_campaign.budget == 20000
    
    @patch('src.services.campaign_service.send_notification')
    def test_activate_campaign_sends_notification(self, mock_send_notification, 
                                                 campaign_service, sample_campaign_data):
        """캠페인 활성화 시 알림 전송 테스트"""
        campaign = campaign_service.create_campaign(sample_campaign_data)
        
        campaign_service.activate_campaign(campaign.id)
        
        mock_send_notification.assert_called_once()

# tests/integration/test_campaign_api.py - 통합 테스트
import pytest

class TestCampaignAPI:
    
    def test_create_campaign_endpoint(self, client, sample_campaign_data):
        """캠페인 생성 API 테스트"""
        response = client.post("/campaigns", json=sample_campaign_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_campaign_data["name"]
        assert "id" in data
    
    def test_get_campaign_list(self, client):
        """캠페인 목록 조회 테스트"""
        response = client.get("/campaigns")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["items"], list)
        assert "total" in data
    
    def test_update_campaign_unauthorized(self, client, sample_campaign_data):
        """권한 없는 캠페인 수정 테스트"""
        # 캠페인 생성
        create_response = client.post("/campaigns", json=sample_campaign_data)
        campaign_id = create_response.json()["id"]
        
        # 잘못된 토큰으로 수정 시도
        response = client.put(
            f"/campaigns/{campaign_id}",
            json={"name": "Updated Name"},
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401

# tests/performance/load_test.py - 성능 테스트
import asyncio
import aiohttp
import time
from typing import List

class LoadTester:
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = []
    
    async def make_request(self, session: aiohttp.ClientSession, 
                          endpoint: str, method: str = 'GET', 
                          data: dict = None) -> dict:
        """단일 요청 실행"""
        start_time = time.time()
        
        try:
            if method == 'GET':
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    status = response.status
                    await response.text()
            elif method == 'POST':
                async with session.post(f"{self.base_url}{endpoint}", json=data) as response:
                    status = response.status
                    await response.text()
            
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'method': method,
                'status': status,
                'response_time': end_time - start_time,
                'success': 200 <= status < 300
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'method': method,
                'status': 0,
                'response_time': end_time - start_time,
                'success': False,
                'error': str(e)
            }
    
    async def run_load_test(self, endpoints: List[dict], 
                           concurrent_users: int = 10,
                           duration_seconds: int = 60):
        """부하 테스트 실행"""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            tasks = []
            
            while time.time() - start_time < duration_seconds:
                for endpoint_config in endpoints:
                    for _ in range(concurrent_users):
                        task = self.make_request(
                            session,
                            endpoint_config['endpoint'],
                            endpoint_config.get('method', 'GET'),
                            endpoint_config.get('data')
                        )
                        tasks.append(task)
                
                # 배치 실행
                if len(tasks) >= 100:
                    results = await asyncio.gather(*tasks)
                    self.results.extend(results)
                    tasks = []
                
                await asyncio.sleep(0.1)
            
            # 남은 태스크 실행
            if tasks:
                results = await asyncio.gather(*tasks)
                self.results.extend(results)
    
    def generate_report(self) -> dict:
        """성능 리포트 생성"""
        if not self.results:
            return {}
        
        successful_requests = [r for r in self.results if r['success']]
        failed_requests = [r for r in self.results if not r['success']]
        
        response_times = [r['response_time'] for r in successful_requests]
        
        return {
            'total_requests': len(self.results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(self.results) * 100,
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'requests_per_second': len(self.results) / max(response_times) if response_times else 0
        }

# 성능 테스트 실행
async def main():
    tester = LoadTester('http://localhost:8000')
    
    endpoints = [
        {'endpoint': '/campaigns', 'method': 'GET'},
        {'endpoint': '/campaigns', 'method': 'POST', 'data': {'name': 'Test Campaign', 'budget': 1000}},
        {'endpoint': '/health', 'method': 'GET'}
    ]
    
    await tester.run_load_test(endpoints, concurrent_users=20, duration_seconds=30)
    report = tester.generate_report()
    
    print(f"Performance Test Results:")
    print(f"Total Requests: {report['total_requests']}")
    print(f"Success Rate: {report['success_rate']:.2f}%")
    print(f"Average Response Time: {report['avg_response_time']:.3f}s")
    print(f"Requests per Second: {report['requests_per_second']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🚀 프로젝트
1. **완전 자동화 CI/CD 파이프라인**
2. **무중단 Blue-Green 배포 시스템**
3. **통합 테스트 자동화 프레임워크**
4. **성능 모니터링 및 알림 시스템**