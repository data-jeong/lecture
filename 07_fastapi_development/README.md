# 07. FastAPI Development - FastAPI 개발

## 📚 과정 소개
고성능 광고 API 서버를 FastAPI로 구축하는 방법을 학습합니다. 비동기 처리, 자동 문서화, 타입 안정성을 갖춘 프로덕션 레벨 API를 개발합니다.

## 🎯 학습 목표
- FastAPI를 활용한 RESTful API 설계
- 비동기 처리로 고성능 서버 구축
- 광고 시스템 API 아키텍처
- 실시간 웹소켓 통신

## 📖 주요 내용

### 광고 캠페인 API 구현
```python
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio

app = FastAPI(title="Ad Campaign API", version="1.0.0")

# Pydantic 모델
from pydantic import BaseModel, Field

class CampaignBase(BaseModel):
    name: str = Field(..., example="여름 세일 캠페인")
    budget: float = Field(..., gt=0, example=1000000)
    start_date: datetime
    end_date: datetime
    target_audience: dict

class CampaignCreate(CampaignBase):
    pass

class Campaign(CampaignBase):
    id: int
    status: str
    spent: float = 0
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    
    class Config:
        orm_mode = True

# API 엔드포인트
@app.post("/campaigns", response_model=Campaign)
async def create_campaign(
    campaign: CampaignCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """새 광고 캠페인 생성"""
    db_campaign = CampaignModel(**campaign.dict())
    db.add(db_campaign)
    db.commit()
    
    # 백그라운드 작업
    background_tasks.add_task(
        setup_campaign_automation,
        campaign_id=db_campaign.id
    )
    
    return db_campaign

@app.get("/campaigns/{campaign_id}/performance")
async def get_campaign_performance(
    campaign_id: int,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
):
    """캠페인 성과 조회"""
    # Redis 캐시 확인
    cache_key = f"campaign:{campaign_id}:performance"
    cached = await redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # DB에서 조회
    performance = await calculate_performance(
        campaign_id, date_from, date_to
    )
    
    # 캐시 저장 (5분 TTL)
    await redis_client.setex(
        cache_key, 300, json.dumps(performance)
    )
    
    return performance

# WebSocket 실시간 대시보드
@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            # 실시간 지표 전송
            metrics = await get_realtime_metrics()
            await websocket.send_json(metrics)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
```

### 고급 기능 구현
- JWT 인증 및 권한 관리
- Rate Limiting
- 파일 업로드 (광고 크리에이티브)
- 배치 처리 API
- GraphQL 통합

### 성능 최적화
- 비동기 데이터베이스 쿼리
- 연결 풀링
- 응답 캐싱
- 부하 분산

## 🚀 프로젝트
1. **광고 관리 플랫폼 API**
2. **실시간 입찰 시스템**
3. **광고 성과 대시보드 API**
4. **마이크로서비스 게이트웨이**