# 43. Kubernetes Orchestration - 쿠버네티스 오케스트레이션

## 📚 과정 소개
대규모 광고 플랫폼을 위한 Kubernetes 클러스터 설계, 배포, 운영을 마스터합니다. 마이크로서비스 아키텍처, 오토스케일링, 모니터링까지 포괄적으로 다룹니다.

## 🎯 학습 목표
- 광고 플랫폼 마이크로서비스 설계
- Kubernetes 클러스터 운영
- CI/CD 파이프라인 구축
- 고가용성 및 장애 복구

## 📖 주요 내용

### 광고 플랫폼 마이크로서비스 아키텍처
```yaml
# ad-platform-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ad-platform
  labels:
    name: ad-platform
    environment: production
---
# ConfigMap for shared configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: ad-platform-config
  namespace: ad-platform
data:
  redis.host: "redis-service.ad-platform.svc.cluster.local"
  redis.port: "6379"
  postgres.host: "postgres-service.ad-platform.svc.cluster.local"
  postgres.port: "5432"
  kafka.brokers: "kafka-service.ad-platform.svc.cluster.local:9092"
  log.level: "INFO"
  metrics.enabled: "true"
```

```yaml
# campaign-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: campaign-service
  namespace: ad-platform
  labels:
    app: campaign-service
    tier: backend
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: campaign-service
  template:
    metadata:
      labels:
        app: campaign-service
        version: v1.0
    spec:
      containers:
      - name: campaign-service
        image: adplatform/campaign-service:v1.2.0
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 9090
          name: metrics
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        - name: REDIS_HOST
          valueFrom:
            configMapKeyRef:
              name: ad-platform-config
              key: redis.host
        - name: KAFKA_BROKERS
          valueFrom:
            configMapKeyRef:
              name: ad-platform-config
              key: kafka.brokers
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: logs-volume
          mountPath: /app/logs
      volumes:
      - name: config-volume
        configMap:
          name: campaign-service-config
      - name: logs-volume
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: campaign-service
  namespace: ad-platform
  labels:
    app: campaign-service
spec:
  selector:
    app: campaign-service
  ports:
  - name: http
    port: 80
    targetPort: 8080
  - name: metrics
    port: 9090
    targetPort: 9090
  type: ClusterIP
```

```yaml
# bidding-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bidding-service
  namespace: ad-platform
  labels:
    app: bidding-service
    tier: backend
spec:
  replicas: 5  # 높은 처리량을 위해 더 많은 복제본
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 2
  selector:
    matchLabels:
      app: bidding-service
  template:
    metadata:
      labels:
        app: bidding-service
        version: v1.0
    spec:
      containers:
      - name: bidding-service
        image: adplatform/bidding-service:v1.1.0
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: REDIS_HOST
          valueFrom:
            configMapKeyRef:
              name: ad-platform-config
              key: redis.host
        - name: KAFKA_BROKERS
          valueFrom:
            configMapKeyRef:
              name: ad-platform-config
              key: kafka.brokers
        - name: BID_TIMEOUT_MS
          value: "100"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 2
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 3
          timeoutSeconds: 2
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - bidding-service
              topologyKey: kubernetes.io/hostname
---
apiVersion: v1
kind: Service
metadata:
  name: bidding-service
  namespace: ad-platform
spec:
  selector:
    app: bidding-service
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
```

### 오토스케일링 설정
```yaml
# campaign-service-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: campaign-service-hpa
  namespace: ad-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: campaign-service
  minReplicas: 3
  maxReplicas: 20
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
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
---
# bidding-service-hpa.yaml - 더 aggressive한 스케일링
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bidding-service-hpa
  namespace: ad-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bidding-service
  minReplicas: 5
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60  # 더 낮은 임계값
  - type: Pods
    pods:
      metric:
        name: bid_requests_per_second
      target:
        type: AverageValue
        averageValue: "500"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30  # 빠른 스케일업
      policies:
      - type: Percent
        value: 200
        periodSeconds: 30
```

### 데이터베이스 및 캐시 클러스터
```yaml
# postgres-cluster.yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: ad-platform
type: Opaque
data:
  username: cG9zdGdyZXM=  # postgres (base64)
  password: YWRwbGF0Zm9ybTEyMw==  # adplatform123 (base64)
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres-master
  namespace: ad-platform
spec:
  serviceName: postgres-master
  replicas: 1
  selector:
    matchLabels:
      app: postgres
      role: master
  template:
    metadata:
      labels:
        app: postgres
        role: master
    spec:
      containers:
      - name: postgres
        image: postgres:13
        env:
        - name: POSTGRES_DB
          value: adplatform
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: POSTGRES_REPLICATION_USER
          value: replicator
        - name: POSTGRES_REPLICATION_PASSWORD
          value: replicator123
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        - name: postgres-config
          mountPath: /etc/postgresql
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
      volumes:
      - name: postgres-config
        configMap:
          name: postgres-config
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 100Gi
---
# Redis Cluster
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
  namespace: ad-platform
spec:
  serviceName: redis-cluster
  replicas: 6
  selector:
    matchLabels:
      app: redis-cluster
  template:
    metadata:
      labels:
        app: redis-cluster
    spec:
      containers:
      - name: redis
        image: redis:6.2-alpine
        command:
        - redis-server
        - /etc/redis/redis.conf
        - --cluster-enabled
        - "yes"
        - --cluster-config-file
        - /data/nodes.conf
        - --cluster-node-timeout
        - "5000"
        - --appendonly
        - "yes"
        ports:
        - containerPort: 6379
          name: redis
        - containerPort: 16379
          name: cluster
        volumeMounts:
        - name: redis-data
          mountPath: /data
        - name: redis-config
          mountPath: /etc/redis
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: redis-config
        configMap:
          name: redis-config
  volumeClaimTemplates:
  - metadata:
      name: redis-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 10Gi
```

### Ingress 및 네트워킹
```yaml
# ingress-controller.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ad-platform-ingress
  namespace: ad-platform
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit-connections: "100"
    nginx.ingress.kubernetes.io/rate-limit-requests-per-minute: "6000"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.adplatform.com
    - bidding.adplatform.com
    secretName: adplatform-tls
  rules:
  - host: api.adplatform.com
    http:
      paths:
      - path: /campaigns
        pathType: Prefix
        backend:
          service:
            name: campaign-service
            port:
              number: 80
      - path: /analytics
        pathType: Prefix
        backend:
          service:
            name: analytics-service
            port:
              number: 80
  - host: bidding.adplatform.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: bidding-service
            port:
              number: 80
---
# Network Policy for security
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ad-platform-network-policy
  namespace: ad-platform
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - namespaceSelector:
        matchLabels:
          name: monitoring
  - from:
    - podSelector: {}
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
  - to:
    - podSelector: {}
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
```

### 모니터링 및 로깅
```yaml
# prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    scrape_configs:
    - job_name: 'kubernetes-pods'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - ad-platform
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
    
    - job_name: 'campaign-service'
      static_configs:
      - targets: ['campaign-service.ad-platform:9090']
      scrape_interval: 10s
      metrics_path: /metrics
    
    - job_name: 'bidding-service'
      static_configs:
      - targets: ['bidding-service.ad-platform:9090']
      scrape_interval: 5s  # 더 자주 수집
      metrics_path: /metrics
    
    rule_files:
    - "alert_rules.yml"
    
    alerting:
      alertmanagers:
      - static_configs:
        - targets:
          - alertmanager:9093
---
# Alert Rules
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-alert-rules
  namespace: monitoring
data:
  alert_rules.yml: |
    groups:
    - name: ad-platform-alerts
      rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 5% for {{ $labels.service }}"
      
      - alert: HighBidLatency
        expr: histogram_quantile(0.95, rate(bid_request_duration_seconds_bucket[5m])) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High bid latency"
          description: "95th percentile latency is above 100ms"
      
      - alert: PodCrashLooping
        expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pod is crash looping"
          description: "Pod {{ $labels.pod }} is restarting frequently"
```

### CI/CD 파이프라인
```yaml
# gitlab-ci.yml
stages:
  - test
  - build
  - deploy-staging
  - deploy-production

variables:
  DOCKER_REGISTRY: registry.adplatform.com
  KUBERNETES_NAMESPACE_STAGING: ad-platform-staging
  KUBERNETES_NAMESPACE_PROD: ad-platform

test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest tests/ --cov=app/
    - flake8 app/
  coverage: '/TOTAL.*\s+(\d+%)$/'

build:
  stage: build
  script:
    - docker build -t $DOCKER_REGISTRY/campaign-service:$CI_COMMIT_SHA .
    - docker push $DOCKER_REGISTRY/campaign-service:$CI_COMMIT_SHA
  only:
    - master
    - develop

deploy-staging:
  stage: deploy-staging
  script:
    - kubectl config use-context staging-cluster
    - helm upgrade --install campaign-service ./helm/campaign-service
        --namespace $KUBERNETES_NAMESPACE_STAGING
        --set image.tag=$CI_COMMIT_SHA
        --set environment=staging
        --wait
    - kubectl get pods -n $KUBERNETES_NAMESPACE_STAGING
  environment:
    name: staging
    url: https://staging-api.adplatform.com
  only:
    - develop

deploy-production:
  stage: deploy-production
  script:
    - kubectl config use-context production-cluster
    - helm upgrade --install campaign-service ./helm/campaign-service
        --namespace $KUBERNETES_NAMESPACE_PROD
        --set image.tag=$CI_COMMIT_SHA
        --set environment=production
        --set replicas=5
        --wait
    - kubectl rollout status deployment/campaign-service -n $KUBERNETES_NAMESPACE_PROD
  environment:
    name: production
    url: https://api.adplatform.com
  when: manual
  only:
    - master
```

### Helm 차트 예시
```yaml
# helm/campaign-service/values.yaml
replicaCount: 3

image:
  repository: registry.adplatform.com/campaign-service
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: api.adplatform.com
      paths:
        - path: /campaigns
          pathType: Prefix
  tls:
    - secretName: adplatform-tls
      hosts:
        - api.adplatform.com

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 200m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70

nodeSelector: {}
tolerations: []
affinity: {}

# Environment-specific values
staging:
  replicaCount: 2
  resources:
    limits:
      memory: 256Mi
    requests:
      memory: 128Mi

production:
  replicaCount: 5
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi
```

```yaml
# helm/campaign-service/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "campaign-service.fullname" . }}
  labels:
    {{- include "campaign-service.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "campaign-service.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        prometheus.io/scrape: "true"
        prometheus.io/path: "/metrics"
        prometheus.io/port: "9090"
      labels:
        {{- include "campaign-service.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
            - name: metrics
              containerPort: 9090
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /health/live
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          env:
            - name: ENVIRONMENT
              value: {{ .Values.environment | default "production" }}
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: database-secret
                  key: url
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

### 보안 설정
```yaml
# security-policies.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: campaign-service-sa
  namespace: ad-platform
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: ad-platform
  name: campaign-service-role
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: campaign-service-rolebinding
  namespace: ad-platform
subjects:
- kind: ServiceAccount
  name: campaign-service-sa
  namespace: ad-platform
roleRef:
  kind: Role
  name: campaign-service-role
  apiGroup: rbac.authorization.k8s.io
---
# Pod Security Policy
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: ad-platform-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

## 🚀 프로젝트
1. **대규모 광고 플랫폼 K8s 클러스터**
2. **완전 자동화 CI/CD 파이프라인**
3. **실시간 모니터링 및 알림 시스템**
4. **고가용성 데이터베이스 클러스터**