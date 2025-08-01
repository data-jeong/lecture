# 33. Attribution Modeling - 어트리뷰션 모델링

## 📚 과정 소개
마케팅 터치포인트의 기여도를 과학적으로 측정하는 어트리뷰션 모델링을 마스터합니다. 룰 기반부터 알고리즘 기반, 통계적 모델까지 포괄적으로 다룹니다.

## 🎯 학습 목표
- 다양한 어트리뷰션 모델 구현
- 마케팅 믹스 모델링 (MMM)
- 증분성 테스트 설계
- 크로스 디바이스 어트리뷰션

## 📖 주요 내용

### 룰 기반 어트리뷰션 모델
```python
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from dataclasses import dataclass

@dataclass
class TouchpointData:
    """터치포인트 데이터 클래스"""
    user_id: str
    timestamp: datetime
    channel: str
    campaign: str
    cost: float
    interaction_type: str  # impression, click, visit

@dataclass
class ConversionData:
    """전환 데이터 클래스"""
    user_id: str
    timestamp: datetime
    value: float
    conversion_type: str

class RuleBasedAttribution:
    """룰 기반 어트리뷰션 모델"""
    
    def __init__(self):
        self.touchpoints = []
        self.conversions = []
        
    def add_touchpoint(self, touchpoint: TouchpointData):
        """터치포인트 추가"""
        self.touchpoints.append(touchpoint)
    
    def add_conversion(self, conversion: ConversionData):
        """전환 추가"""
        self.conversions.append(conversion)
    
    def first_touch_attribution(self, lookback_days: int = 30) -> Dict:
        """퍼스트 터치 어트리뷰션"""
        attribution_results = {}
        
        for conversion in self.conversions:
            # 전환 전 터치포인트 찾기
            user_touchpoints = [
                tp for tp in self.touchpoints 
                if tp.user_id == conversion.user_id 
                and tp.timestamp <= conversion.timestamp
                and (conversion.timestamp - tp.timestamp).days <= lookback_days
            ]
            
            if user_touchpoints:
                # 첫 번째 터치포인트에 100% 기여
                first_touch = min(user_touchpoints, key=lambda x: x.timestamp)
                key = f"{first_touch.channel}_{first_touch.campaign}"
                
                if key not in attribution_results:
                    attribution_results[key] = {
                        'channel': first_touch.channel,
                        'campaign': first_touch.campaign,
                        'conversions': 0,
                        'revenue': 0,
                        'cost': 0
                    }
                
                attribution_results[key]['conversions'] += 1
                attribution_results[key]['revenue'] += conversion.value
                attribution_results[key]['cost'] += first_touch.cost
        
        return self._calculate_metrics(attribution_results)
    
    def last_touch_attribution(self, lookback_days: int = 30) -> Dict:
        """라스트 터치 어트리뷰션"""
        attribution_results = {}
        
        for conversion in self.conversions:
            user_touchpoints = [
                tp for tp in self.touchpoints 
                if tp.user_id == conversion.user_id 
                and tp.timestamp <= conversion.timestamp
                and (conversion.timestamp - tp.timestamp).days <= lookback_days
            ]
            
            if user_touchpoints:
                # 마지막 터치포인트에 100% 기여
                last_touch = max(user_touchpoints, key=lambda x: x.timestamp)
                key = f"{last_touch.channel}_{last_touch.campaign}"
                
                if key not in attribution_results:
                    attribution_results[key] = {
                        'channel': last_touch.channel,
                        'campaign': last_touch.campaign,
                        'conversions': 0,
                        'revenue': 0,
                        'cost': 0
                    }
                
                attribution_results[key]['conversions'] += 1
                attribution_results[key]['revenue'] += conversion.value
                attribution_results[key]['cost'] += last_touch.cost
        
        return self._calculate_metrics(attribution_results)
    
    def linear_attribution(self, lookback_days: int = 30) -> Dict:
        """선형 어트리뷰션"""
        attribution_results = {}
        
        for conversion in self.conversions:
            user_touchpoints = [
                tp for tp in self.touchpoints 
                if tp.user_id == conversion.user_id 
                and tp.timestamp <= conversion.timestamp
                and (conversion.timestamp - tp.timestamp).days <= lookback_days
            ]
            
            if user_touchpoints:
                # 모든 터치포인트에 균등하게 기여도 분배
                attribution_weight = 1.0 / len(user_touchpoints)
                
                for touchpoint in user_touchpoints:
                    key = f"{touchpoint.channel}_{touchpoint.campaign}"
                    
                    if key not in attribution_results:
                        attribution_results[key] = {
                            'channel': touchpoint.channel,
                            'campaign': touchpoint.campaign,
                            'conversions': 0,
                            'revenue': 0,
                            'cost': 0
                        }
                    
                    attribution_results[key]['conversions'] += attribution_weight
                    attribution_results[key]['revenue'] += conversion.value * attribution_weight
                    attribution_results[key]['cost'] += touchpoint.cost * attribution_weight
        
        return self._calculate_metrics(attribution_results)
    
    def time_decay_attribution(self, lookback_days: int = 30, 
                              decay_rate: float = 0.7) -> Dict:
        """시간 감쇠 어트리뷰션"""
        attribution_results = {}
        
        for conversion in self.conversions:
            user_touchpoints = [
                tp for tp in self.touchpoints 
                if tp.user_id == conversion.user_id 
                and tp.timestamp <= conversion.timestamp
                and (conversion.timestamp - tp.timestamp).days <= lookback_days
            ]
            
            if user_touchpoints:
                # 전환 시점부터의 시간에 따른 가중치 계산
                total_weight = 0
                touchpoint_weights = []
                
                for touchpoint in user_touchpoints:
                    days_ago = (conversion.timestamp - touchpoint.timestamp).days
                    weight = decay_rate ** days_ago
                    touchpoint_weights.append((touchpoint, weight))
                    total_weight += weight
                
                # 가중치 정규화 및 기여도 분배
                for touchpoint, weight in touchpoint_weights:
                    normalized_weight = weight / total_weight
                    key = f"{touchpoint.channel}_{touchpoint.campaign}"
                    
                    if key not in attribution_results:
                        attribution_results[key] = {
                            'channel': touchpoint.channel,
                            'campaign': touchpoint.campaign,
                            'conversions': 0,
                            'revenue': 0,
                            'cost': 0
                        }
                    
                    attribution_results[key]['conversions'] += normalized_weight
                    attribution_results[key]['revenue'] += conversion.value * normalized_weight
                    attribution_results[key]['cost'] += touchpoint.cost * normalized_weight
        
        return self._calculate_metrics(attribution_results)
    
    def u_shaped_attribution(self, lookback_days: int = 30) -> Dict:
        """U자형 어트리뷰션 (40%-20%-40%)"""
        attribution_results = {}
        
        for conversion in self.conversions:
            user_touchpoints = [
                tp for tp in self.touchpoints 
                if tp.user_id == conversion.user_id 
                and tp.timestamp <= conversion.timestamp
                and (conversion.timestamp - tp.timestamp).days <= lookback_days
            ]
            
            if user_touchpoints:
                user_touchpoints.sort(key=lambda x: x.timestamp)
                n_touchpoints = len(user_touchpoints)
                
                for i, touchpoint in enumerate(user_touchpoints):
                    if n_touchpoints == 1:
                        weight = 1.0
                    elif n_touchpoints == 2:
                        weight = 0.5  # 50-50 분배
                    else:
                        if i == 0:  # 첫 번째
                            weight = 0.4
                        elif i == n_touchpoints - 1:  # 마지막
                            weight = 0.4
                        else:  # 중간 터치포인트들
                            weight = 0.2 / (n_touchpoints - 2)
                    
                    key = f"{touchpoint.channel}_{touchpoint.campaign}"
                    
                    if key not in attribution_results:
                        attribution_results[key] = {
                            'channel': touchpoint.channel,
                            'campaign': touchpoint.campaign,
                            'conversions': 0,
                            'revenue': 0,
                            'cost': 0
                        }
                    
                    attribution_results[key]['conversions'] += weight
                    attribution_results[key]['revenue'] += conversion.value * weight
                    attribution_results[key]['cost'] += touchpoint.cost * weight
        
        return self._calculate_metrics(attribution_results)
    
    def _calculate_metrics(self, attribution_results: Dict) -> Dict:
        """성과 지표 계산"""
        for key, data in attribution_results.items():
            data['cpa'] = data['cost'] / data['conversions'] if data['conversions'] > 0 else 0
            data['roas'] = data['revenue'] / data['cost'] if data['cost'] > 0 else 0
            data['roi'] = (data['revenue'] - data['cost']) / data['cost'] if data['cost'] > 0 else 0
        
        return attribution_results

class AlgorithmicAttribution:
    """알고리즘 기반 어트리뷰션"""
    
    def __init__(self):
        self.model_data = pd.DataFrame()
        
    def prepare_data(self, touchpoints: List[TouchpointData], 
                    conversions: List[ConversionData]) -> pd.DataFrame:
        """데이터 준비"""
        # 사용자별 여정 데이터 생성
        journey_data = []
        
        conversion_dict = {conv.user_id: conv for conv in conversions}
        
        # 사용자별 터치포인트 그룹화
        user_touchpoints = {}
        for tp in touchpoints:
            if tp.user_id not in user_touchpoints:
                user_touchpoints[tp.user_id] = []
            user_touchpoints[tp.user_id].append(tp)
        
        for user_id, user_tps in user_touchpoints.items():
            # 시간순 정렬
            user_tps.sort(key=lambda x: x.timestamp)
            
            # 특성 추출
            features = self._extract_journey_features(user_tps)
            
            # 전환 여부
            converted = 1 if user_id in conversion_dict else 0
            conversion_value = conversion_dict[user_id].value if converted else 0
            
            journey_data.append({
                'user_id': user_id,
                'converted': converted,
                'conversion_value': conversion_value,
                **features
            })
        
        return pd.DataFrame(journey_data)
    
    def _extract_journey_features(self, touchpoints: List[TouchpointData]) -> Dict:
        """여정 특성 추출"""
        if not touchpoints:
            return {}
        
        # 채널별 접촉 횟수
        channel_counts = {}
        for tp in touchpoints:
            channel_counts[tp.channel] = channel_counts.get(tp.channel, 0) + 1
        
        # 여정 특성
        features = {
            'journey_length': len(touchpoints),
            'unique_channels': len(set(tp.channel for tp in touchpoints)),
            'total_cost': sum(tp.cost for tp in touchpoints),
            'journey_duration_days': (touchpoints[-1].timestamp - touchpoints[0].timestamp).days,
            'first_channel': touchpoints[0].channel,
            'last_channel': touchpoints[-1].channel
        }
        
        # 채널별 원핫 인코딩
        all_channels = ['google_ads', 'facebook_ads', 'email', 'organic_search', 'direct']
        for channel in all_channels:
            features[f'has_{channel}'] = 1 if channel in channel_counts else 0
            features[f'count_{channel}'] = channel_counts.get(channel, 0)
        
        return features
    
    def train_shapley_model(self, data: pd.DataFrame) -> Dict:
        """샤플리 값 기반 어트리뷰션"""
        from itertools import combinations, permutations
        
        # 채널별 샤플리 값 계산
        channels = ['google_ads', 'facebook_ads', 'email', 'organic_search', 'direct']
        shapley_values = {channel: 0 for channel in channels}
        
        # 각 사용자의 여정에 대해 샤플리 값 계산
        for _, row in data.iterrows():
            user_channels = [ch for ch in channels if row[f'has_{ch}'] == 1]
            if not user_channels:
                continue
            
            user_shapley = self._calculate_user_shapley(user_channels, row['conversion_value'])
            
            for channel, value in user_shapley.items():
                shapley_values[channel] += value
        
        return shapley_values
    
    def _calculate_user_shapley(self, user_channels: List[str], conversion_value: float) -> Dict:
        """사용자별 샤플리 값 계산"""
        shapley_values = {channel: 0 for channel in user_channels}
        n = len(user_channels)
        
        # 모든 순열에 대해 기여도 계산
        for perm in permutations(user_channels):
            for i, channel in enumerate(perm):
                # 현재 채널 이전의 채널들
                prev_channels = set(perm[:i])
                curr_channels = prev_channels | {channel}
                
                # 기여도 = v(S ∪ {i}) - v(S)
                marginal_contribution = (
                    self._coalition_value(curr_channels, conversion_value) - 
                    self._coalition_value(prev_channels, conversion_value)
                )
                
                shapley_values[channel] += marginal_contribution / np.math.factorial(n)
        
        return shapley_values
    
    def _coalition_value(self, channels: set, conversion_value: float) -> float:
        """채널 연합의 가치 추정"""
        if not channels:
            return 0
        
        # 간단한 모델: 채널 수에 따른 전환 확률
        base_conversion_prob = 0.02
        channel_multipliers = {
            'google_ads': 1.2,
            'facebook_ads': 1.1,
            'email': 1.3,
            'organic_search': 1.5,
            'direct': 1.4
        }
        
        combined_multiplier = 1.0
        for channel in channels:
            combined_multiplier *= channel_multipliers.get(channel, 1.0)
        
        # 채널 수가 많을수록 체감효과
        diminishing_factor = 0.8 ** (len(channels) - 1)
        
        conversion_prob = min(base_conversion_prob * combined_multiplier * diminishing_factor, 0.5)
        
        return conversion_value * conversion_prob

class MarkovChainAttribution:
    """마르코프 체인 어트리뷰션"""
    
    def __init__(self):
        self.transition_matrix = {}
        self.removal_effects = {}
        
    def build_transition_matrix(self, journeys: List[List[str]]) -> Dict:
        """전이 행렬 구축"""
        transitions = {}
        
        for journey in journeys:
            # 시작 상태 추가
            extended_journey = ['(start)'] + journey + ['(conversion)']
            
            for i in range(len(extended_journey) - 1):
                current_state = extended_journey[i]
                next_state = extended_journey[i + 1]
                
                if current_state not in transitions:
                    transitions[current_state] = {}
                
                if next_state not in transitions[current_state]:
                    transitions[current_state][next_state] = 0
                
                transitions[current_state][next_state] += 1
        
        # 확률로 변환
        for current_state in transitions:
            total = sum(transitions[current_state].values())
            for next_state in transitions[current_state]:
                transitions[current_state][next_state] /= total
        
        self.transition_matrix = transitions
        return transitions
    
    def calculate_removal_effect(self, channel_to_remove: str) -> float:
        """채널 제거 효과 계산"""
        # 원본 전환 확률
        original_conversion_prob = self._calculate_conversion_probability()
        
        # 채널 제거 후 전환 확률
        modified_matrix = self._remove_channel(channel_to_remove)
        modified_conversion_prob = self._calculate_conversion_probability(modified_matrix)
        
        # 제거 효과 = 원본 확률 - 수정된 확률
        removal_effect = original_conversion_prob - modified_conversion_prob
        
        return removal_effect
    
    def _calculate_conversion_probability(self, transition_matrix: Dict = None) -> float:
        """전환 확률 계산"""
        if transition_matrix is None:
            transition_matrix = self.transition_matrix
        
        # 흡수 상태까지의 확률 계산 (간단한 시뮬레이션)
        conversion_count = 0
        total_simulations = 10000
        
        for _ in range(total_simulations):
            current_state = '(start)'
            
            while current_state not in ['(conversion)', '(null)'] and current_state in transition_matrix:
                # 다음 상태 선택
                next_states = list(transition_matrix[current_state].keys())
                probabilities = list(transition_matrix[current_state].values())
                
                current_state = np.random.choice(next_states, p=probabilities)
            
            if current_state == '(conversion)':
                conversion_count += 1
        
        return conversion_count / total_simulations
    
    def _remove_channel(self, channel: str) -> Dict:
        """채널 제거한 전이 행렬 생성"""
        modified_matrix = {}
        
        for current_state, transitions in self.transition_matrix.items():
            if current_state == channel:
                continue  # 제거할 채널은 건너뛰기
            
            modified_matrix[current_state] = {}
            total_prob = 0
            
            # 제거할 채널을 제외한 전이 확률 재계산
            for next_state, prob in transitions.items():
                if next_state != channel:
                    modified_matrix[current_state][next_state] = prob
                    total_prob += prob
            
            # 확률 정규화
            if total_prob > 0:
                for next_state in modified_matrix[current_state]:
                    modified_matrix[current_state][next_state] /= total_prob
        
        return modified_matrix

class CrossDeviceAttribution:
    """크로스 디바이스 어트리뷰션"""
    
    def __init__(self):
        self.device_graph = {}
        
    def build_device_graph(self, login_data: List[Dict]) -> Dict:
        """디바이스 그래프 구축"""
        # 로그인 데이터로 디바이스 연결
        for record in login_data:
            user_id = record['user_id']
            device_id = record['device_id']
            
            if user_id not in self.device_graph:
                self.device_graph[user_id] = set()
            
            self.device_graph[user_id].add(device_id)
        
        return self.device_graph
    
    def attribute_cross_device_journeys(self, touchpoints: List[TouchpointData], 
                                      conversions: List[ConversionData]) -> Dict:
        """크로스 디바이스 여정 어트리뷰션"""
        # 디바이스 ID를 사용자 ID로 매핑
        device_to_user = {}
        for user_id, devices in self.device_graph.items():
            for device_id in devices:
                device_to_user[device_id] = user_id
        
        # 터치포인트를 사용자별로 통합
        user_journeys = {}
        
        for tp in touchpoints:
            # 디바이스 ID가 있다면 사용자 ID로 변환
            user_id = device_to_user.get(tp.user_id, tp.user_id)
            
            if user_id not in user_journeys:
                user_journeys[user_id] = []
            
            user_journeys[user_id].append(tp)
        
        # 통합된 여정으로 어트리뷰션 수행
        attribution_model = RuleBasedAttribution()
        
        for user_id, journey in user_journeys.items():
            for tp in journey:
                attribution_model.add_touchpoint(tp)
        
        for conv in conversions:
            user_id = device_to_user.get(conv.user_id, conv.user_id)
            conv.user_id = user_id  # 사용자 ID로 변경
            attribution_model.add_conversion(conv)
        
        return attribution_model.linear_attribution()

# 사용 예시
def example_attribution_analysis():
    """어트리뷰션 분석 예시"""
    # 샘플 데이터 생성
    attribution_model = RuleBasedAttribution()
    
    # 터치포인트 추가
    touchpoints = [
        TouchpointData("user1", datetime(2024, 1, 1), "google_ads", "campaign1", 10.0, "click"),
        TouchpointData("user1", datetime(2024, 1, 5), "facebook_ads", "campaign2", 15.0, "click"),
        TouchpointData("user1", datetime(2024, 1, 10), "email", "newsletter", 2.0, "click"),
    ]
    
    conversions = [
        ConversionData("user1", datetime(2024, 1, 12), 100.0, "purchase")
    ]
    
    for tp in touchpoints:
        attribution_model.add_touchpoint(tp)
    
    for conv in conversions:
        attribution_model.add_conversion(conv)
    
    # 다양한 모델 비교
    results = {
        'first_touch': attribution_model.first_touch_attribution(),
        'last_touch': attribution_model.last_touch_attribution(),
        'linear': attribution_model.linear_attribution(),
        'time_decay': attribution_model.time_decay_attribution(),
        'u_shaped': attribution_model.u_shaped_attribution()
    }
    
    return results
```

## 🚀 프로젝트
1. **통합 어트리뷰션 플랫폼**
2. **마케팅 믹스 모델링 시스템**
3. **크로스 디바이스 여정 분석**
4. **실시간 어트리뷰션 대시보드**