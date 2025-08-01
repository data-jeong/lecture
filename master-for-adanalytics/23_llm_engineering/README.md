# 23. LLM Engineering - LLM 엔지니어링

## 📚 과정 소개
대규모 언어 모델(LLM)을 활용한 마케팅 자동화 및 광고 카피 생성 시스템을 구축합니다. RAG, LangChain, 프롬프트 엔지니어링을 마스터합니다.

## 🎯 학습 목표
- LLM을 활용한 광고 카피 자동 생성
- RAG 기반 마케팅 인사이트 시스템
- 고객 상담 자동화
- 비용 효율적인 LLM 운영

## 📖 주요 내용

### 광고 카피 생성 시스템
```python
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.memory import ConversationSummaryMemory
import pinecone

class AdCopyGenerator:
    """LLM 기반 광고 카피 생성기"""
    
    def __init__(self, api_key):
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.7,
            api_key=api_key
        )
        self.embeddings = OpenAIEmbeddings()
        self._init_vector_store()
        
    def _init_vector_store(self):
        """벡터 스토어 초기화 (성공 사례 DB)"""
        pinecone.init(api_key="YOUR_PINECONE_KEY")
        
        # 기존 성공 광고 카피 임베딩
        self.vectorstore = Pinecone.from_existing_index(
            "successful-ad-copies",
            self.embeddings
        )
    
    def generate_ad_copy(self, product_info, target_audience, tone="professional"):
        """광고 카피 생성"""
        # 유사한 성공 사례 검색
        similar_ads = self.vectorstore.similarity_search(
            f"{product_info} {target_audience}",
            k=3
        )
        
        # 프롬프트 템플릿
        prompt = PromptTemplate(
            input_variables=["product", "audience", "tone", "examples"],
            template="""
            당신은 전문 광고 카피라이터입니다.
            
            제품 정보: {product}
            타겟 고객: {audience}
            톤앤매너: {tone}
            
            성공 사례:
            {examples}
            
            위 정보를 바탕으로 매력적인 광고 카피를 작성해주세요:
            1. 헤드라인 (15자 이내)
            2. 본문 (50자 이내)
            3. CTA (행동 유도 문구)
            
            추가로 A/B 테스트를 위한 변형 2개도 제안해주세요.
            """
        )
        
        # 체인 실행
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        result = chain.run(
            product=product_info,
            audience=target_audience,
            tone=tone,
            examples="\n".join([ad.page_content for ad in similar_ads])
        )
        
        return self._parse_ad_copy(result)
    
    def optimize_existing_copy(self, current_copy, performance_data):
        """기존 카피 최적화"""
        optimization_prompt = f"""
        현재 광고 카피:
        {current_copy}
        
        성과 데이터:
        - CTR: {performance_data['ctr']}%
        - 전환율: {performance_data['cvr']}%
        - 주요 이탈 지점: {performance_data['drop_off_point']}
        
        이 데이터를 바탕으로 광고 카피를 개선해주세요.
        개선 이유도 함께 설명해주세요.
        """
        
        response = self.llm.predict(optimization_prompt)
        return response
```

### RAG 기반 마케팅 인사이트
```python
from langchain.chains import RetrievalQA
from langchain.document_loaders import S3DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class MarketingInsightRAG:
    """RAG 기반 마케팅 인사이트 시스템"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k")
        self._setup_knowledge_base()
        
    def _setup_knowledge_base(self):
        """지식 베이스 구축"""
        # 마케팅 문서 로드
        loader = S3DirectoryLoader(
            bucket="marketing-knowledge",
            prefix="documents/"
        )
        documents = loader.load()
        
        # 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.split_documents(documents)
        
        # 벡터 스토어 생성
        self.vectorstore = Pinecone.from_documents(
            texts,
            OpenAIEmbeddings(),
            index_name="marketing-knowledge"
        )
        
        # QA 체인 설정
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 5}
            )
        )
    
    def get_campaign_insights(self, campaign_data):
        """캠페인 인사이트 생성"""
        query = f"""
        다음 캠페인 데이터를 분석하고 인사이트를 제공해주세요:
        
        캠페인: {campaign_data['name']}
        기간: {campaign_data['period']}
        성과:
        - 노출: {campaign_data['impressions']}
        - CTR: {campaign_data['ctr']}%
        - CPA: {campaign_data['cpa']}원
        - ROAS: {campaign_data['roas']}
        
        1. 성과 평가
        2. 개선 방안
        3. 유사 성공 사례
        4. 다음 단계 추천
        """
        
        response = self.qa_chain.run(query)
        return response
```

### LangChain 워크플로우
```python
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.tools import DuckDuckGoSearchRun
from langchain.utilities import GoogleSerperAPIWrapper

class MarketingAutomationAgent:
    """마케팅 자동화 에이전트"""
    
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0)
        self.search = DuckDuckGoSearchRun()
        self.serper = GoogleSerperAPIWrapper()
        self._setup_tools()
        
    def _setup_tools(self):
        """도구 설정"""
        self.tools = [
            Tool(
                name="Search",
                func=self.search.run,
                description="최신 마케팅 트렌드 검색"
            ),
            Tool(
                name="Competitor Analysis",
                func=self._analyze_competitor,
                description="경쟁사 광고 분석"
            ),
            Tool(
                name="Generate Copy",
                func=self._generate_copy,
                description="광고 카피 생성"
            ),
            Tool(
                name="Performance Prediction",
                func=self._predict_performance,
                description="광고 성과 예측"
            )
        ]
        
        # 에이전트 초기화
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
    
    def create_campaign(self, brief):
        """캠페인 자동 생성"""
        task = f"""
        다음 브리프를 바탕으로 완전한 광고 캠페인을 생성하세요:
        {brief}
        
        수행할 작업:
        1. 시장 및 경쟁사 조사
        2. 타겟 오디언스 정의
        3. 광고 카피 3종 생성
        4. 예상 성과 분석
        5. 예산 배분 제안
        """
        
        result = self.agent.run(task)
        return result
```

### 비용 최적화 전략
```python
class LLMCostOptimizer:
    """LLM 비용 최적화"""
    
    def __init__(self):
        self.models = {
            'gpt-4': {'cost_per_1k': 0.03, 'quality': 0.95},
            'gpt-3.5-turbo': {'cost_per_1k': 0.002, 'quality': 0.85},
            'claude-2': {'cost_per_1k': 0.008, 'quality': 0.90}
        }
        
    def select_optimal_model(self, task_type, budget_constraint):
        """작업별 최적 모델 선택"""
        if task_type == "creative_generation":
            # 창의적 작업은 고품질 모델
            return 'gpt-4'
        elif task_type == "data_extraction":
            # 단순 추출은 저비용 모델
            return 'gpt-3.5-turbo'
        else:
            # 비용/품질 균형
            return 'claude-2'
    
    def implement_caching(self):
        """응답 캐싱으로 비용 절감"""
        from functools import lru_cache
        
        @lru_cache(maxsize=1000)
        def cached_llm_call(prompt_hash):
            # 동일한 프롬프트는 캐시에서 반환
            pass
```

### 프롬프트 엔지니어링
```python
class PromptOptimizer:
    """프롬프트 최적화"""
    
    def __init__(self):
        self.best_practices = {
            'clarity': '명확하고 구체적인 지시',
            'examples': 'Few-shot 예시 제공',
            'format': '원하는 출력 형식 명시',
            'constraints': '제약 조건 명확히'
        }
    
    def optimize_prompt(self, base_prompt):
        """프롬프트 최적화"""
        optimized = f"""
        [작업 컨텍스트]
        당신은 10년 경력의 디지털 마케팅 전문가입니다.
        
        [작업 지시]
        {base_prompt}
        
        [출력 형식]
        - JSON 형식으로 응답
        - 각 항목에 대한 근거 포함
        - 실행 가능한 구체적 제안
        
        [제약 조건]
        - 한국 시장 특성 고려
        - 모바일 우선 접근
        - 개인정보 보호 규정 준수
        """
        
        return optimized
```

## 🚀 프로젝트
1. **AI 광고 카피라이터**
2. **마케팅 챗봇 시스템**
3. **자동화된 A/B 테스트 플랫폼**
4. **RAG 기반 마케팅 지식 관리 시스템**