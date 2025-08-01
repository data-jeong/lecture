# 24. Elasticsearch Search - 검색 엔진

## 📚 과정 소개
광고 도메인에 특화된 Elasticsearch 검색 시스템을 마스터합니다. 대용량 광고 로그 검색, 실시간 분석, 키워드 트렌드 분석, 경쟁사 모니터링까지 포괄적으로 다룹니다.

## 🎯 학습 목표
- 대규모 광고 데이터 인덱싱
- 복잡한 검색 쿼리 최적화
- 실시간 광고 성과 모니터링
- Kibana 대시보드 구축

## 📖 주요 내용

### 광고 검색 시스템
```python
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import logging
from dataclasses import dataclass, asdict
import asyncio
from collections import defaultdict
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AdDocument:
    """광고 문서 클래스"""
    ad_id: str
    campaign_id: str
    ad_group_id: str
    title: str
    description: str
    keywords: List[str]
    landing_page_url: str
    advertiser: str
    industry: str
    target_audience: Dict[str, Any]
    creative_type: str
    ad_format: str
    bid_amount: float
    daily_budget: float
    impressions: int
    clicks: int
    conversions: int
    cost: float
    revenue: float
    ctr: float
    cvr: float
    roas: float
    quality_score: float
    relevance_score: float
    timestamp: datetime
    geography: List[str]
    devices: List[str]
    placements: List[str]

@dataclass
class SearchQuery:
    """검색 쿼리 클래스"""
    query_text: str
    filters: Dict[str, Any]
    sort_by: List[Dict[str, str]]
    aggregations: Dict[str, Any]
    size: int = 100
    from_: int = 0

class ElasticsearchAdManager:
    """Elasticsearch 광고 관리자"""
    
    def __init__(self, hosts: List[str] = ['localhost:9200']):
        self.es = Elasticsearch(hosts)
        self.index_name = 'ad_analytics'
        self.setup_index()
        
    def setup_index(self):
        """인덱스 설정"""
        # 인덱스 매핑 정의
        mapping = {
            "mappings": {
                "properties": {
                    "ad_id": {"type": "keyword"},
                    "campaign_id": {"type": "keyword"},
                    "ad_group_id": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "suggest": {"type": "completion"}
                        }
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "keywords": {
                        "type": "text",
                        "analyzer": "keyword_analyzer"
                    },
                    "landing_page_url": {"type": "keyword"},
                    "advertiser": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}}
                    },
                    "industry": {"type": "keyword"},
                    "target_audience": {
                        "properties": {
                            "age_range": {"type": "keyword"},
                            "gender": {"type": "keyword"},
                            "interests": {"type": "keyword"},
                            "behavior": {"type": "keyword"}
                        }
                    },
                    "creative_type": {"type": "keyword"},
                    "ad_format": {"type": "keyword"},
                    "bid_amount": {"type": "float"},
                    "daily_budget": {"type": "float"},
                    "impressions": {"type": "long"},
                    "clicks": {"type": "long"},
                    "conversions": {"type": "long"},
                    "cost": {"type": "float"},
                    "revenue": {"type": "float"},
                    "ctr": {"type": "float"},
                    "cvr": {"type": "float"},
                    "roas": {"type": "float"},
                    "quality_score": {"type": "float"},
                    "relevance_score": {"type": "float"},
                    "timestamp": {"type": "date"},
                    "geography": {"type": "keyword"},
                    "devices": {"type": "keyword"},
                    "placements": {"type": "keyword"}
                }
            },
            "settings": {
                "analysis": {
                    "analyzer": {
                        "keyword_analyzer": {
                            "type": "custom",
                            "tokenizer": "keyword",
                            "filter": ["lowercase", "trim"]
                        }
                    }
                }
            }
        }
        
        # 인덱스 생성 (존재하지 않는 경우)
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name, body=mapping)
            logger.info(f"Index {self.index_name} created")
    
    def index_ad_document(self, ad_doc: AdDocument) -> Dict[str, Any]:
        """광고 문서 인덱싱"""
        doc_dict = asdict(ad_doc)
        doc_dict['timestamp'] = ad_doc.timestamp.isoformat()
        
        try:
            response = self.es.index(
                index=self.index_name,
                id=ad_doc.ad_id,
                body=doc_dict
            )
            logger.info(f"Indexed ad document: {ad_doc.ad_id}")
            return response
        except Exception as e:
            logger.error(f"Error indexing document {ad_doc.ad_id}: {e}")
            return {}
    
    def bulk_index_ads(self, ad_docs: List[AdDocument]) -> Dict[str, Any]:
        """대량 광고 문서 인덱싱"""
        actions = []
        
        for ad_doc in ad_docs:
            doc_dict = asdict(ad_doc)
            doc_dict['timestamp'] = ad_doc.timestamp.isoformat()
            
            action = {
                "_index": self.index_name,
                "_id": ad_doc.ad_id,
                "_source": doc_dict
            }
            actions.append(action)
        
        try:
            success, failed = bulk(self.es, actions)
            logger.info(f"Bulk indexed {success} documents, {len(failed)} failed")
            return {"success": success, "failed": failed}
        except Exception as e:
            logger.error(f"Error in bulk indexing: {e}")
            return {"success": 0, "failed": len(ad_docs)}

class AdSearchEngine:
    """광고 검색 엔진"""
    
    def __init__(self, es_manager: ElasticsearchAdManager):
        self.es_manager = es_manager
        self.es = es_manager.es
        self.index_name = es_manager.index_name
    
    def search_ads(self, search_query: SearchQuery) -> Dict[str, Any]:
        """광고 검색"""
        query_body = self._build_query(search_query)
        
        try:
            response = self.es.search(
                index=self.index_name,
                body=query_body,
                size=search_query.size,
                from_=search_query.from_
            )
            
            return self._format_search_results(response)
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {"hits": [], "total": 0, "aggregations": {}}
    
    def _build_query(self, search_query: SearchQuery) -> Dict[str, Any]:
        """검색 쿼리 구성"""
        query_body = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": [],
                    "should": [],
                    "must_not": []
                }
            }
        }
        
        # 텍스트 검색
        if search_query.query_text:
            text_query = {
                "multi_match": {
                    "query": search_query.query_text,
                    "fields": [
                        "title^3",
                        "description^2", 
                        "keywords^2",
                        "advertiser"
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            }
            query_body["query"]["bool"]["must"].append(text_query)
        
        # 필터 적용
        for field, value in search_query.filters.items():
            if isinstance(value, list):
                filter_query = {"terms": {field: value}}
            elif isinstance(value, dict):
                if "gte" in value or "lte" in value:
                    filter_query = {"range": {field: value}}
                else:
                    filter_query = {"term": {field: value}}
            else:
                filter_query = {"term": {field: value}}
            
            query_body["query"]["bool"]["filter"].append(filter_query)
        
        # 정렬
        if search_query.sort_by:
            query_body["sort"] = search_query.sort_by
        
        # 집계
        if search_query.aggregations:
            query_body["aggs"] = search_query.aggregations
        
        return query_body
    
    def _format_search_results(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """검색 결과 포맷팅"""
        hits = []
        
        for hit in response['hits']['hits']:
            formatted_hit = {
                "id": hit["_id"],
                "score": hit["_score"],
                "source": hit["_source"]
            }
            hits.append(formatted_hit)
        
        return {
            "hits": hits,
            "total": response['hits']['total']['value'],
            "max_score": response['hits']['max_score'],
            "aggregations": response.get('aggregations', {}),
            "took": response['took']
        }
    
    def find_similar_ads(self, ad_id: str, size: int = 10) -> Dict[str, Any]:
        """유사 광고 찾기"""
        # 원본 광고 가져오기
        try:
            original_ad = self.es.get(index=self.index_name, id=ad_id)
            source = original_ad['_source']
            
            # More Like This 쿼리
            mlt_query = {
                "query": {
                    "more_like_this": {
                        "fields": ["title", "description", "keywords"],
                        "like": [
                            {
                                "_index": self.index_name,
                                "_id": ad_id
                            }
                        ],
                        "min_term_freq": 1,
                        "max_query_terms": 20,
                        "min_doc_freq": 1
                    }
                },
                "size": size
            }
            
            response = self.es.search(index=self.index_name, body=mlt_query)
            return self._format_search_results(response)
            
        except Exception as e:
            logger.error(f"Error finding similar ads: {e}")
            return {"hits": [], "total": 0}
    
    def get_keyword_suggestions(self, prefix: str, size: int = 10) -> List[str]:
        """키워드 자동완성"""
        suggest_query = {
            "suggest": {
                "keyword_suggest": {
                    "prefix": prefix,
                    "completion": {
                        "field": "title.suggest",
                        "size": size
                    }
                }
            }
        }
        
        try:
            response = self.es.search(index=self.index_name, body=suggest_query)
            suggestions = []
            
            for suggestion in response['suggest']['keyword_suggest']:
                for option in suggestion['options']:
                    suggestions.append(option['text'])
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            return []

class AdAnalyticsEngine:
    """광고 분석 엔진"""
    
    def __init__(self, es_manager: ElasticsearchAdManager):
        self.es_manager = es_manager
        self.es = es_manager.es
        self.index_name = es_manager.index_name
    
    def analyze_campaign_performance(self, date_range: Dict[str, str],
                                   group_by: str = "campaign_id") -> Dict[str, Any]:
        """캠페인 성과 분석"""
        query = {
            "query": {
                "range": {
                    "timestamp": {
                        "gte": date_range["start"],
                        "lte": date_range["end"]
                    }
                }
            },
            "aggs": {
                "performance_by_group": {
                    "terms": {
                        "field": group_by,
                        "size": 100
                    },
                    "aggs": {
                        "total_impressions": {"sum": {"field": "impressions"}},
                        "total_clicks": {"sum": {"field": "clicks"}},
                        "total_conversions": {"sum": {"field": "conversions"}},
                        "total_cost": {"sum": {"field": "cost"}},
                        "total_revenue": {"sum": {"field": "revenue"}},
                        "avg_ctr": {"avg": {"field": "ctr"}},
                        "avg_cvr": {"avg": {"field": "cvr"}},
                        "avg_roas": {"avg": {"field": "roas"}},
                        "performance_trend": {
                            "date_histogram": {
                                "field": "timestamp",
                                "calendar_interval": "day"
                            },
                            "aggs": {
                                "daily_impressions": {"sum": {"field": "impressions"}},
                                "daily_clicks": {"sum": {"field": "clicks"}},
                                "daily_cost": {"sum": {"field": "cost"}}
                            }
                        }
                    }
                }
            },
            "size": 0
        }
        
        try:
            response = self.es.search(index=self.index_name, body=query)
            return self._format_performance_analysis(response)
        except Exception as e:
            logger.error(f"Error in performance analysis: {e}")
            return {}
    
    def analyze_keyword_trends(self, time_period: str = "30d") -> Dict[str, Any]:
        """키워드 트렌드 분석"""
        query = {
            "query": {
                "range": {
                    "timestamp": {
                        "gte": f"now-{time_period}"
                    }
                }
            },
            "aggs": {
                "keyword_performance": {
                    "terms": {
                        "field": "keywords",
                        "size": 50
                    },
                    "aggs": {
                        "avg_ctr": {"avg": {"field": "ctr"}},
                        "avg_cvr": {"avg": {"field": "cvr"}},
                        "total_impressions": {"sum": {"field": "impressions"}},
                        "trend": {
                            "date_histogram": {
                                "field": "timestamp",
                                "calendar_interval": "day"
                            },
                            "aggs": {
                                "daily_impressions": {"sum": {"field": "impressions"}}
                            }
                        }
                    }
                },
                "trending_keywords": {
                    "significant_terms": {
                        "field": "keywords",
                        "background_filter": {
                            "range": {
                                "timestamp": {
                                    "gte": f"now-{int(time_period[:-1])*2}d"
                                }
                            }
                        }
                    }
                }
            },
            "size": 0
        }
        
        try:
            response = self.es.search(index=self.index_name, body=query)
            return self._format_keyword_analysis(response)
        except Exception as e:
            logger.error(f"Error in keyword analysis: {e}")
            return {}
    
    def analyze_audience_segments(self) -> Dict[str, Any]:
        """오디언스 세그먼트 분석"""
        query = {
            "aggs": {
                "age_performance": {
                    "terms": {"field": "target_audience.age_range"},
                    "aggs": {
                        "avg_ctr": {"avg": {"field": "ctr"}},
                        "avg_cvr": {"avg": {"field": "cvr"}},
                        "avg_roas": {"avg": {"field": "roas"}}
                    }
                },
                "gender_performance": {
                    "terms": {"field": "target_audience.gender"},
                    "aggs": {
                        "avg_ctr": {"avg": {"field": "ctr"}},
                        "avg_cvr": {"avg": {"field": "cvr"}},
                        "avg_roas": {"avg": {"field": "roas"}}
                    }
                },
                "interest_performance": {
                    "terms": {"field": "target_audience.interests", "size": 20},
                    "aggs": {
                        "avg_ctr": {"avg": {"field": "ctr"}},
                        "avg_cvr": {"avg": {"field": "cvr"}},
                        "total_revenue": {"sum": {"field": "revenue"}}
                    }
                },
                "device_performance": {
                    "terms": {"field": "devices"},
                    "aggs": {
                        "avg_ctr": {"avg": {"field": "ctr"}},
                        "avg_cvr": {"avg": {"field": "cvr"}},
                        "device_trend": {
                            "date_histogram": {
                                "field": "timestamp",
                                "calendar_interval": "day"
                            },
                            "aggs": {
                                "daily_conversions": {"sum": {"field": "conversions"}}
                            }
                        }
                    }
                }
            },
            "size": 0
        }
        
        try:
            response = self.es.search(index=self.index_name, body=query)
            return self._format_audience_analysis(response)
        except Exception as e:
            logger.error(f"Error in audience analysis: {e}")
            return {}
    
    def _format_performance_analysis(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """성과 분석 결과 포맷팅"""
        results = {}
        
        for bucket in response['aggregations']['performance_by_group']['buckets']:
            group_id = bucket['key']
            
            results[group_id] = {
                'impressions': bucket['total_impressions']['value'],
                'clicks': bucket['total_clicks']['value'],
                'conversions': bucket['total_conversions']['value'],
                'cost': bucket['total_cost']['value'],
                'revenue': bucket['total_revenue']['value'],
                'avg_ctr': bucket['avg_ctr']['value'],
                'avg_cvr': bucket['avg_cvr']['value'],
                'avg_roas': bucket['avg_roas']['value'],
                'trend': [
                    {
                        'date': trend_bucket['key_as_string'],
                        'impressions': trend_bucket['daily_impressions']['value'],
                        'clicks': trend_bucket['daily_clicks']['value'],
                        'cost': trend_bucket['daily_cost']['value']
                    }
                    for trend_bucket in bucket['performance_trend']['buckets']
                ]
            }
        
        return results
    
    def _format_keyword_analysis(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """키워드 분석 결과 포맷팅"""
        keyword_performance = {}
        trending_keywords = []
        
        # 키워드 성과
        for bucket in response['aggregations']['keyword_performance']['buckets']:
            keyword = bucket['key']
            keyword_performance[keyword] = {
                'avg_ctr': bucket['avg_ctr']['value'],
                'avg_cvr': bucket['avg_cvr']['value'],
                'total_impressions': bucket['total_impressions']['value'],
                'trend': [
                    {
                        'date': trend_bucket['key_as_string'],
                        'impressions': trend_bucket['daily_impressions']['value']
                    }
                    for trend_bucket in bucket['trend']['buckets']
                ]
            }
        
        # 트렌딩 키워드
        for bucket in response['aggregations']['trending_keywords']['buckets']:
            trending_keywords.append({
                'keyword': bucket['key'],
                'score': bucket['score'],
                'doc_count': bucket['doc_count']
            })
        
        return {
            'keyword_performance': keyword_performance,
            'trending_keywords': trending_keywords
        }
    
    def _format_audience_analysis(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """오디언스 분석 결과 포맷팅"""
        return {
            'age_performance': {
                bucket['key']: {
                    'avg_ctr': bucket['avg_ctr']['value'],
                    'avg_cvr': bucket['avg_cvr']['value'],
                    'avg_roas': bucket['avg_roas']['value']
                }
                for bucket in response['aggregations']['age_performance']['buckets']
            },
            'gender_performance': {
                bucket['key']: {
                    'avg_ctr': bucket['avg_ctr']['value'],
                    'avg_cvr': bucket['avg_cvr']['value'],
                    'avg_roas': bucket['avg_roas']['value']
                }
                for bucket in response['aggregations']['gender_performance']['buckets']
            },
            'interest_performance': {
                bucket['key']: {
                    'avg_ctr': bucket['avg_ctr']['value'],
                    'avg_cvr': bucket['avg_cvr']['value'],
                    'total_revenue': bucket['total_revenue']['value']
                }
                for bucket in response['aggregations']['interest_performance']['buckets']
            },
            'device_performance': {
                bucket['key']: {
                    'avg_ctr': bucket['avg_ctr']['value'],
                    'avg_cvr': bucket['avg_cvr']['value'],
                    'trend': [
                        {
                            'date': trend_bucket['key_as_string'],
                            'conversions': trend_bucket['daily_conversions']['value']
                        }
                        for trend_bucket in bucket['device_trend']['buckets']
                    ]
                }
                for bucket in response['aggregations']['device_performance']['buckets']
            }
        }

class CompetitorMonitoringSystem:
    """경쟁사 모니터링 시스템"""
    
    def __init__(self, es_manager: ElasticsearchAdManager):
        self.es_manager = es_manager
        self.es = es_manager.es
        self.index_name = es_manager.index_name
        self.competitor_index = "competitor_ads"
        self.setup_competitor_index()
    
    def setup_competitor_index(self):
        """경쟁사 인덱스 설정"""
        mapping = {
            "mappings": {
                "properties": {
                    "competitor_name": {"type": "keyword"},
                    "ad_content": {"type": "text", "analyzer": "standard"},
                    "keywords": {"type": "text"},
                    "bid_estimate": {"type": "float"},
                    "ad_position": {"type": "integer"},
                    "detected_at": {"type": "date"},
                    "industry": {"type": "keyword"},
                    "ad_format": {"type": "keyword"},
                    "landing_page": {"type": "keyword"},
                    "creative_elements": {"type": "nested"}
                }
            }
        }
        
        if not self.es.indices.exists(index=self.competitor_index):
            self.es.indices.create(index=self.competitor_index, body=mapping)
            logger.info(f"Competitor index {self.competitor_index} created")
    
    def monitor_competitor_keywords(self, keywords: List[str], 
                                  competitors: List[str]) -> Dict[str, Any]:
        """경쟁사 키워드 모니터링"""
        monitoring_results = {}
        
        for keyword in keywords:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"keywords": keyword}},
                            {"terms": {"advertiser": competitors}}
                        ]
                    }
                },
                "aggs": {
                    "competitor_activity": {
                        "terms": {"field": "advertiser"},
                        "aggs": {
                            "avg_bid": {"avg": {"field": "bid_amount"}},
                            "total_impressions": {"sum": {"field": "impressions"}},
                            "avg_position": {"avg": {"field": "ad_position"}},
                            "recent_ads": {
                                "top_hits": {
                                    "sort": [{"timestamp": {"order": "desc"}}],
                                    "size": 3
                                }
                            }
                        }
                    }
                },
                "size": 0
            }
            
            try:
                response = self.es.search(index=self.index_name, body=query)
                monitoring_results[keyword] = self._format_competitor_analysis(response)
            except Exception as e:
                logger.error(f"Error monitoring keyword {keyword}: {e}")
                monitoring_results[keyword] = {}
        
        return monitoring_results
    
    def analyze_competitor_strategies(self, competitor: str,
                                    time_range: Dict[str, str]) -> Dict[str, Any]:
        """경쟁사 전략 분석"""
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"advertiser": competitor}},
                        {"range": {"timestamp": time_range}}
                    ]
                }
            },
            "aggs": {
                "creative_types": {
                    "terms": {"field": "creative_type"}
                },
                "ad_formats": {
                    "terms": {"field": "ad_format"}
                },
                "target_demographics": {
                    "terms": {"field": "target_audience.age_range"}
                },
                "budget_distribution": {
                    "histogram": {
                        "field": "daily_budget",
                        "interval": 100
                    }
                },
                "keyword_strategy": {
                    "terms": {"field": "keywords", "size": 20}
                },
                "performance_metrics": {
                    "avg": {"field": "ctr"}
                }
            },
            "size": 0
        }
        
        try:
            response = self.es.search(index=self.index_name, body=query)
            return self._format_strategy_analysis(response, competitor)
        except Exception as e:
            logger.error(f"Error analyzing competitor {competitor}: {e}")
            return {}
    
    def _format_competitor_analysis(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """경쟁사 분석 결과 포맷팅"""
        competitor_data = {}
        
        for bucket in response['aggregations']['competitor_activity']['buckets']:
            competitor = bucket['key']
            competitor_data[competitor] = {
                'avg_bid': bucket['avg_bid']['value'],
                'total_impressions': bucket['total_impressions']['value'],
                'avg_position': bucket['avg_position']['value'],
                'recent_ads': [
                    hit['_source'] for hit in bucket['recent_ads']['hits']['hits']
                ]
            }
        
        return competitor_data
    
    def _format_strategy_analysis(self, response: Dict[str, Any], 
                                competitor: str) -> Dict[str, Any]:
        """전략 분석 결과 포맷팅"""
        return {
            'competitor': competitor,
            'creative_distribution': {
                bucket['key']: bucket['doc_count']
                for bucket in response['aggregations']['creative_types']['buckets']
            },
            'format_preference': {
                bucket['key']: bucket['doc_count']
                for bucket in response['aggregations']['ad_formats']['buckets']
            },
            'target_demographics': {
                bucket['key']: bucket['doc_count']
                for bucket in response['aggregations']['target_demographics']['buckets']
            },
            'budget_distribution': [
                {'range': f"{bucket['key']}-{bucket['key']+100}", 'count': bucket['doc_count']}
                for bucket in response['aggregations']['budget_distribution']['buckets']
            ],
            'top_keywords': [
                bucket['key'] for bucket in response['aggregations']['keyword_strategy']['buckets']
            ],
            'avg_ctr': response['aggregations']['performance_metrics']['value']
        }

# 사용 예시
def example_elasticsearch_ad_system():
    """Elasticsearch 광고 시스템 예시"""
    print("=== Elasticsearch 광고 검색 시스템 ===")
    
    # 1. Elasticsearch 관리자 초기화
    es_manager = ElasticsearchAdManager()
    
    # 2. 샘플 광고 데이터 생성
    sample_ads = []
    
    campaigns = ['camp_mobile_game', 'camp_ecommerce', 'camp_finance']
    industries = ['gaming', 'retail', 'finance']
    creative_types = ['image', 'video', 'carousel', 'text']
    
    np.random.seed(42)
    
    for i in range(1000):
        ad_doc = AdDocument(
            ad_id=f"ad_{i:05d}",
            campaign_id=np.random.choice(campaigns),
            ad_group_id=f"adgroup_{np.random.randint(1, 50):03d}",
            title=f"Best {np.random.choice(['Product', 'Service', 'Deal'])} for You",
            description=f"Discover amazing {np.random.choice(['features', 'benefits', 'savings'])} with our latest offering",
            keywords=[f"keyword_{j}" for j in np.random.choice(100, 3, replace=False)],
            landing_page_url=f"https://example.com/landing_{i}",
            advertiser=f"Advertiser_{np.random.randint(1, 20)}",
            industry=np.random.choice(industries),
            target_audience={
                'age_range': np.random.choice(['18-24', '25-34', '35-44', '45-54']),
                'gender': np.random.choice(['M', 'F', 'All']),
                'interests': [f"interest_{j}" for j in np.random.choice(50, 2, replace=False)],
                'behavior': np.random.choice(['high_spender', 'bargain_hunter', 'brand_loyal'])
            },
            creative_type=np.random.choice(creative_types),
            ad_format=np.random.choice(['search', 'display', 'video', 'shopping']),
            bid_amount=np.random.uniform(0.5, 10.0),
            daily_budget=np.random.uniform(50, 1000),
            impressions=np.random.randint(1000, 100000),
            clicks=np.random.randint(10, 5000),
            conversions=np.random.randint(1, 500),
            cost=np.random.uniform(100, 5000),
            revenue=np.random.uniform(200, 10000),
            ctr=np.random.uniform(0.01, 0.15),
            cvr=np.random.uniform(0.01, 0.3),
            roas=np.random.uniform(1.0, 8.0),
            quality_score=np.random.uniform(1, 10),
            relevance_score=np.random.uniform(0, 1),
            timestamp=datetime.now() - timedelta(days=np.random.randint(0, 90)),
            geography=['KR', 'US', 'JP'],
            devices=['mobile', 'desktop'],
            placements=['search', 'youtube', 'gmail']
        )
        sample_ads.append(ad_doc)
    
    # 3. 대량 인덱싱
    print("대량 인덱싱 시작...")
    result = es_manager.bulk_index_ads(sample_ads[:100])  # 처음 100개만 테스트
    print(f"인덱싱 완료: 성공 {result['success']}개")
    
    # 4. 검색 엔진 테스트
    print("\n=== 광고 검색 테스트 ===")
    search_engine = AdSearchEngine(es_manager)
    
    # 기본 검색
    search_query = SearchQuery(
        query_text="product",
        filters={'industry': 'gaming'},
        sort_by=[{'ctr': {'order': 'desc'}}],
        aggregations={
            'avg_ctr_by_format': {
                'terms': {'field': 'ad_format'},
                'aggs': {'avg_ctr': {'avg': {'field': 'ctr'}}}
            }
        },
        size=10
    )
    
    search_results = search_engine.search_ads(search_query)
    print(f"검색 결과: {search_results['total']}개")
    print(f"최고 점수: {search_results['max_score']}")
    
    # 5. 성과 분석
    print("\n=== 성과 분석 ===")
    analytics_engine = AdAnalyticsEngine(es_manager)
    
    date_range = {
        'start': (datetime.now() - timedelta(days=30)).isoformat(),
        'end': datetime.now().isoformat()
    }
    
    performance_analysis = analytics_engine.analyze_campaign_performance(date_range)
    print(f"분석된 캠페인 수: {len(performance_analysis)}")
    
    # 키워드 트렌드 분석
    keyword_trends = analytics_engine.analyze_keyword_trends("30d")
    print(f"키워드 성과 분석: {len(keyword_trends.get('keyword_performance', {}))}")
    print(f"트렌딩 키워드: {len(keyword_trends.get('trending_keywords', []))}")
    
    # 6. 경쟁사 모니터링
    print("\n=== 경쟁사 모니터링 ===")
    competitor_monitor = CompetitorMonitoringSystem(es_manager)
    
    competitors = ['Advertiser_1', 'Advertiser_2', 'Advertiser_3']
    keywords = ['keyword_1', 'keyword_2']
    
    monitoring_results = competitor_monitor.monitor_competitor_keywords(keywords, competitors)
    print(f"모니터링된 키워드: {len(monitoring_results)}")
    
    return {
        'indexed_ads': result['success'],
        'search_results': search_results['total'],
        'campaigns_analyzed': len(performance_analysis),
        'keywords_analyzed': len(keyword_trends.get('keyword_performance', {}))
    }

if __name__ == "__main__":
    results = example_elasticsearch_ad_system()
    print(f"\nElasticsearch 광고 시스템 완료!")
    print(f"인덱싱된 광고: {results['indexed_ads']}개")
    print(f"검색 결과: {results['search_results']}개")
    print(f"분석된 캠페인: {results['campaigns_analyzed']}개")
```

## 🚀 프로젝트
1. **대규모 광고 검색 플랫폼**
2. **실시간 경쟁사 모니터링 시스템**
3. **키워드 트렌드 분석 도구**
4. **성과 최적화 대시보드**