# 25. Graph Databases - 그래프 데이터베이스

## 📚 과정 소개
광고 도메인에 특화된 그래프 데이터베이스를 마스터합니다. 고객 여정 분석, 영향력 전파, 추천 시스템, 사기 탐지까지 Neo4j를 활용한 복잡한 관계 데이터 분석을 학습합니다.

## 🎯 학습 목표
- 복잡한 고객 관계 모델링
- 실시간 추천 시스템 구축
- 소셜 네트워크 영향력 분석
- 광고 사기 탐지 시스템

## 📖 주요 내용

### 그래프 기반 광고 시스템
```python
from neo4j import GraphDatabase
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class User:
    """사용자 노드"""
    user_id: str
    demographics: Dict[str, Any]
    interests: List[str]
    behavior_score: float
    lifetime_value: float
    registration_date: datetime
    last_activity: datetime

@dataclass
class Product:
    """상품 노드"""
    product_id: str
    name: str
    category: str
    brand: str
    price: float
    features: List[str]
    popularity_score: float

@dataclass
class Campaign:
    """캠페인 노드"""
    campaign_id: str
    name: str
    advertiser: str
    budget: float
    start_date: datetime
    end_date: datetime
    target_audience: Dict[str, Any]
    objectives: List[str]

@dataclass
class AdInteraction:
    """광고 상호작용 관계"""
    user_id: str
    ad_id: str
    interaction_type: str  # impression, click, conversion
    timestamp: datetime
    value: float
    context: Dict[str, Any]

class Neo4jAdGraphManager:
    """Neo4j 광고 그래프 관리자"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", 
                 user: str = "neo4j", password: str = "password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.setup_constraints()
        self.setup_indices()
    
    def close(self):
        """연결 종료"""
        self.driver.close()
    
    def setup_constraints(self):
        """제약 조건 설정"""
        constraints = [
            "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
            "CREATE CONSTRAINT product_id_unique IF NOT EXISTS FOR (p:Product) REQUIRE p.product_id IS UNIQUE", 
            "CREATE CONSTRAINT campaign_id_unique IF NOT EXISTS FOR (c:Campaign) REQUIRE c.campaign_id IS UNIQUE",
            "CREATE CONSTRAINT ad_id_unique IF NOT EXISTS FOR (a:Ad) REQUIRE a.ad_id IS UNIQUE"
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"Constraint created: {constraint}")
                except Exception as e:
                    logger.debug(f"Constraint may already exist: {e}")
    
    def setup_indices(self):
        """인덱스 설정"""
        indices = [
            "CREATE INDEX user_demographics IF NOT EXISTS FOR (u:User) ON (u.age_group, u.gender)",
            "CREATE INDEX product_category IF NOT EXISTS FOR (p:Product) ON (p.category, p.brand)",
            "CREATE INDEX campaign_dates IF NOT EXISTS FOR (c:Campaign) ON (c.start_date, c.end_date)",
            "CREATE INDEX interaction_timestamp IF NOT EXISTS FOR ()-[r:INTERACTED_WITH]-() ON (r.timestamp)"
        ]
        
        with self.driver.session() as session:
            for index in indices:
                try:
                    session.run(index)
                    logger.info(f"Index created: {index}")
                except Exception as e:
                    logger.debug(f"Index may already exist: {e}")
    
    def create_user(self, user: User) -> bool:
        """사용자 노드 생성"""
        query = """
        CREATE (u:User {
            user_id: $user_id,
            age_group: $age_group,
            gender: $gender,
            income_level: $income_level,
            interests: $interests,
            behavior_score: $behavior_score,
            lifetime_value: $lifetime_value,
            registration_date: $registration_date,
            last_activity: $last_activity
        })
        """
        
        with self.driver.session() as session:
            try:
                session.run(query, 
                    user_id=user.user_id,
                    age_group=user.demographics.get('age_group'),
                    gender=user.demographics.get('gender'),
                    income_level=user.demographics.get('income_level'),
                    interests=user.interests,
                    behavior_score=user.behavior_score,
                    lifetime_value=user.lifetime_value,
                    registration_date=user.registration_date.isoformat(),
                    last_activity=user.last_activity.isoformat()
                )
                return True
            except Exception as e:
                logger.error(f"Error creating user {user.user_id}: {e}")
                return False
    
    def create_product(self, product: Product) -> bool:
        """상품 노드 생성"""
        query = """
        CREATE (p:Product {
            product_id: $product_id,
            name: $name,
            category: $category,
            brand: $brand,
            price: $price,
            features: $features,
            popularity_score: $popularity_score
        })
        """
        
        with self.driver.session() as session:
            try:
                session.run(query,
                    product_id=product.product_id,
                    name=product.name,
                    category=product.category,
                    brand=product.brand,
                    price=product.price,
                    features=product.features,
                    popularity_score=product.popularity_score
                )
                return True
            except Exception as e:
                logger.error(f"Error creating product {product.product_id}: {e}")
                return False
    
    def create_campaign(self, campaign: Campaign) -> bool:
        """캠페인 노드 생성"""
        query = """
        CREATE (c:Campaign {
            campaign_id: $campaign_id,
            name: $name,
            advertiser: $advertiser,
            budget: $budget,
            start_date: $start_date,
            end_date: $end_date,
            target_demographics: $target_demographics,
            objectives: $objectives
        })
        """
        
        with self.driver.session() as session:
            try:
                session.run(query,
                    campaign_id=campaign.campaign_id,
                    name=campaign.name,
                    advertiser=campaign.advertiser,
                    budget=campaign.budget,
                    start_date=campaign.start_date.isoformat(),
                    end_date=campaign.end_date.isoformat(),
                    target_demographics=json.dumps(campaign.target_audience),
                    objectives=campaign.objectives
                )
                return True
            except Exception as e:
                logger.error(f"Error creating campaign {campaign.campaign_id}: {e}")
                return False
    
    def create_interaction(self, interaction: AdInteraction) -> bool:
        """사용자-광고 상호작용 관계 생성"""
        query = """
        MATCH (u:User {user_id: $user_id})
        MATCH (a:Ad {ad_id: $ad_id})
        CREATE (u)-[r:INTERACTED_WITH {
            interaction_type: $interaction_type,
            timestamp: $timestamp,
            value: $value,
            context: $context
        }]->(a)
        """
        
        with self.driver.session() as session:
            try:
                session.run(query,
                    user_id=interaction.user_id,
                    ad_id=interaction.ad_id,
                    interaction_type=interaction.interaction_type,
                    timestamp=interaction.timestamp.isoformat(),
                    value=interaction.value,
                    context=json.dumps(interaction.context)
                )
                return True
            except Exception as e:
                logger.error(f"Error creating interaction: {e}")
                return False
    
    def create_user_similarity(self, user1_id: str, user2_id: str, 
                             similarity_score: float, similarity_type: str) -> bool:
        """사용자 간 유사성 관계 생성"""
        query = """
        MATCH (u1:User {user_id: $user1_id})
        MATCH (u2:User {user_id: $user2_id})
        CREATE (u1)-[r:SIMILAR_TO {
            similarity_score: $similarity_score,
            similarity_type: $similarity_type,
            created_at: $created_at
        }]->(u2)
        """
        
        with self.driver.session() as session:
            try:
                session.run(query,
                    user1_id=user1_id,
                    user2_id=user2_id,
                    similarity_score=similarity_score,
                    similarity_type=similarity_type,
                    created_at=datetime.now().isoformat()
                )
                return True
            except Exception as e:
                logger.error(f"Error creating similarity: {e}")
                return False

class CustomerJourneyAnalyzer:
    """고객 여정 분석기"""
    
    def __init__(self, graph_manager: Neo4jAdGraphManager):
        self.graph_manager = graph_manager
    
    def analyze_conversion_paths(self, user_id: str, 
                               days_back: int = 30) -> Dict[str, Any]:
        """전환 경로 분석"""
        query = """
        MATCH (u:User {user_id: $user_id})-[r:INTERACTED_WITH]->(a:Ad)
        WHERE r.timestamp >= $start_date
        WITH u, r, a
        ORDER BY r.timestamp
        RETURN 
            a.ad_id as ad_id,
            a.campaign_id as campaign_id,
            r.interaction_type as interaction_type,
            r.timestamp as timestamp,
            r.value as value
        """
        
        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        with self.graph_manager.driver.session() as session:
            result = session.run(query, user_id=user_id, start_date=start_date)
            
            journey_data = []
            for record in result:
                journey_data.append({
                    'ad_id': record['ad_id'],
                    'campaign_id': record['campaign_id'],
                    'interaction_type': record['interaction_type'],
                    'timestamp': record['timestamp'],
                    'value': record['value']
                })
        
        # 여정 패턴 분석
        return self._analyze_journey_patterns(journey_data)
    
    def _analyze_journey_patterns(self, journey_data: List[Dict]) -> Dict[str, Any]:
        """여정 패턴 분석"""
        if not journey_data:
            return {'touchpoints': 0, 'conversion_path': [], 'time_to_conversion': 0}
        
        # 터치포인트 순서
        touchpoints = [item['interaction_type'] for item in journey_data]
        
        # 전환까지의 시간
        first_interaction = datetime.fromisoformat(journey_data[0]['timestamp'])
        last_conversion = None
        
        for item in reversed(journey_data):
            if item['interaction_type'] == 'conversion':
                last_conversion = datetime.fromisoformat(item['timestamp'])
                break
        
        time_to_conversion = (last_conversion - first_interaction).days if last_conversion else 0
        
        # 캠페인별 기여도
        campaign_contributions = defaultdict(float)
        for item in journey_data:
            campaign_contributions[item['campaign_id']] += item['value']
        
        return {
            'touchpoints': len(journey_data),
            'conversion_path': touchpoints,
            'time_to_conversion_days': time_to_conversion,
            'campaign_contributions': dict(campaign_contributions),
            'conversion_funnel': self._calculate_funnel_metrics(touchpoints)
        }
    
    def _calculate_funnel_metrics(self, touchpoints: List[str]) -> Dict[str, float]:
        """퍼널 지표 계산"""
        funnel_stages = ['impression', 'click', 'conversion']
        stage_counts = {stage: touchpoints.count(stage) for stage in funnel_stages}
        
        metrics = {}
        if stage_counts['impression'] > 0:
            metrics['click_through_rate'] = stage_counts['click'] / stage_counts['impression']
        else:
            metrics['click_through_rate'] = 0
        
        if stage_counts['click'] > 0:
            metrics['conversion_rate'] = stage_counts['conversion'] / stage_counts['click']
        else:
            metrics['conversion_rate'] = 0
        
        return metrics
    
    def find_similar_customer_journeys(self, user_id: str, 
                                     similarity_threshold: float = 0.7) -> List[Dict]:
        """유사한 고객 여정 찾기"""
        query = """
        MATCH (u1:User {user_id: $user_id})-[r1:INTERACTED_WITH]->(a1:Ad)
        MATCH (u2:User)-[r2:INTERACTED_WITH]->(a2:Ad)
        WHERE u1 <> u2
        WITH u1, u2, 
             collect(DISTINCT r1.interaction_type) as u1_interactions,
             collect(DISTINCT r2.interaction_type) as u2_interactions
        WITH u1, u2, u1_interactions, u2_interactions,
             size([x IN u1_interactions WHERE x IN u2_interactions]) as common_interactions,
             size(u1_interactions + u2_interactions) as total_unique_interactions
        WITH u1, u2, 
             toFloat(common_interactions * 2) / total_unique_interactions as jaccard_similarity
        WHERE jaccard_similarity >= $similarity_threshold
        RETURN u2.user_id as similar_user_id, jaccard_similarity
        ORDER BY jaccard_similarity DESC
        LIMIT 10
        """
        
        with self.graph_manager.driver.session() as session:
            result = session.run(query, user_id=user_id, 
                               similarity_threshold=similarity_threshold)
            
            similar_users = []
            for record in result:
                similar_users.append({
                    'user_id': record['similar_user_id'],
                    'similarity_score': record['jaccard_similarity']
                })
            
            return similar_users

class InfluenceAnalyzer:
    """영향력 분석기"""
    
    def __init__(self, graph_manager: Neo4jAdGraphManager):
        self.graph_manager = graph_manager
    
    def calculate_user_influence(self, user_id: str) -> Dict[str, float]:
        """사용자 영향력 계산"""
        # PageRank 기반 영향력 계산
        pagerank_query = """
        CALL gds.pageRank.stream('user_similarity_graph')
        YIELD nodeId, score
        WITH gds.util.asNode(nodeId) AS user, score
        WHERE user.user_id = $user_id
        RETURN score as pagerank_score
        """
        
        # Degree Centrality 계산
        degree_query = """
        MATCH (u:User {user_id: $user_id})-[r:SIMILAR_TO]-(other:User)
        RETURN count(r) as degree_centrality
        """
        
        # Betweenness Centrality 계산 (간접적)
        betweenness_query = """
        MATCH (u:User {user_id: $user_id})
        MATCH (u)-[r1:SIMILAR_TO]-(other1:User)
        MATCH (u)-[r2:SIMILAR_TO]-(other2:User)
        WHERE other1 <> other2
        RETURN count(DISTINCT other1) + count(DISTINCT other2) as betweenness_proxy
        """
        
        results = {}
        
        with self.graph_manager.driver.session() as session:
            # PageRank 점수
            try:
                result = session.run(pagerank_query, user_id=user_id)
                record = result.single()
                results['pagerank_score'] = record['pagerank_score'] if record else 0.0
            except:
                results['pagerank_score'] = 0.0
            
            # Degree Centrality
            result = session.run(degree_query, user_id=user_id)
            record = result.single()
            results['degree_centrality'] = record['degree_centrality'] if record else 0
            
            # Betweenness 근사값
            result = session.run(betweenness_query, user_id=user_id)
            record = result.single()
            results['betweenness_proxy'] = record['betweenness_proxy'] if record else 0
        
        # 종합 영향력 점수 계산
        results['influence_score'] = (
            results['pagerank_score'] * 0.5 +
            (results['degree_centrality'] / 100) * 0.3 +
            (results['betweenness_proxy'] / 100) * 0.2
        )
        
        return results
    
    def find_influencers(self, top_k: int = 10) -> List[Dict]:
        """영향력자 찾기"""
        query = """
        MATCH (u:User)-[r:SIMILAR_TO]-(other:User)
        WITH u, count(r) as connections, 
             avg(r.similarity_score) as avg_similarity,
             u.lifetime_value as ltv,
             u.behavior_score as behavior
        WHERE connections >= 5
        WITH u, connections, avg_similarity, ltv, behavior,
             (connections * 0.3 + avg_similarity * 0.2 + ltv/10000 * 0.3 + behavior * 0.2) as influence_score
        RETURN u.user_id as user_id, 
               connections,
               avg_similarity,
               ltv,
               behavior,
               influence_score
        ORDER BY influence_score DESC
        LIMIT $top_k
        """
        
        with self.graph_manager.driver.session() as session:
            result = session.run(query, top_k=top_k)
            
            influencers = []
            for record in result:
                influencers.append({
                    'user_id': record['user_id'],
                    'connections': record['connections'],
                    'avg_similarity': record['avg_similarity'],
                    'lifetime_value': record['ltv'],
                    'behavior_score': record['behavior'],
                    'influence_score': record['influence_score']
                })
            
            return influencers
    
    def simulate_viral_spread(self, initial_users: List[str],
                            infection_rate: float = 0.1,
                            max_iterations: int = 10) -> Dict[str, Any]:
        """바이럴 전파 시뮬레이션"""
        # 간단한 SI 모델 (Susceptible-Infected)
        infected_users = set(initial_users)
        iteration_results = []
        
        for iteration in range(max_iterations):
            new_infections = set()
            
            # 현재 감염된 사용자들의 이웃 찾기
            query = """
            MATCH (infected:User)-[r:SIMILAR_TO]-(neighbor:User)
            WHERE infected.user_id IN $infected_users
            AND NOT neighbor.user_id IN $infected_users
            RETURN neighbor.user_id as neighbor_id, r.similarity_score as similarity
            """
            
            with self.graph_manager.driver.session() as session:
                result = session.run(query, infected_users=list(infected_users))
                
                for record in result:
                    neighbor_id = record['neighbor_id']
                    similarity = record['similarity']
                    
                    # 감염 확률 = infection_rate * similarity_score
                    infection_prob = infection_rate * similarity
                    
                    if np.random.random() < infection_prob:
                        new_infections.add(neighbor_id)
            
            if not new_infections:
                break
            
            infected_users.update(new_infections)
            
            iteration_results.append({
                'iteration': iteration + 1,
                'new_infections': len(new_infections),
                'total_infected': len(infected_users),
                'newly_infected_users': list(new_infections)
            })
        
        return {
            'total_infected': len(infected_users),
            'infection_rate_used': infection_rate,
            'iterations': len(iteration_results),
            'iteration_details': iteration_results,
            'final_infected_users': list(infected_users)
        }

class RecommendationEngine:
    """그래프 기반 추천 엔진"""
    
    def __init__(self, graph_manager: Neo4jAdGraphManager):
        self.graph_manager = graph_manager
    
    def recommend_products(self, user_id: str, top_k: int = 10) -> List[Dict]:
        """상품 추천"""
        # 협업 필터링 + 그래프 기반 추천
        query = """
        // 유사한 사용자들이 구매한 상품 찾기
        MATCH (u:User {user_id: $user_id})-[s:SIMILAR_TO]-(similar:User)
        MATCH (similar)-[r:INTERACTED_WITH]->(a:Ad)-[:PROMOTES]->(p:Product)
        WHERE r.interaction_type = 'conversion'
        AND NOT EXISTS((u)-[:INTERACTED_WITH]->(:Ad)-[:PROMOTES]->(p))
        
        WITH p, sum(s.similarity_score * r.value) as recommendation_score,
             count(DISTINCT similar) as similar_users_bought,
             p.popularity_score as popularity
        
        // 최종 추천 점수 계산
        WITH p, recommendation_score, similar_users_bought, popularity,
             (recommendation_score * 0.6 + popularity * 0.3 + similar_users_bought * 0.1) as final_score
        
        RETURN p.product_id as product_id,
               p.name as product_name,
               p.category as category,
               p.price as price,
               final_score,
               recommendation_score,
               similar_users_bought
        ORDER BY final_score DESC
        LIMIT $top_k
        """
        
        with self.graph_manager.driver.session() as session:
            result = session.run(query, user_id=user_id, top_k=top_k)
            
            recommendations = []
            for record in result:
                recommendations.append({
                    'product_id': record['product_id'],
                    'product_name': record['product_name'],
                    'category': record['category'],
                    'price': record['price'],
                    'recommendation_score': record['final_score'],
                    'collaborative_score': record['recommendation_score'],
                    'social_proof': record['similar_users_bought']
                })
            
            return recommendations
    
    def recommend_ads(self, user_id: str, active_campaigns: List[str],
                     top_k: int = 5) -> List[Dict]:
        """광고 추천"""
        query = """
        // 사용자 프로필과 캠페인 타겟팅 매칭
        MATCH (u:User {user_id: $user_id})
        MATCH (c:Campaign)-[:CONTAINS]->(a:Ad)
        WHERE c.campaign_id IN $active_campaigns
        
        // 유사한 사용자들의 상호작용 패턴
        OPTIONAL MATCH (u)-[s:SIMILAR_TO]-(similar:User)
        OPTIONAL MATCH (similar)-[r:INTERACTED_WITH]->(a)
        
        WITH u, a, c, 
             avg(s.similarity_score) as similarity_avg,
             sum(CASE WHEN r.interaction_type = 'click' THEN 1 ELSE 0 END) as similar_clicks,
             sum(CASE WHEN r.interaction_type = 'conversion' THEN r.value ELSE 0 END) as similar_conversions
        
        // 사용자 특성과 광고 매칭 점수 계산
        WITH u, a, c, similarity_avg, similar_clicks, similar_conversions,
             CASE 
                WHEN u.age_group IN ['25-34', '35-44'] AND a.target_age CONTAINS u.age_group THEN 0.3
                ELSE 0
             END +
             CASE 
                WHEN any(interest IN u.interests WHERE interest IN a.target_interests) THEN 0.4
                ELSE 0
             END +
             similarity_avg * 0.2 +
             (similar_clicks + similar_conversions) * 0.1 as matching_score
        
        RETURN a.ad_id as ad_id,
               c.campaign_id as campaign_id,
               a.title as ad_title,
               matching_score,
               similar_clicks,
               similar_conversions
        ORDER BY matching_score DESC
        LIMIT $top_k
        """
        
        with self.graph_manager.driver.session() as session:
            result = session.run(query, user_id=user_id, 
                               active_campaigns=active_campaigns, top_k=top_k)
            
            ad_recommendations = []
            for record in result:
                ad_recommendations.append({
                    'ad_id': record['ad_id'],
                    'campaign_id': record['campaign_id'],
                    'ad_title': record['ad_title'],
                    'matching_score': record['matching_score'],
                    'social_signals': {
                        'similar_clicks': record['similar_clicks'],
                        'similar_conversions': record['similar_conversions']
                    }
                })
            
            return ad_recommendations

class FraudDetectionSystem:
    """그래프 기반 사기 탐지 시스템"""
    
    def __init__(self, graph_manager: Neo4jAdGraphManager):
        self.graph_manager = graph_manager
    
    def detect_click_fraud(self, time_window_hours: int = 24) -> List[Dict]:
        """클릭 사기 탐지"""
        query = """
        // 비정상적인 클릭 패턴 탐지
        MATCH (u:User)-[r:INTERACTED_WITH]->(a:Ad)
        WHERE r.interaction_type = 'click'
        AND r.timestamp >= datetime() - duration({hours: $time_window_hours})
        
        WITH u, a, count(r) as click_count,
             collect(r.timestamp) as click_timestamps,
             collect(r.context) as contexts
        
        // 의심 패턴 식별
        WITH u, a, click_count, click_timestamps, contexts,
             // 같은 광고에 과도한 클릭
             CASE WHEN click_count > 50 THEN 1 ELSE 0 END as excessive_clicks,
             // 짧은 시간 내 연속 클릭
             size([t IN click_timestamps WHERE 
                   any(other IN click_timestamps WHERE 
                       abs(duration.between(datetime(t), datetime(other)).seconds) < 10)]) as rapid_clicks,
             // IP 주소 패턴 (context에서)
             size([c IN contexts WHERE c.ip_address IS NOT NULL]) as ip_diversity
        
        WHERE excessive_clicks = 1 OR rapid_clicks > 10
        
        RETURN u.user_id as suspicious_user,
               a.ad_id as targeted_ad,
               click_count,
               excessive_clicks,
               rapid_clicks,
               ip_diversity,
               (excessive_clicks * 0.4 + rapid_clicks/10 * 0.6) as fraud_score
        ORDER BY fraud_score DESC
        """
        
        with self.graph_manager.driver.session() as session:
            result = session.run(query, time_window_hours=time_window_hours)
            
            fraud_cases = []
            for record in result:
                fraud_cases.append({
                    'suspicious_user': record['suspicious_user'],
                    'targeted_ad': record['targeted_ad'],
                    'click_count': record['click_count'],
                    'fraud_indicators': {
                        'excessive_clicks': bool(record['excessive_clicks']),
                        'rapid_clicks': record['rapid_clicks'],
                        'ip_diversity': record['ip_diversity']
                    },
                    'fraud_score': record['fraud_score']
                })
            
            return fraud_cases
    
    def detect_fake_accounts(self) -> List[Dict]:
        """가짜 계정 탐지"""
        query = """
        // 비정상적인 계정 특성 탐지
        MATCH (u:User)
        OPTIONAL MATCH (u)-[r:INTERACTED_WITH]->(a:Ad)
        
        WITH u, 
             count(r) as total_interactions,
             count(DISTINCT a.campaign_id) as unique_campaigns,
             avg(r.value) as avg_interaction_value,
             collect(DISTINCT r.interaction_type) as interaction_types,
             u.registration_date as reg_date,
             u.last_activity as last_activity
        
        // 의심 패턴 계산
        WITH u, total_interactions, unique_campaigns, avg_interaction_value, 
             interaction_types, reg_date, last_activity,
             // 등록 후 즉시 대량 활동
             CASE 
                WHEN duration.between(datetime(reg_date), datetime(last_activity)).days < 1 
                     AND total_interactions > 100 
                THEN 1 ELSE 0 
             END as immediate_high_activity,
             // 비정상적 상호작용 패턴
             CASE WHEN size(interaction_types) = 1 AND 'click' IN interaction_types THEN 1 ELSE 0 END as only_clicks,
             // 가치 없는 상호작용
             CASE WHEN avg_interaction_value = 0 AND total_interactions > 50 THEN 1 ELSE 0 END as zero_value_interactions
        
        WHERE immediate_high_activity = 1 OR only_clicks = 1 OR zero_value_interactions = 1
        
        RETURN u.user_id as suspicious_user,
               total_interactions,
               unique_campaigns,
               avg_interaction_value,
               interaction_types,
               immediate_high_activity,
               only_clicks,
               zero_value_interactions,
               (immediate_high_activity * 0.4 + only_clicks * 0.3 + zero_value_interactions * 0.3) as fake_score
        ORDER BY fake_score DESC
        """
        
        with self.graph_manager.driver.session() as session:
            result = session.run(query)
            
            fake_accounts = []
            for record in result:
                fake_accounts.append({
                    'suspicious_user': record['suspicious_user'],
                    'activity_stats': {
                        'total_interactions': record['total_interactions'],
                        'unique_campaigns': record['unique_campaigns'],
                        'avg_interaction_value': record['avg_interaction_value'],
                        'interaction_types': record['interaction_types']
                    },
                    'fraud_indicators': {
                        'immediate_high_activity': bool(record['immediate_high_activity']),
                        'only_clicks': bool(record['only_clicks']),
                        'zero_value_interactions': bool(record['zero_value_interactions'])
                    },
                    'fake_score': record['fake_score']
                })
            
            return fake_accounts

# 사용 예시
def example_graph_ad_system():
    """그래프 광고 시스템 예시"""
    print("=== Neo4j 그래프 광고 시스템 ===")
    
    # 1. 그래프 관리자 초기화
    try:
        graph_manager = Neo4jAdGraphManager()
    except Exception as e:
        print(f"Neo4j 연결 실패: {e}")
        print("Mock 데이터로 예시 진행...")
        return example_mock_analysis()
    
    # 2. 샘플 데이터 생성
    print("샘플 데이터 생성 중...")
    
    # 사용자 생성
    sample_users = []
    for i in range(100):
        user = User(
            user_id=f"user_{i:05d}",
            demographics={
                'age_group': np.random.choice(['18-24', '25-34', '35-44', '45-54']),
                'gender': np.random.choice(['M', 'F']),
                'income_level': np.random.choice(['low', 'medium', 'high'])
            },
            interests=[f"interest_{j}" for j in np.random.choice(20, 3, replace=False)],
            behavior_score=np.random.uniform(0, 1),
            lifetime_value=np.random.uniform(100, 5000),
            registration_date=datetime.now() - timedelta(days=np.random.randint(1, 365)),
            last_activity=datetime.now() - timedelta(days=np.random.randint(0, 30))
        )
        sample_users.append(user)
        graph_manager.create_user(user)
    
    # 상품 생성
    sample_products = []
    categories = ['electronics', 'fashion', 'home', 'sports']
    brands = ['BrandA', 'BrandB', 'BrandC', 'BrandD']
    
    for i in range(50):
        product = Product(
            product_id=f"prod_{i:03d}",
            name=f"Product {i}",
            category=np.random.choice(categories),
            brand=np.random.choice(brands),
            price=np.random.uniform(10, 1000),
            features=[f"feature_{j}" for j in np.random.choice(10, 2, replace=False)],
            popularity_score=np.random.uniform(0, 1)
        )
        sample_products.append(product)
        graph_manager.create_product(product)
    
    print(f"생성된 사용자: {len(sample_users)}명")
    print(f"생성된 상품: {len(sample_products)}개")
    
    # 3. 고객 여정 분석
    print("\n=== 고객 여정 분석 ===")
    journey_analyzer = CustomerJourneyAnalyzer(graph_manager)
    
    # 샘플 사용자의 여정 분석
    sample_user_id = sample_users[0].user_id
    journey_analysis = journey_analyzer.analyze_conversion_paths(sample_user_id)
    
    print(f"분석 사용자: {sample_user_id}")
    print(f"터치포인트 수: {journey_analysis['touchpoints']}")
    print(f"전환까지 기간: {journey_analysis['time_to_conversion_days']}일")
    
    # 4. 영향력 분석
    print("\n=== 영향력 분석 ===")
    influence_analyzer = InfluenceAnalyzer(graph_manager)
    
    # 영향력자 찾기
    try:
        influencers = influence_analyzer.find_influencers(top_k=5)
        print(f"발견된 영향력자: {len(influencers)}명")
        
        if influencers:
            top_influencer = influencers[0]
            print(f"최고 영향력자: {top_influencer['user_id']} (점수: {top_influencer['influence_score']:.3f})")
    except Exception as e:
        print(f"영향력 분석 오류: {e}")
    
    # 5. 추천 시스템
    print("\n=== 추천 시스템 ===")
    recommendation_engine = RecommendationEngine(graph_manager)
    
    try:
        # 상품 추천
        recommendations = recommendation_engine.recommend_products(sample_user_id, top_k=5)
        print(f"추천된 상품: {len(recommendations)}개")
        
        if recommendations:
            top_recommendation = recommendations[0]
            print(f"최고 추천 상품: {top_recommendation['product_name']} (점수: {top_recommendation['recommendation_score']:.3f})")
    except Exception as e:
        print(f"추천 시스템 오류: {e}")
    
    # 6. 사기 탐지
    print("\n=== 사기 탐지 ===")
    fraud_detector = FraudDetectionSystem(graph_manager)
    
    try:
        # 클릭 사기 탐지
        fraud_cases = fraud_detector.detect_click_fraud(time_window_hours=24)
        print(f"의심 클릭 사기 사례: {len(fraud_cases)}건")
        
        # 가짜 계정 탐지
        fake_accounts = fraud_detector.detect_fake_accounts()
        print(f"의심 가짜 계정: {len(fake_accounts)}개")
    except Exception as e:
        print(f"사기 탐지 오류: {e}")
    
    # 연결 종료
    graph_manager.close()
    
    return {
        'users_created': len(sample_users),
        'products_created': len(sample_products),
        'journey_touchpoints': journey_analysis.get('touchpoints', 0),
        'influencers_found': len(influencers) if 'influencers' in locals() else 0,
        'recommendations_generated': len(recommendations) if 'recommendations' in locals() else 0
    }

def example_mock_analysis():
    """Mock 분석 (Neo4j 없을 때)"""
    print("Mock 그래프 분석 실행...")
    
    # NetworkX로 간단한 그래프 분석
    G = nx.Graph()
    
    # 노드 추가 (사용자)
    users = [f"user_{i:03d}" for i in range(50)]
    G.add_nodes_from(users)
    
    # 랜덤 엣지 추가 (유사성 관계)
    np.random.seed(42)
    for i in range(100):
        u1, u2 = np.random.choice(users, 2, replace=False)
        weight = np.random.uniform(0.3, 1.0)
        G.add_edge(u1, u2, weight=weight)
    
    # 중심성 분석
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    pagerank = nx.pagerank(G)
    
    # 상위 영향력자
    top_users = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
    
    print(f"그래프 노드 수: {G.number_of_nodes()}")
    print(f"그래프 엣지 수: {G.number_of_edges()}")
    print(f"최고 PageRank 사용자: {top_users[0][0]} (점수: {top_users[0][1]:.3f})")
    
    return {
        'users_created': G.number_of_nodes(),
        'relationships_created': G.number_of_edges(),
        'top_influencer_score': top_users[0][1],
        'analysis_type': 'mock_networkx'
    }

if __name__ == "__main__":
    results = example_graph_ad_system()
    print(f"\n그래프 광고 시스템 완료!")
    print(f"생성된 사용자: {results.get('users_created', 0)}명")
    if 'analysis_type' in results:
        print(f"분석 유형: {results['analysis_type']}")
    else:
        print(f"여정 터치포인트: {results.get('journey_touchpoints', 0)}개")
        print(f"발견된 영향력자: {results.get('influencers_found', 0)}명")
```

## 🚀 프로젝트
1. **고객 여정 분석 플랫폼**
2. **실시간 추천 시스템**
3. **소셜 영향력 분석 도구**
4. **그래프 기반 사기 탐지 시스템**