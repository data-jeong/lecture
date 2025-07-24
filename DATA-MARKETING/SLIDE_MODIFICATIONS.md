# Detailed Slide Modifications

## CSS Updates for Better Structure

```css
/* Add to existing CSS */

/* Part dividers */
.part-divider {
    background: linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
}

.part-number {
    font-size: 4rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 900;
    margin-bottom: 1rem;
}

.part-title {
    font-size: 2.5rem;
    color: #fff;
    font-weight: 700;
    margin-bottom: 1rem;
}

.part-subtitle {
    font-size: 1.2rem;
    color: #888;
}

/* Slide numbering */
.slide-number {
    position: absolute;
    top: 2rem;
    right: 2rem;
    color: #666;
    font-size: 0.9rem;
    font-weight: 500;
}

/* Overflow fixes for hypothesis worksheet */
.hypothesis-worksheet-compact {
    background: rgba(255, 255, 255, 0.03);
    border: 2px solid rgba(255, 198, 0, 0.3);
    border-radius: 20px;
    padding: 1.5rem;
    margin: 1rem 0;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.worksheet-group {
    background: rgba(255, 255, 255, 0.02);
    padding: 1rem;
    border-radius: 10px;
}

.worksheet-group-title {
    color: #4ecdc4;
    font-size: 1.1rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.worksheet-content {
    font-size: 0.9rem;
    line-height: 1.4;
}

.worksheet-example {
    background: rgba(78, 205, 196, 0.1);
    padding: 0.5rem;
    border-radius: 5px;
    font-size: 0.8rem;
    margin-top: 0.5rem;
    color: #95e1d3;
}

/* Compact platform cards */
.platform-grid-compact {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin: 2rem 0;
}

.platform-card-compact {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.platform-card-compact:hover {
    transform: translateY(-5px);
    border-color: #4ecdc4;
    box-shadow: 0 10px 30px rgba(78, 205, 196, 0.2);
}

/* Transition slides */
.transition-content {
    text-align: center;
    padding: 3rem;
}

.transition-arrow {
    font-size: 3rem;
    color: #4ecdc4;
    margin: 2rem 0;
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-20px); }
}
```

## Slide-by-Slide Modifications

### Slide 1: Title (Keep existing)
```html
<!-- Add slide number -->
<div class="slide-number">1 / 17</div>
```

### Slide 2: Problem Statement (Modify)
```html
<section class="slide content-slide">
    <div class="slide-number">2 / 17</div>
    <div class="slide-content">
        <h2>AI 시대, 데이터가 없으면?</h2>
        
        <div class="problem-statement-enhanced">
            <div class="ai-reality">
                <h3>매체는 이미 AI로 무장했다</h3>
                <div class="platform-ai-showcase">
                    <div class="ai-platform">
                        <span class="platform-name">Google</span>
                        <span class="ai-feature">Performance Max</span>
                    </div>
                    <div class="ai-platform">
                        <span class="platform-name">Meta</span>
                        <span class="ai-feature">Advantage+</span>
                    </div>
                    <div class="ai-platform">
                        <span class="platform-name">TikTok</span>
                        <span class="ai-feature">Smart Creative</span>
                    </div>
                </div>
            </div>
            
            <div class="transition-metaphor">
                <p class="metaphor-text">
                    "데이터 없는 AI는 <span class="highlight">눈 감고 운전하는 것</span>과 같습니다"
                </p>
            </div>
            
            <div class="critical-questions">
                <h3>우리의 준비 상태는?</h3>
                <ul class="question-list">
                    <li>데이터로 AI 성과를 극대화할 준비가 되었나요?</li>
                    <li>매체 AI와 협력할 데이터 전략이 있나요?</li>
                    <li>측정 가능한 성과 지표를 설정했나요?</li>
                </ul>
            </div>
        </div>
    </div>
</section>
```

### Part 1 Divider (New)
```html
<section class="slide part-divider">
    <div class="slide-number">3 / 17</div>
    <div class="part-number">Part 1</div>
    <h2 class="part-title">Data Strategy Understanding</h2>
    <p class="part-subtitle">데이터 전략의 이해와 필요성</p>
</section>
```

### Slide 4: Why Data Strategy Matters (Modified)
```html
<section class="slide content-slide">
    <div class="slide-number">4 / 17</div>
    <div class="slide-content">
        <h2>데이터 기반의 절대적 필요성</h2>
        
        <div class="theoretical-foundation">
            <blockquote class="drucker-quote">
                <p>"측정할 수 없으면 관리할 수 없고, 관리할 수 없으면 개선할 수 없다"</p>
                <cite>- Peter Drucker</cite>
            </blockquote>
        </div>
        
        <div class="module-intro">
            <h3>'적당한' 데이터는 더 이상 통하지 않는다</h3>
            <!-- Keep existing content but restructured -->
        </div>
    </div>
</section>
```

### Slide 5: Cost of Bad Data (Restructured)
```html
<section class="slide content-slide">
    <div class="slide-number">5 / 17</div>
    <div class="slide-content">
        <h2>나쁜 데이터의 비용 정량화하기</h2>
        
        <div class="cost-categories">
            <div class="cost-category">
                <h3 class="category-title">전략적 실패</h3>
                <div class="cost-items">
                    <div class="cost-item">
                        <h4>잘못된 예산 분배</h4>
                        <p>효과적으로 '보이는' 채널에 과도하게 투자</p>
                    </div>
                    <div class="cost-item">
                        <h4>결함 있는 전략</h4>
                        <p>불완전한 데이터 기반 의사결정</p>
                    </div>
                </div>
            </div>
            
            <div class="cost-category">
                <h3 class="category-title">신뢰와 관계</h3>
                <div class="cost-items">
                    <div class="cost-item">
                        <h4>클라이언트 신뢰도 하락</h4>
                        <p>백엔드 데이터와 모순되는 보고서</p>
                    </div>
                    <div class="cost-item">
                        <h4>개인화의 실패</h4>
                        <p>깨끗한 데이터 없이는 개인화 불가능</p>
                    </div>
                </div>
            </div>
            
            <div class="cost-category">
                <h3 class="category-title">운영 비효율</h3>
                <div class="cost-items">
                    <div class="cost-item">
                        <h4>기회비용 손실</h4>
                        <p>늦은 의사결정, 시장 기회 상실</p>
                    </div>
                    <div class="cost-item">
                        <h4>반복 작업의 비효율</h4>
                        <p>데이터 불일치로 인한 재작업</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
```

### Slide 8: Hypothesis Validation (Overflow Fix)
```html
<section class="slide content-slide">
    <div class="slide-number">8 / 17</div>
    <div class="slide-content">
        <h2>가설 검증 프레임워크</h2>
        
        <div class="hypothesis-worksheet-compact">
            <div class="worksheet-group">
                <div class="worksheet-group-title">
                    <span>📋</span> 문제 정의 & 가설
                </div>
                <div class="worksheet-content">
                    <p><strong>문제:</strong> 해결하고자 하는 비즈니스 이슈</p>
                    <p><strong>가설:</strong> "우리는...라고 믿는다" 형식</p>
                    <div class="worksheet-example">
                        예: 모바일 전환율이 낮다 → 결제 단계를 줄이면 15% 개선될 것
                    </div>
                </div>
            </div>
            
            <div class="worksheet-group">
                <div class="worksheet-group-title">
                    <span>🎯</span> 타겟 & KPI
                </div>
                <div class="worksheet-content">
                    <p><strong>대상:</strong> 테스트 타겟 세그먼트</p>
                    <p><strong>지표:</strong> 추적할 핵심 KPI</p>
                    <div class="worksheet-example">
                        예: 모바일 사용자 → 구매 전환율, 이탈률
                    </div>
                </div>
            </div>
            
            <div class="worksheet-group">
                <div class="worksheet-group-title">
                    <span>🔬</span> 검증 방법 & 기간
                </div>
                <div class="worksheet-content">
                    <p><strong>방법:</strong> A/B 테스트, 탐색 분석 등</p>
                    <p><strong>기간:</strong> 통계적 유의성 확보 기간</p>
                    <div class="worksheet-example">
                        예: A/B 테스트 → 2주간 (일 1,000+ 세션)
                    </div>
                </div>
            </div>
            
            <div class="worksheet-group">
                <div class="worksheet-group-title">
                    <span>✅</span> 의사결정 & 액션
                </div>
                <div class="worksheet-content">
                    <p><strong>기준:</strong> 성공/실패 판단 기준</p>
                    <p><strong>다음:</strong> 결과에 따른 액션 플랜</p>
                    <div class="worksheet-example">
                        예: 10%+ 개선 시 → 전체 적용
                    </div>
                </div>
            </div>
        </div>
        
        <a href="hypothesis-validation-template.html" class="download-btn" target="_blank">
            가설 검증 템플릿 다운로드
        </a>
    </div>
</section>
```

### Transition Between Parts
```html
<section class="slide content-slide">
    <div class="slide-number">11 / 17</div>
    <div class="transition-content">
        <h3>이론을 알았다면, 이제 실전이다</h3>
        <div class="transition-arrow">↓</div>
        <p>GA4와 GTM으로 구현하는 실전 데이터 전략</p>
    </div>
</section>
```

### Platform Strategy Cards (Compact)
```html
<section class="slide content-slide">
    <div class="slide-number">15 / 17</div>
    <div class="slide-content">
        <h2>플랫폼별 AI 최적화 전략</h2>
        
        <div class="platform-grid-compact">
            <div class="platform-card-compact">
                <div class="platform-header">
                    <span class="platform-icon">🔍</span>
                    <h4>Google Ads</h4>
                </div>
                <ul class="platform-strategy">
                    <li>Enhanced Conversions 설정</li>
                    <li>가치 기반 입찰 최적화</li>
                    <li>잠재고객 신호 강화</li>
                </ul>
            </div>
            
            <div class="platform-card-compact">
                <div class="platform-header">
                    <span class="platform-icon">📘</span>
                    <h4>Meta Ads</h4>
                </div>
                <ul class="platform-strategy">
                    <li>Conversions API 구현</li>
                    <li>이벤트 매치 품질 향상</li>
                    <li>가치 최적화 캠페인</li>
                </ul>
            </div>
            
            <div class="platform-card-compact">
                <div class="platform-header">
                    <span class="platform-icon">🎵</span>
                    <h4>TikTok Ads</h4>
                </div>
                <ul class="platform-strategy">
                    <li>Events API 연동</li>
                    <li>콘텐츠 신호 추적</li>
                    <li>창의적 성과 분석</li>
                </ul>
            </div>
            
            <div class="platform-card-compact">
                <div class="platform-header">
                    <span class="platform-icon">🛍️</span>
                    <h4>Naver Ads</h4>
                </div>
                <ul class="platform-strategy">
                    <li>전환 추적 스크립트</li>
                    <li>쇼핑 피드 최적화</li>
                    <li>키워드 성과 연동</li>
                </ul>
            </div>
        </div>
    </div>
</section>
```