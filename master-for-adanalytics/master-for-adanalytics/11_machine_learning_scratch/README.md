# 11. Machine Learning from Scratch - 머신러닝 스크래치 구현

## 📚 과정 소개
라이브러리에 의존하지 않고 머신러닝 알고리즘을 직접 구현하여 깊이 있는 이해를 도모합니다. 광고 마케팅 도메인에 특화된 ML 모델을 처음부터 만들어봅니다.

## 🎯 학습 목표
- ML 알고리즘의 수학적 원리 완벽 이해
- NumPy만으로 모든 알고리즘 구현
- 광고 도메인 특화 최적화
- 프로덕션 레벨 코드 작성

## 📖 커리큘럼

### Chapter 01-02: 선형대수 & 미적분 기초
```python
# 광고 CTR 예측을 위한 경사하강법 구현
class GradientDescent:
    def __init__(self, learning_rate=0.01):
        self.lr = learning_rate
    
    def compute_gradient(self, X, y, weights):
        m = len(y)
        predictions = X.dot(weights)
        errors = predictions - y
        gradient = (1/m) * X.T.dot(errors)
        return gradient
```

### Chapter 03-04: 선형/로지스틱 회귀
- CTR 예측 모델 구현
- 광고 비용 최적화
- 정규화 기법 적용

### Chapter 05-08: 트리 기반 모델
- 의사결정트리로 고객 세분화
- 랜덤포레스트 앙상블
- 그래디언트 부스팅 구현

### Chapter 09-10: 클러스터링
- K-means로 고객 군집화
- DBSCAN으로 이상 탐지

### Chapter 11-12: 신경망 기초
- 퍼셉트론부터 시작
- 역전파 알고리즘 구현
- 광고 추천 신경망

### Chapter 13-15: 최적화 & 정규화
- Adam, RMSprop 구현
- Dropout, L1/L2 정규화
- 조기 종료 전략

### Chapter 16-17: 앙상블 기법
- 배깅 & 부스팅
- 스태킹 구현

### Chapter 18-20: 마케팅 ML 특화
- LTV 예측 모델
- 이탈 예측 시스템
- 광고 입찰 최적화

## 🚀 핵심 프로젝트
1. **CTR 예측 엔진 (스크래치)**
2. **고객 세분화 시스템**
3. **광고 추천 알고리즘**
4. **실시간 입찰 최적화기**

## 💡 구현 예시: CTR 예측 모델

```python
import numpy as np

class CTRPredictor:
    """광고 CTR 예측 모델 (스크래치 구현)"""
    
    def __init__(self, learning_rate=0.01, epochs=1000):
        self.lr = learning_rate
        self.epochs = epochs
        self.weights = None
        self.bias = None
        
    def sigmoid(self, z):
        """시그모이드 활성화 함수"""
        return 1 / (1 + np.exp(-np.clip(z, -500, 500)))
    
    def fit(self, X, y):
        """모델 학습"""
        m, n = X.shape
        self.weights = np.zeros(n)
        self.bias = 0
        
        for epoch in range(self.epochs):
            # Forward propagation
            z = X.dot(self.weights) + self.bias
            predictions = self.sigmoid(z)
            
            # Compute loss
            loss = -np.mean(y * np.log(predictions + 1e-7) + 
                           (1 - y) * np.log(1 - predictions + 1e-7))
            
            # Backward propagation
            dz = predictions - y
            dw = (1/m) * X.T.dot(dz)
            db = (1/m) * np.sum(dz)
            
            # Update parameters
            self.weights -= self.lr * dw
            self.bias -= self.lr * db
            
            if epoch % 100 == 0:
                print(f"Epoch {epoch}, Loss: {loss:.4f}")
    
    def predict_proba(self, X):
        """CTR 확률 예측"""
        z = X.dot(self.weights) + self.bias
        return self.sigmoid(z)
    
    def predict(self, X, threshold=0.5):
        """클릭 여부 예측"""
        return self.predict_proba(X) >= threshold

# 사용 예시
# 광고 특성: [노출시간, 위치점수, 사용자관련도, 광고품질점수]
X_train = np.array([
    [0.8, 0.9, 0.7, 0.8],  # 높은 CTR 예상
    [0.2, 0.3, 0.1, 0.4],  # 낮은 CTR 예상
    # ... 더 많은 데이터
])
y_train = np.array([1, 0, ...])  # 실제 클릭 여부

model = CTRPredictor(learning_rate=0.1, epochs=1000)
model.fit(X_train, y_train)

# 새로운 광고의 CTR 예측
new_ad = np.array([[0.7, 0.8, 0.6, 0.9]])
ctr_probability = model.predict_proba(new_ad)
print(f"예상 CTR: {ctr_probability[0]:.2%}")
```

---

다음: [Chapter 01: Linear Algebra with NumPy →](01_linear_algebra_numpy/README.md)