# 12. Deep Learning from Scratch - 딥러닝 스크래치 구현

## 📚 과정 소개
NumPy만으로 딥러닝 프레임워크를 구현하고, 광고 도메인에 특화된 신경망을 처음부터 만들어봅니다. 수학적 원리부터 최적화까지 완벽히 이해합니다.

## 🎯 학습 목표
- 역전파 알고리즘 직접 구현
- 광고 CTR 예측 신경망 구축
- 컨볼루션 신경망 스크래치 구현
- 최적화 알고리즘 이해와 구현

## 📖 주요 내용

### 기본 신경망 구현
```python
import numpy as np
from typing import List, Tuple, Dict

class Layer:
    """기본 레이어 인터페이스"""
    def forward(self, x):
        raise NotImplementedError
    
    def backward(self, grad):
        raise NotImplementedError

class Dense(Layer):
    """완전 연결 레이어"""
    def __init__(self, input_dim: int, output_dim: int):
        # He 초기화
        self.W = np.random.randn(input_dim, output_dim) * np.sqrt(2.0 / input_dim)
        self.b = np.zeros((1, output_dim))
        self.x = None
        self.dW = None
        self.db = None
        
    def forward(self, x: np.ndarray) -> np.ndarray:
        self.x = x
        return np.dot(x, self.W) + self.b
    
    def backward(self, dout: np.ndarray) -> np.ndarray:
        dx = np.dot(dout, self.W.T)
        self.dW = np.dot(self.x.T, dout)
        self.db = np.sum(dout, axis=0, keepdims=True)
        return dx

class ReLU(Layer):
    """ReLU 활성화 함수"""
    def __init__(self):
        self.mask = None
        
    def forward(self, x: np.ndarray) -> np.ndarray:
        self.mask = (x <= 0)
        out = x.copy()
        out[self.mask] = 0
        return out
    
    def backward(self, dout: np.ndarray) -> np.ndarray:
        dout[self.mask] = 0
        return dout

class Softmax(Layer):
    """Softmax with Cross Entropy Loss"""
    def __init__(self):
        self.y = None
        self.t = None
        
    def forward(self, x: np.ndarray, t: np.ndarray) -> float:
        self.t = t
        self.y = self._softmax(x)
        return self._cross_entropy(self.y, self.t)
    
    def backward(self, dout: float = 1) -> np.ndarray:
        batch_size = self.t.shape[0]
        return (self.y - self.t) / batch_size
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        x = x - np.max(x, axis=-1, keepdims=True)  # 오버플로우 방지
        return np.exp(x) / np.sum(np.exp(x), axis=-1, keepdims=True)
    
    def _cross_entropy(self, y: np.ndarray, t: np.ndarray) -> float:
        if y.ndim == 1:
            t = t.reshape(1, t.size)
            y = y.reshape(1, y.size)
        
        batch_size = y.shape[0]
        return -np.sum(t * np.log(y + 1e-7)) / batch_size
```

### CTR 예측 신경망
```python
class CTRPredictionNetwork:
    """광고 CTR 예측 신경망"""
    
    def __init__(self, input_dim: int, hidden_dims: List[int]):
        self.layers = []
        
        # 네트워크 구성
        dims = [input_dim] + hidden_dims + [2]  # 이진 분류
        
        for i in range(len(dims) - 1):
            self.layers.append(Dense(dims[i], dims[i+1]))
            if i < len(dims) - 2:  # 마지막 레이어 제외
                self.layers.append(ReLU())
        
        self.loss_layer = Softmax()
        
    def predict(self, x: np.ndarray) -> np.ndarray:
        for layer in self.layers:
            x = layer.forward(x)
        return x
    
    def loss(self, x: np.ndarray, t: np.ndarray) -> float:
        y = self.predict(x)
        return self.loss_layer.forward(y, t)
    
    def accuracy(self, x: np.ndarray, t: np.ndarray) -> float:
        y = self.predict(x)
        y = np.argmax(y, axis=1)
        t = np.argmax(t, axis=1)
        return np.sum(y == t) / x.shape[0]
    
    def gradient(self, x: np.ndarray, t: np.ndarray) -> Dict:
        # Forward
        self.loss(x, t)
        
        # Backward
        dout = self.loss_layer.backward()
        
        for layer in reversed(self.layers):
            dout = layer.backward(dout)
        
        # 가중치 수집
        grads = {}
        for i, layer in enumerate(self.layers):
            if isinstance(layer, Dense):
                grads[f'W{i}'] = layer.dW
                grads[f'b{i}'] = layer.db
        
        return grads
```

### 최적화 알고리즘 구현
```python
class Optimizer:
    """최적화 기본 클래스"""
    def update(self, params: Dict, grads: Dict):
        raise NotImplementedError

class SGD(Optimizer):
    """확률적 경사 하강법"""
    def __init__(self, lr: float = 0.01):
        self.lr = lr
        
    def update(self, params: Dict, grads: Dict):
        for key in params.keys():
            params[key] -= self.lr * grads[key]

class Adam(Optimizer):
    """Adam 최적화"""
    def __init__(self, lr: float = 0.001, beta1: float = 0.9, 
                 beta2: float = 0.999, epsilon: float = 1e-8):
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.m = {}
        self.v = {}
        self.t = 0
        
    def update(self, params: Dict, grads: Dict):
        self.t += 1
        
        for key in params.keys():
            if key not in self.m:
                self.m[key] = np.zeros_like(params[key])
                self.v[key] = np.zeros_like(params[key])
            
            # Momentum
            self.m[key] = self.beta1 * self.m[key] + (1 - self.beta1) * grads[key]
            # RMSprop
            self.v[key] = self.beta2 * self.v[key] + (1 - self.beta2) * (grads[key] ** 2)
            
            # Bias correction
            m_hat = self.m[key] / (1 - self.beta1 ** self.t)
            v_hat = self.v[key] / (1 - self.beta2 ** self.t)
            
            # Update
            params[key] -= self.lr * m_hat / (np.sqrt(v_hat) + self.epsilon)
```

### 학습 프로세스
```python
class Trainer:
    """신경망 학습기"""
    
    def __init__(self, network: CTRPredictionNetwork, 
                 optimizer: Optimizer):
        self.network = network
        self.optimizer = optimizer
        self.loss_history = []
        
    def train(self, x_train: np.ndarray, t_train: np.ndarray,
              x_val: np.ndarray, t_val: np.ndarray,
              epochs: int = 100, batch_size: int = 32):
        
        train_size = x_train.shape[0]
        iter_per_epoch = train_size // batch_size
        
        for epoch in range(epochs):
            # 데이터 셔플
            indices = np.random.permutation(train_size)
            x_train = x_train[indices]
            t_train = t_train[indices]
            
            epoch_loss = 0
            
            for i in range(iter_per_epoch):
                # 미니배치
                batch_mask = slice(i * batch_size, (i + 1) * batch_size)
                x_batch = x_train[batch_mask]
                t_batch = t_train[batch_mask]
                
                # 기울기 계산
                grads = self.network.gradient(x_batch, t_batch)
                
                # 매개변수 수집
                params = {}
                for i, layer in enumerate(self.network.layers):
                    if isinstance(layer, Dense):
                        params[f'W{i}'] = layer.W
                        params[f'b{i}'] = layer.b
                
                # 업데이트
                self.optimizer.update(params, grads)
                
                # 업데이트된 매개변수 적용
                for i, layer in enumerate(self.network.layers):
                    if isinstance(layer, Dense):
                        layer.W = params[f'W{i}']
                        layer.b = params[f'b{i}']
                
                # 손실 기록
                loss = self.network.loss(x_batch, t_batch)
                epoch_loss += loss
            
            # 검증
            val_loss = self.network.loss(x_val, t_val)
            val_acc = self.network.accuracy(x_val, t_val)
            
            print(f"Epoch {epoch+1}/{epochs} - "
                  f"Loss: {epoch_loss/iter_per_epoch:.4f}, "
                  f"Val Loss: {val_loss:.4f}, "
                  f"Val Acc: {val_acc:.4f}")
```

### 고급 기법 구현
```python
class Dropout(Layer):
    """드롭아웃 레이어"""
    def __init__(self, dropout_ratio: float = 0.5):
        self.dropout_ratio = dropout_ratio
        self.mask = None
        self.training = True
        
    def forward(self, x: np.ndarray) -> np.ndarray:
        if self.training:
            self.mask = np.random.rand(*x.shape) > self.dropout_ratio
            return x * self.mask / (1.0 - self.dropout_ratio)
        else:
            return x
    
    def backward(self, dout: np.ndarray) -> np.ndarray:
        return dout * self.mask / (1.0 - self.dropout_ratio)

class BatchNormalization(Layer):
    """배치 정규화"""
    def __init__(self, momentum: float = 0.9, epsilon: float = 1e-5):
        self.gamma = None
        self.beta = None
        self.momentum = momentum
        self.epsilon = epsilon
        self.running_mean = None
        self.running_var = None
        
    def forward(self, x: np.ndarray) -> np.ndarray:
        if self.gamma is None:
            self.gamma = np.ones(x.shape[1])
            self.beta = np.zeros(x.shape[1])
            self.running_mean = np.zeros(x.shape[1])
            self.running_var = np.ones(x.shape[1])
        
        if self.training:
            mu = x.mean(axis=0)
            var = x.var(axis=0)
            self.running_mean = self.momentum * self.running_mean + (1 - self.momentum) * mu
            self.running_var = self.momentum * self.running_var + (1 - self.momentum) * var
        else:
            mu = self.running_mean
            var = self.running_var
        
        self.x_normalized = (x - mu) / np.sqrt(var + self.epsilon)
        return self.gamma * self.x_normalized + self.beta
```

## 🚀 프로젝트
1. **광고 CTR 예측 모델 (스크래치)**
2. **이미지 기반 광고 분류 CNN**
3. **시계열 광고 성과 예측 RNN**
4. **GAN을 이용한 광고 이미지 생성**