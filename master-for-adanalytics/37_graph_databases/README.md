# 37. Graph Databases - 그래프 데이터베이스

## 📚 과정 소개
Neo4j, Amazon Neptune을 활용한 그래프 데이터베이스로 고객 여정 분석, 추천 시스템, 영향력 분석, 어트리뷰션 모델링을 구현합니다.

## 🎯 학습 목표
- 고객 여정 그래프 모델링
- 그래프 기반 추천 시스템
- 인플루언서 네트워크 분석
- 멀티터치 어트리뷰션

## 📖 주요 내용

### Neo4j 고객 여정 모델링
```python
from neo4j import GraphDatabase
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
import json

class CustomerJourneyGraph:
    """고객 여정 그래프 분석기"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()
    
    def create_customer_journey_schema(self):
        """고객 여정 스키마 생성"""
        with self.driver.session() as session:
            # 인덱스 생성
            session.run("""
                CREATE CONSTRAINT customer_id_unique IF NOT EXISTS 
                FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE
            """)
            
            session.run("""
                CREATE CONSTRAINT touchpoint_id_unique IF NOT EXISTS 
                FOR (t:Touchpoint) REQUIRE t.touchpoint_id IS UNIQUE
            """)
            
            session.run("""
                CREATE INDEX touchpoint_timestamp IF NOT EXISTS 
                FOR (t:Touchpoint) ON (t.timestamp)
            """)
            
            session.run("""
                CREATE INDEX interaction_timestamp IF NOT EXISTS 
                FOR ()-[r:INTERACTED_WITH]-() ON (r.timestamp)
            """)
    
    def add_customer(self, customer_data: Dict):
        """고객 노드 추가"""
        with self.driver.session() as session:
            session.run("""
                MERGE (c:Customer {customer_id: $customer_id})
                SET c.age = $age,
                    c.gender = $gender,
                    c.location = $location,
                    c.segment = $segment,
                    c.lifetime_value = $lifetime_value,
                    c.acquisition_date = datetime($acquisition_date)
            """, **customer_data)
    
    def add_touchpoint(self, touchpoint_data: Dict):
        """터치포인트 노드 추가"""
        with self.driver.session() as session:
            session.run("""
                MERGE (t:Touchpoint {touchpoint_id: $touchpoint_id})
                SET t.type = $type,
                    t.channel = $channel,
                    t.campaign = $campaign,
                    t.content = $content,
                    t.cost = $cost
            """, **touchpoint_data)
    
    def add_interaction(self, interaction_data: Dict):
        """상호작용 관계 추가"""
        with self.driver.session() as session:
            session.run("""
                MATCH (c:Customer {customer_id: $customer_id})
                MATCH (t:Touchpoint {touchpoint_id: $touchpoint_id})
                CREATE (c)-[r:INTERACTED_WITH {
                    timestamp: datetime($timestamp),
                    action_type: $action_type,
                    value: $value,
                    session_id: $session_id,
                    device: $device
                }]->(t)
            """, **interaction_data)
    
    def analyze_customer_paths(self, customer_id: str = None, limit: int = 100) -> List[Dict]:
        """고객 경로 분석"""
        with self.driver.session() as session:
            if customer_id:
                query = """
                    MATCH path = (c:Customer {customer_id: $customer_id})-[r:INTERACTED_WITH*]->(t:Touchpoint)
                    WITH path, relationships(path) as rels
                    UNWIND rels as rel
                    WITH path, rel, startNode(rel) as customer, endNode(rel) as touchpoint
                    ORDER BY rel.timestamp
                    RETURN customer.customer_id as customer_id,
                           collect({
                               touchpoint: touchpoint.touchpoint_id,
                               channel: touchpoint.channel,
                               campaign: touchpoint.campaign,
                               timestamp: rel.timestamp,
                               action_type: rel.action_type,
                               value: rel.value
                           }) as journey
                """
                result = session.run(query, customer_id=customer_id)
            else:
                query = """
                    MATCH (c:Customer)-[r:INTERACTED_WITH]->(t:Touchpoint)
                    WITH c, collect({
                        touchpoint: t.touchpoint_id,
                        channel: t.channel,
                        campaign: t.campaign,
                        timestamp: r.timestamp,
                        action_type: r.action_type,
                        value: r.value
                    }) as interactions
                    WHERE size(interactions) > 1
                    RETURN c.customer_id as customer_id,
                           [i in interactions | i ORDER BY i.timestamp] as journey
                    LIMIT $limit
                """
                result = session.run(query, limit=limit)
            
            return [record.data() for record in result]
    
    def find_conversion_paths(self, min_path_length: int = 2) -> List[Dict]:
        """전환 경로 분석"""
        with self.driver.session() as session:
            query = """
                MATCH path = (c:Customer)-[r:INTERACTED_WITH*2..10]->(t:Touchpoint)
                WHERE ANY(rel in relationships(path) WHERE rel.action_type = 'conversion')
                WITH path, relationships(path) as rels, nodes(path) as touchpoints
                WITH path, 
                     [rel in rels | {
                         channel: endNode(rel).channel,
                         campaign: endNode(rel).campaign,
                         timestamp: rel.timestamp,
                         action_type: rel.action_type,
                         value: rel.value
                     }] as journey_steps
                WHERE size(journey_steps) >= $min_path_length
                RETURN journey_steps,
                       size(journey_steps) as path_length,
                       reduce(total = 0, step in journey_steps | 
                              total + CASE WHEN step.action_type = 'conversion' 
                                          THEN step.value ELSE 0 END) as conversion_value
                ORDER BY conversion_value DESC
                LIMIT 100
            """
            
            result = session.run(query, min_path_length=min_path_length)
            return [record.data() for record in result]
    
    def calculate_channel_attribution(self, model: str = 'first_touch') -> List[Dict]:
        """채널 어트리뷰션 계산"""
        with self.driver.session() as session:
            if model == 'first_touch':
                query = """
                    MATCH (c:Customer)-[r:INTERACTED_WITH]->(t:Touchpoint)
                    WHERE r.action_type = 'conversion'
                    WITH c, r, t
                    MATCH (c)-[first:INTERACTED_WITH]->(first_touch:Touchpoint)
                    WHERE first.timestamp <= r.timestamp
                    WITH c, r, first_touch, first.timestamp as first_time
                    ORDER BY first_time
                    WITH c, r, collect(first_touch)[0] as attribution_touchpoint
                    RETURN attribution_touchpoint.channel as channel,
                           count(*) as conversions,
                           sum(r.value) as total_value
                    ORDER BY total_value DESC
                """
            elif model == 'last_touch':
                query = """
                    MATCH (c:Customer)-[r:INTERACTED_WITH]->(t:Touchpoint)
                    WHERE r.action_type = 'conversion'
                    WITH c, r, t
                    MATCH (c)-[last:INTERACTED_WITH]->(last_touch:Touchpoint)
                    WHERE last.timestamp <= r.timestamp
                    WITH c, r, last_touch, last.timestamp as last_time
                    ORDER BY last_time DESC
                    WITH c, r, collect(last_touch)[0] as attribution_touchpoint
                    RETURN attribution_touchpoint.channel as channel,
                           count(*) as conversions,
                           sum(r.value) as total_value
                    ORDER BY total_value DESC
                """
            else:  # linear attribution
                query = """
                    MATCH path = (c:Customer)-[r:INTERACTED_WITH*]->(conv_touchpoint:Touchpoint)
                    WHERE ANY(rel in relationships(path) WHERE rel.action_type = 'conversion')
                    WITH path, relationships(path) as rels,
                         [rel in relationships(path) WHERE rel.action_type = 'conversion'][0] as conv_rel
                    WITH path, rels, conv_rel, size(rels) as path_length
                    UNWIND rels as rel
                    WITH conv_rel, rel, endNode(rel) as touchpoint, path_length
                    WHERE rel.timestamp <= conv_rel.timestamp
                    RETURN touchpoint.channel as channel,
                           count(*) as interactions,
                           sum(conv_rel.value / path_length) as attributed_value
                    ORDER BY attributed_value DESC
                """
            
            result = session.run(query)
            return [record.data() for record in result]

class RecommendationEngine:
    """그래프 기반 추천 엔진"""
    
    def __init__(self, driver):
        self.driver = driver
    
    def create_recommendation_schema(self):
        """추천 스키마 생성"""
        with self.driver.session() as session:
            # 제품 노드
            session.run("""
                CREATE CONSTRAINT product_id_unique IF NOT EXISTS 
                FOR (p:Product) REQUIRE p.product_id IS UNIQUE
            """)
            
            # 카테고리 노드
            session.run("""
                CREATE CONSTRAINT category_id_unique IF NOT EXISTS 
                FOR (cat:Category) REQUIRE cat.category_id IS UNIQUE
            """)
    
    def add_product_data(self, product_data: Dict):
        """제품 데이터 추가"""
        with self.driver.session() as session:
            # 제품 노드 생성
            session.run("""
                MERGE (p:Product {product_id: $product_id})
                SET p.name = $name,
                    p.price = $price,
                    p.rating = $rating,
                    p.brand = $brand
            """, **product_data)
            
            # 카테고리 관계 생성
            if 'categories' in product_data:
                for category in product_data['categories']:
                    session.run("""
                        MERGE (cat:Category {category_id: $category_id})
                        SET cat.name = $category_name
                        WITH cat
                        MATCH (p:Product {product_id: $product_id})
                        MERGE (p)-[:BELONGS_TO]->(cat)
                    """, 
                    product_id=product_data['product_id'],
                    category_id=category['id'],
                    category_name=category['name'])
    
    def add_customer_behavior(self, behavior_data: Dict):
        """고객 행동 데이터 추가"""
        with self.driver.session() as session:
            session.run("""
                MATCH (c:Customer {customer_id: $customer_id})
                MATCH (p:Product {product_id: $product_id})
                MERGE (c)-[r:INTERACTED {
                    action: $action,
                    timestamp: datetime($timestamp),
                    rating: $rating,
                    session_id: $session_id
                }]->(p)
            """, **behavior_data)
    
    def get_collaborative_recommendations(self, customer_id: str, limit: int = 10) -> List[Dict]:
        """협업 필터링 추천"""
        with self.driver.session() as session:
            query = """
                // 유사한 고객 찾기
                MATCH (target:Customer {customer_id: $customer_id})-[r1:INTERACTED]->(p:Product)
                WHERE r1.action IN ['purchase', 'like', 'view']
                WITH target, collect(DISTINCT p) as target_products
                
                MATCH (other:Customer)-[r2:INTERACTED]->(shared:Product)
                WHERE other <> target AND shared IN target_products
                  AND r2.action IN ['purchase', 'like', 'view']
                WITH target, other, 
                     size([p in target_products WHERE (other)-[:INTERACTED]->(p)]) as shared_count,
                     size(target_products) as target_count
                WHERE shared_count > 1
                WITH target, other, 
                     toFloat(shared_count) / target_count as similarity
                ORDER BY similarity DESC
                LIMIT 50
                
                // 유사 고객이 좋아한 제품 추천
                MATCH (other)-[r3:INTERACTED]->(rec:Product)
                WHERE r3.action IN ['purchase', 'like'] 
                  AND NOT (target)-[:INTERACTED]->(rec)
                WITH rec, sum(similarity * CASE 
                              WHEN r3.action = 'purchase' THEN 2 
                              ELSE 1 END) as score,
                     count(DISTINCT other) as supporter_count
                WHERE supporter_count >= 2
                RETURN rec.product_id as product_id,
                       rec.name as product_name,
                       rec.price as price,
                       score,
                       supporter_count
                ORDER BY score DESC
                LIMIT $limit
            """
            
            result = session.run(query, customer_id=customer_id, limit=limit)
            return [record.data() for record in result]
    
    def get_content_based_recommendations(self, customer_id: str, limit: int = 10) -> List[Dict]:
        """컨텐츠 기반 추천"""
        with self.driver.session() as session:
            query = """
                // 고객이 선호하는 카테고리/브랜드 분석
                MATCH (c:Customer {customer_id: $customer_id})-[r:INTERACTED]->(p:Product)
                WHERE r.action IN ['purchase', 'like']
                WITH c, p, r
                MATCH (p)-[:BELONGS_TO]->(cat:Category)
                WITH c, cat, p.brand as brand, count(*) as interaction_count,
                     avg(CASE WHEN r.rating IS NOT NULL THEN r.rating ELSE 4.0 END) as avg_rating
                WITH c, cat, brand, interaction_count, avg_rating,
                     interaction_count * avg_rating as preference_score
                ORDER BY preference_score DESC
                LIMIT 5
                
                // 선호 카테고리/브랜드의 다른 제품 추천
                WITH c, collect({category: cat, brand: brand, score: preference_score}) as preferences
                UNWIND preferences as pref
                MATCH (rec:Product)-[:BELONGS_TO]->(pref.category)
                WHERE rec.brand = pref.brand 
                  AND NOT (c)-[:INTERACTED]->(rec)
                  AND rec.rating > 3.5
                WITH rec, pref.score as category_score,
                     rec.rating as product_rating
                RETURN rec.product_id as product_id,
                       rec.name as product_name,
                       rec.price as price,
                       rec.rating as rating,
                       category_score * product_rating as recommendation_score
                ORDER BY recommendation_score DESC
                LIMIT $limit
            """
            
            result = session.run(query, customer_id=customer_id, limit=limit)
            return [record.data() for record in result]

class InfluencerNetworkAnalysis:
    """인플루언서 네트워크 분석"""
    
    def __init__(self, driver):
        self.driver = driver
    
    def create_social_schema(self):
        """소셜 네트워크 스키마 생성"""
        with self.driver.session() as session:
            session.run("""
                CREATE CONSTRAINT influencer_id_unique IF NOT EXISTS 
                FOR (i:Influencer) REQUIRE i.influencer_id IS UNIQUE
            """)
            
            session.run("""
                CREATE INDEX influencer_followers IF NOT EXISTS 
                FOR (i:Influencer) ON (i.followers)
            """)
    
    def add_influencer(self, influencer_data: Dict):
        """인플루언서 추가"""
        with self.driver.session() as session:
            session.run("""
                MERGE (i:Influencer {influencer_id: $influencer_id})
                SET i.name = $name,
                    i.platform = $platform,
                    i.followers = $followers,
                    i.engagement_rate = $engagement_rate,
                    i.category = $category,
                    i.location = $location,
                    i.cost_per_post = $cost_per_post
            """, **influencer_data)
    
    def add_collaboration(self, collab_data: Dict):
        """협업 관계 추가"""
        with self.driver.session() as session:
            session.run("""
                MATCH (i:Influencer {influencer_id: $influencer_id})
                MATCH (b:Brand {brand_id: $brand_id})
                CREATE (i)-[c:COLLABORATED_WITH {
                    campaign_id: $campaign_id,
                    start_date: date($start_date),
                    end_date: date($end_date),
                    cost: $cost,
                    reach: $reach,
                    engagement: $engagement,
                    conversions: $conversions
                }]->(b)
            """, **collab_data)
    
    def find_top_influencers(self, category: str = None, min_followers: int = 10000) -> List[Dict]:
        """상위 인플루언서 찾기"""
        with self.driver.session() as session:
            if category:
                query = """
                    MATCH (i:Influencer)
                    WHERE i.category = $category AND i.followers >= $min_followers
                    WITH i, i.followers * i.engagement_rate as influence_score
                    RETURN i.influencer_id as influencer_id,
                           i.name as name,
                           i.platform as platform,
                           i.followers as followers,
                           i.engagement_rate as engagement_rate,
                           influence_score,
                           i.cost_per_post as cost_per_post,
                           influence_score / i.cost_per_post as roi_estimate
                    ORDER BY influence_score DESC
                    LIMIT 20
                """
                result = session.run(query, category=category, min_followers=min_followers)
            else:
                query = """
                    MATCH (i:Influencer)
                    WHERE i.followers >= $min_followers
                    WITH i, i.followers * i.engagement_rate as influence_score
                    RETURN i.influencer_id as influencer_id,
                           i.name as name,
                           i.platform as platform,
                           i.category as category,
                           i.followers as followers,
                           i.engagement_rate as engagement_rate,
                           influence_score,
                           i.cost_per_post as cost_per_post,
                           influence_score / i.cost_per_post as roi_estimate
                    ORDER BY influence_score DESC
                    LIMIT 20
                """
                result = session.run(query, min_followers=min_followers)
            
            return [record.data() for record in result]
    
    def analyze_network_centrality(self) -> List[Dict]:
        """네트워크 중심성 분석"""
        with self.driver.session() as session:
            # PageRank 알고리즘 실행
            session.run("""
                CALL gds.pageRank.write('influencer-network', {
                    writeProperty: 'pagerank',
                    relationshipTypes: ['FOLLOWS', 'MENTIONS']
                })
            """)
            
            # 중심성 결과 조회
            query = """
                MATCH (i:Influencer)
                WHERE i.pagerank IS NOT NULL
                RETURN i.influencer_id as influencer_id,
                       i.name as name,
                       i.followers as followers,
                       i.pagerank as centrality_score
                ORDER BY i.pagerank DESC
                LIMIT 20
            """
            
            result = session.run(query)
            return [record.data() for record in result]

class AttributionModeling:
    """그래프 기반 어트리뷰션 모델링"""
    
    def __init__(self, driver):
        self.driver = driver
    
    def shapley_value_attribution(self, customer_id: str) -> Dict:
        """샤플리 값 기반 어트리뷰션"""
        with self.driver.session() as session:
            # 고객의 전환 경로 조회
            query = """
                MATCH path = (c:Customer {customer_id: $customer_id})-[r:INTERACTED_WITH*]->(t:Touchpoint)
                WHERE ANY(rel in relationships(path) WHERE rel.action_type = 'conversion')
                WITH relationships(path) as rels,
                     [rel in relationships(path) WHERE rel.action_type = 'conversion'][0] as conv_rel
                WITH rels, conv_rel, size(rels) as path_length
                UNWIND range(0, path_length-1) as i
                WITH rels[i] as rel, endNode(rels[i]) as touchpoint, conv_rel, path_length, i
                WHERE rel.timestamp <= conv_rel.timestamp
                RETURN collect({
                    position: i,
                    channel: touchpoint.channel,
                    campaign: touchpoint.campaign,
                    timestamp: rel.timestamp
                }) as journey_touchpoints,
                conv_rel.value as conversion_value
            """
            
            result = session.run(query, customer_id=customer_id)
            record = result.single()
            
            if not record:
                return {}
            
            touchpoints = record['journey_touchpoints']
            conversion_value = record['conversion_value']
            
            # 샤플리 값 계산
            shapley_values = self._calculate_shapley_values(touchpoints, conversion_value)
            
            return {
                'customer_id': customer_id,
                'conversion_value': conversion_value,
                'attribution': shapley_values,
                'path_length': len(touchpoints)
            }
    
    def _calculate_shapley_values(self, touchpoints: List[Dict], conversion_value: float) -> Dict:
        """샤플리 값 계산"""
        import itertools
        from math import factorial
        
        n = len(touchpoints)
        channels = [tp['channel'] for tp in touchpoints]
        unique_channels = list(set(channels))
        
        shapley_values = {channel: 0.0 for channel in unique_channels}
        
        # 모든 순열에 대해 기여도 계산
        for permutation in itertools.permutations(range(n)):
            marginal_contributions = {}
            
            for i, touchpoint_idx in enumerate(permutation):
                channel = channels[touchpoint_idx]
                
                # 이전 터치포인트들 없이의 가치
                prev_channels = set(channels[permutation[j]] for j in range(i))
                
                # 현재 터치포인트 포함한 가치
                curr_channels = prev_channels | {channel}
                
                # 기여도 = 포함 후 가치 - 포함 전 가치
                marginal_contribution = self._estimate_conversion_probability(curr_channels) - \
                                      self._estimate_conversion_probability(prev_channels)
                
                marginal_contributions[channel] = marginal_contribution * conversion_value
            
            # 각 채널의 샤플리 값에 기여도 추가
            for channel, contribution in marginal_contributions.items():
                shapley_values[channel] += contribution / factorial(n)
        
        return shapley_values
    
    def _estimate_conversion_probability(self, channels: set) -> float:
        """채널 조합의 전환 확률 추정 (간단한 모델)"""
        if not channels:
            return 0.0
        
        # 채널별 기본 전환율 (실제로는 데이터 기반)
        channel_rates = {
            'google_ads': 0.15,
            'facebook_ads': 0.12,
            'email': 0.08,
            'organic_search': 0.20,
            'direct': 0.25
        }
        
        # 결합 효과 고려 (간단한 모델)
        combined_rate = 1.0
        for channel in channels:
            rate = channel_rates.get(channel, 0.05)
            combined_rate *= (1 - rate)
        
        return 1 - combined_rate
```

## 🚀 프로젝트
1. **고객 여정 분석 플랫폼**
2. **그래프 기반 추천 시스템**
3. **인플루언서 네트워크 분석**
4. **멀티터치 어트리뷰션 모델링**