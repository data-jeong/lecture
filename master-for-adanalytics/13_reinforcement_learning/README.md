# 13. Reinforcement Learning - 강화학습

## 📚 과정 소개
강화학습을 활용한 광고 최적화와 자동 입찰 시스템을 구축합니다. 실시간 의사결정과 장기 성과 최적화를 위한 RL 알고리즘을 마스터합니다.

## 🎯 학습 목표
- 광고 입찰 최적화 RL 모델
- 멀티 아암 밴딧 실험
- 딥 Q러닝 구현
- 실시간 전략 조정 시스템

## 📖 주요 내용

### 멀티 아암 밴딧 (MAB) 구현
```python
import numpy as np
from typing import List, Dict, Tuple
from abc import ABC, abstractmethod

class Bandit(ABC):
    """밴딧 알고리즘 기본 클래스"""
    
    def __init__(self, n_arms: int):
        self.n_arms = n_arms
        self.counts = np.zeros(n_arms)
        self.values = np.zeros(n_arms)
        self.t = 0
        
    @abstractmethod
    def select_arm(self) -> int:
        pass
    
    def update(self, arm: int, reward: float):
        self.counts[arm] += 1
        self.values[arm] += (reward - self.values[arm]) / self.counts[arm]
        self.t += 1

class EpsilonGreedy(Bandit):
    """엡실론 그리디 알고리즘"""
    
    def __init__(self, n_arms: int, epsilon: float = 0.1):
        super().__init__(n_arms)
        self.epsilon = epsilon
        
    def select_arm(self) -> int:
        if np.random.random() > self.epsilon:
            # 그리디: 최고 가치 선택
            return np.argmax(self.values)
        else:
            # 탐험: 랜덤 선택
            return np.random.randint(self.n_arms)

class UCB(Bandit):
    """Upper Confidence Bound"""
    
    def __init__(self, n_arms: int, c: float = 2.0):
        super().__init__(n_arms)
        self.c = c
        
    def select_arm(self) -> int:
        if self.t < self.n_arms:
            return self.t  # 모든 arm을 한 번씩 시도
        
        # UCB 계산
        confidence_bounds = self.values + self.c * np.sqrt(
            np.log(self.t) / (self.counts + 1e-5)
        )
        return np.argmax(confidence_bounds)

class ThompsonSampling(Bandit):
    """톰슨 샘플링 (베이지안 접근)"""
    
    def __init__(self, n_arms: int):
        super().__init__(n_arms)
        self.alpha = np.ones(n_arms)  # 성공 횟수 + 1
        self.beta = np.ones(n_arms)   # 실패 횟수 + 1
        
    def select_arm(self) -> int:
        # 베타 분포에서 샘플링
        samples = np.random.beta(self.alpha, self.beta)
        return np.argmax(samples)
    
    def update(self, arm: int, reward: float):
        super().update(arm, reward)
        if reward > 0:
            self.alpha[arm] += 1
        else:
            self.beta[arm] += 1
```

### 광고 입찰 최적화 밴딧
```python
class AdBiddingBandit:
    """광고 입찰 최적화를 위한 밴딧"""
    
    def __init__(self, bid_ranges: List[Tuple[float, float]], 
                 algorithm: str = 'ucb'):
        self.bid_ranges = bid_ranges
        self.n_arms = len(bid_ranges)
        
        if algorithm == 'epsilon_greedy':
            self.bandit = EpsilonGreedy(self.n_arms, epsilon=0.1)
        elif algorithm == 'ucb':
            self.bandit = UCB(self.n_arms, c=2.0)
        else:
            self.bandit = ThompsonSampling(self.n_arms)
        
        self.performance_history = []
        
    def select_bid(self) -> float:
        """최적 입찰가 선택"""
        arm = self.bandit.select_arm()
        min_bid, max_bid = self.bid_ranges[arm]
        # 범위 내에서 랜덤 선택
        return np.random.uniform(min_bid, max_bid)
    
    def update_performance(self, bid: float, cost: float, 
                          conversions: int, revenue: float):
        """성과 업데이트"""
        # 입찰가가 속한 arm 찾기
        arm = self._find_arm_for_bid(bid)
        
        # ROI 계산
        roi = (revenue - cost) / cost if cost > 0 else 0
        
        # 밴딧 업데이트
        self.bandit.update(arm, roi)
        
        # 이력 저장
        self.performance_history.append({
            'bid': bid,
            'arm': arm,
            'cost': cost,
            'conversions': conversions,
            'revenue': revenue,
            'roi': roi
        })
    
    def _find_arm_for_bid(self, bid: float) -> int:
        for i, (min_bid, max_bid) in enumerate(self.bid_ranges):
            if min_bid <= bid <= max_bid:
                return i
        return 0  # 기본값
```

### Deep Q-Learning (DQN) 구현
```python
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque

class DQN(nn.Module):
    """Deep Q Network"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 128):
        super(DQN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim)
        )
        
    def forward(self, x):
        return self.network(x)

class DQNAgent:
    """DQN 에이전트"""
    
    def __init__(self, state_dim: int, action_dim: int, 
                 lr: float = 0.001, gamma: float = 0.99,
                 epsilon: float = 1.0, epsilon_decay: float = 0.995,
                 memory_size: int = 10000):
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = 0.01
        
        # 네트워크
        self.q_network = DQN(state_dim, action_dim)
        self.target_network = DQN(state_dim, action_dim)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)
        
        # 경험 재생
        self.memory = deque(maxlen=memory_size)
        
        # 타겟 네트워크 동기화
        self.update_target_network()
        
    def update_target_network(self):
        """타겟 네트워크 업데이트"""
        self.target_network.load_state_dict(self.q_network.state_dict())
        
    def remember(self, state, action, reward, next_state, done):
        """경험 저장"""
        self.memory.append((state, action, reward, next_state, done))
        
    def act(self, state):
        """행동 선택 (엡실론 그리디)"""
        if np.random.random() <= self.epsilon:
            return random.randrange(self.action_dim)
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        q_values = self.q_network(state_tensor)
        return q_values.argmax().item()
        
    def replay(self, batch_size: int = 32):
        """경험 재생 학습"""
        if len(self.memory) < batch_size:
            return
            
        batch = random.sample(self.memory, batch_size)
        states = torch.FloatTensor([e[0] for e in batch])
        actions = torch.LongTensor([e[1] for e in batch])
        rewards = torch.FloatTensor([e[2] for e in batch])
        next_states = torch.FloatTensor([e[3] for e in batch])
        dones = torch.BoolTensor([e[4] for e in batch])
        
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        next_q_values = self.target_network(next_states).max(1)[0].detach()
        target_q_values = rewards + (self.gamma * next_q_values * ~dones)
        
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # 엡실론 감소
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
```

### 광고 환경 시뮬레이터
```python
class AdEnvironment:
    """광고 환경 시뮬레이터"""
    
    def __init__(self):
        self.reset()
        
    def reset(self) -> np.ndarray:
        """환경 초기화"""
        self.time_step = 0
        self.budget_remaining = 100000  # 초기 예산
        self.current_ctr = 0.02
        self.current_cpm = 1000
        self.market_competition = np.random.uniform(0.5, 1.5)
        
        return self._get_state()
    
    def _get_state(self) -> np.ndarray:
        """현재 상태 반환"""
        return np.array([
            self.time_step / 24,  # 정규화된 시간 (24시간 기준)
            self.budget_remaining / 100000,  # 정규화된 예산
            self.current_ctr,
            self.current_cpm / 2000,  # 정규화된 CPM
            self.market_competition,
        ])
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """행동 실행"""
        # 행동을 입찰 배수로 변환 (0.5x ~ 2.0x)
        bid_multiplier = 0.5 + (action / 9) * 1.5  # 10개 행동
        
        bid_amount = self.current_cpm * bid_multiplier
        
        # 환경 반응 시뮬레이션
        win_probability = min(bid_multiplier / self.market_competition, 1.0)
        impressions = int(np.random.poisson(1000 * win_probability))
        
        clicks = np.random.binomial(impressions, self.current_ctr)
        cost = impressions * bid_amount / 1000
        
        # 예산 차감
        cost = min(cost, self.budget_remaining)
        self.budget_remaining -= cost
        
        # 수익 계산 (가정: 클릭당 평균 수익 1500원)
        revenue = clicks * 1500
        
        # 보상 계산 (ROI 기반)
        reward = (revenue - cost) / max(cost, 1) if cost > 0 else 0
        
        # 환경 업데이트
        self.time_step += 1
        self._update_market_conditions()
        
        # 종료 조건
        done = self.time_step >= 24 or self.budget_remaining <= 0
        
        info = {
            'impressions': impressions,
            'clicks': clicks,
            'cost': cost,
            'revenue': revenue,
            'ctr': clicks / max(impressions, 1),
            'cpm': cost / max(impressions, 1) * 1000
        }
        
        return self._get_state(), reward, done, info
    
    def _update_market_conditions(self):
        """시장 상황 업데이트"""
        # 시간에 따른 CTR 변동
        hour = self.time_step % 24
        if 9 <= hour <= 18:  # 업무시간
            self.current_ctr = 0.025
        elif 18 <= hour <= 23:  # 저녁시간
            self.current_ctr = 0.03
        else:  # 심야/새벽
            self.current_ctr = 0.015
            
        # 경쟁 강도 변동
        self.market_competition += np.random.normal(0, 0.1)
        self.market_competition = np.clip(self.market_competition, 0.3, 2.0)
```

### 강화학습 트레이너
```python
class RLAdOptimizer:
    """강화학습 기반 광고 최적화기"""
    
    def __init__(self, state_dim: int = 5, action_dim: int = 10):
        self.env = AdEnvironment()
        self.agent = DQNAgent(state_dim, action_dim)
        self.training_history = []
        
    def train(self, episodes: int = 1000):
        """모델 학습"""
        for episode in range(episodes):
            state = self.env.reset()
            total_reward = 0
            total_cost = 0
            total_revenue = 0
            
            while True:
                action = self.agent.act(state)
                next_state, reward, done, info = self.env.step(action)
                
                self.agent.remember(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward
                total_cost += info['cost']
                total_revenue += info['revenue']
                
                if done:
                    break
            
            # 경험 재생 학습
            if len(self.agent.memory) > 1000:
                self.agent.replay()
            
            # 타겟 네트워크 업데이트
            if episode % 100 == 0:
                self.agent.update_target_network()
            
            # 성과 기록
            self.training_history.append({
                'episode': episode,
                'total_reward': total_reward,
                'total_cost': total_cost,
                'total_revenue': total_revenue,
                'roi': total_revenue / max(total_cost, 1),
                'epsilon': self.agent.epsilon
            })
            
            if episode % 100 == 0:
                avg_reward = np.mean([h['total_reward'] for h in self.training_history[-100:]])
                print(f"Episode {episode}, Avg Reward: {avg_reward:.4f}, "
                      f"Epsilon: {self.agent.epsilon:.4f}")
    
    def optimize_campaign(self, campaign_state: Dict) -> Dict:
        """실제 캠페인 최적화 추천"""
        state = np.array([
            campaign_state['time_progress'],
            campaign_state['budget_remaining'],
            campaign_state['current_ctr'],
            campaign_state['current_cpm'] / 2000,
            campaign_state['competition_level']
        ])
        
        # 최적 행동 선택 (탐험 없이)
        self.agent.epsilon = 0
        action = self.agent.act(state)
        
        # 행동을 실제 입찰 전략으로 변환
        bid_multiplier = 0.5 + (action / 9) * 1.5
        
        return {
            'recommended_bid_multiplier': bid_multiplier,
            'action_index': action,
            'confidence': 1 - self.agent.epsilon
        }
```

## 🚀 프로젝트
1. **실시간 광고 입찰 최적화 시스템**
2. **A/B 테스트 자동화 밴딧**
3. **예산 배분 최적화 RL 모델**
4. **크리에이티브 선택 강화학습**