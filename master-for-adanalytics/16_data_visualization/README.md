# 16. Data Visualization - 데이터 시각화

## 📚 과정 소개
matplotlib, seaborn, plotly를 활용한 광고 데이터 시각화를 마스터합니다. 대시보드 구축부터 인터랙티브 차트까지 실무에 바로 적용할 수 있는 시각화 기술을 학습합니다.

## 🎯 학습 목표
- 광고 성과 데이터 시각화
- 인터랙티브 대시보드 구축
- 스토리텔링을 위한 차트 디자인
- 실시간 모니터링 시각화

## 📖 주요 내용

### 광고 성과 시각화 기초
```python
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
sns.set_style("whitegrid")
sns.set_palette("husl")

class AdDataVisualizer:
    """광고 데이터 시각화 클래스"""
    
    def __init__(self):
        self.color_palette = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17a2b8'
        }
        
    def plot_campaign_performance_overview(self, df: pd.DataFrame) -> go.Figure:
        """캠페인 성과 종합 대시보드"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['일별 지출 및 매출', 'CTR vs CPA 상관관계', 
                          '채널별 성과 비교', '전환 퍼널 분석'],
            specs=[[{"secondary_y": True}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "funnel"}]]
        )
        
        # 1. 일별 지출 및 매출 트렌드
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['cost'], 
                      name='일일 지출', line=dict(color=self.color_palette['danger'])),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['revenue'], 
                      name='일일 매출', line=dict(color=self.color_palette['success'])),
            row=1, col=1, secondary_y=True
        )
        
        # 2. CTR vs CPA 산점도
        fig.add_trace(
            go.Scatter(x=df['ctr'], y=df['cpa'], 
                      mode='markers', name='캠페인',
                      marker=dict(size=df['cost']/1000, 
                                color=df['roas'],
                                colorscale='RdYlGn',
                                showscale=True)),
            row=1, col=2
        )
        
        # 3. 채널별 성과
        channel_performance = df.groupby('channel').agg({
            'cost': 'sum',
            'revenue': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        fig.add_trace(
            go.Bar(x=channel_performance['channel'], 
                  y=channel_performance['cost'],
                  name='지출', marker_color=self.color_palette['primary']),
            row=2, col=1
        )
        
        # 4. 전환 퍼널
        funnel_data = [
            ('노출', df['impressions'].sum()),
            ('클릭', df['clicks'].sum()),
            ('방문', df['clicks'].sum() * 0.8),  # 가정
            ('전환', df['conversions'].sum())
        ]
        
        fig.add_trace(
            go.Funnel(
                y=[step[0] for step in funnel_data],
                x=[step[1] for step in funnel_data],
                textinfo="value+percent initial"
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="광고 캠페인 성과 대시보드",
            showlegend=True
        )
        
        return fig
    
    def create_cohort_heatmap(self, cohort_data: pd.DataFrame) -> go.Figure:
        """코호트 분석 히트맵"""
        fig = go.Figure(data=go.Heatmap(
            z=cohort_data.values,
            x=cohort_data.columns,
            y=cohort_data.index,
            colorscale='RdYlGn',
            text=cohort_data.values,
            texttemplate="%{text:.1%}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='고객 코호트 분석 - 재구매율',
            xaxis_title='구매 후 경과 개월',
            yaxis_title='고객 획득 월',
            height=600
        )
        
        return fig
    
    def plot_attribution_waterfall(self, attribution_data: Dict) -> go.Figure:
        """어트리뷰션 워터폴 차트"""
        channels = list(attribution_data.keys())
        values = list(attribution_data.values())
        
        # 누적 값 계산
        cumulative = np.cumsum([0] + values)
        
        fig = go.Figure()
        
        for i, (channel, value) in enumerate(zip(channels, values)):
            fig.add_trace(go.Bar(
                x=[channel],
                y=[value],
                base=[cumulative[i]],
                name=channel,
                text=f'{value:.0f}',
                textposition='inside'
            ))
        
        fig.update_layout(
            title='채널별 어트리뷰션 기여도',
            xaxis_title='마케팅 채널',
            yaxis_title='기여 전환 수',
            barmode='stack',
            height=500
        )
        
        return fig
    
    def create_real_time_dashboard(self, real_time_data: pd.DataFrame) -> go.Figure:
        """실시간 모니터링 대시보드"""
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=['실시간 지출', '시간별 CTR', '활성 캠페인 수', 
                          '전환률 추이', '상위 키워드', '디바이스별 분포'],
            specs=[[{"type": "indicator"}, {"type": "scatter"}],
                   [{"type": "indicator"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )
        
        # 실시간 지출 게이지
        current_spend = real_time_data['cost'].sum()
        daily_budget = 10000  # 예시
        
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=current_spend,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "일일 지출 (원)"},
            delta={'reference': daily_budget * 0.8},
            gauge={
                'axis': {'range': [None, daily_budget]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, daily_budget * 0.5], 'color': "lightgray"},
                    {'range': [daily_budget * 0.5, daily_budget * 0.8], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': daily_budget * 0.9
                }
            }
        ), row=1, col=1)
        
        # 시간별 CTR 추이
        hourly_ctr = real_time_data.groupby('hour')['ctr'].mean()
        fig.add_trace(
            go.Scatter(x=hourly_ctr.index, y=hourly_ctr.values,
                      mode='lines+markers', name='시간별 CTR'),
            row=1, col=2
        )
        
        # 활성 캠페인 수 표시
        active_campaigns = len(real_time_data['campaign'].unique())
        fig.add_trace(go.Indicator(
            mode="number",
            value=active_campaigns,
            title={'text': "활성 캠페인"},
        ), row=2, col=1)
        
        # 전환률 추이
        hourly_cvr = real_time_data.groupby('hour')['cvr'].mean()
        fig.add_trace(
            go.Scatter(x=hourly_cvr.index, y=hourly_cvr.values,
                      mode='lines+markers', name='시간별 전환률'),
            row=2, col=2
        )
        
        # 상위 키워드 성과
        top_keywords = real_time_data.nlargest(10, 'conversions')
        fig.add_trace(
            go.Bar(x=top_keywords['keyword'], y=top_keywords['conversions']),
            row=3, col=1
        )
        
        # 디바이스별 분포
        device_dist = real_time_data.groupby('device')['clicks'].sum()
        fig.add_trace(
            go.Pie(labels=device_dist.index, values=device_dist.values),
            row=3, col=2
        )
        
        fig.update_layout(height=900, title_text="실시간 광고 모니터링")
        return fig
    
    def plot_keyword_performance_matrix(self, keyword_data: pd.DataFrame) -> go.Figure:
        """키워드 성과 매트릭스"""
        fig = go.Figure()
        
        # 버블 차트로 키워드 성과 표시
        fig.add_trace(go.Scatter(
            x=keyword_data['ctr'],
            y=keyword_data['cvr'],
            mode='markers+text',
            marker=dict(
                size=keyword_data['impressions']/1000,
                color=keyword_data['roas'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="ROAS"),
                line=dict(width=1, color='DarkSlateGrey')
            ),
            text=keyword_data['keyword'],
            textposition="middle center",
            hovertemplate='<b>%{text}</b><br>' +
                         'CTR: %{x:.2%}<br>' +
                         'CVR: %{y:.2%}<br>' +
                         'ROAS: %{marker.color:.1f}<br>' +
                         '<extra></extra>'
        ))
        
        # 사분면 구분선
        avg_ctr = keyword_data['ctr'].mean()
        avg_cvr = keyword_data['cvr'].mean()
        
        fig.add_hline(y=avg_cvr, line_dash="dash", line_color="gray", 
                     annotation_text="평균 전환률")
        fig.add_vline(x=avg_ctr, line_dash="dash", line_color="gray", 
                     annotation_text="평균 CTR")
        
        # 사분면 라벨 추가
        max_ctr = keyword_data['ctr'].max()
        max_cvr = keyword_data['cvr'].max()
        
        fig.add_annotation(x=max_ctr*0.9, y=max_cvr*0.9, text="스타 키워드",
                          showarrow=False, font=dict(size=14, color="green"))
        fig.add_annotation(x=max_ctr*0.1, y=max_cvr*0.9, text="전환 특화",
                          showarrow=False, font=dict(size=14, color="blue"))
        fig.add_annotation(x=max_ctr*0.9, y=max_cvr*0.1, text="트래픽 특화",
                          showarrow=False, font=dict(size=14, color="orange"))
        fig.add_annotation(x=max_ctr*0.1, y=max_cvr*0.1, text="개선 필요",
                          showarrow=False, font=dict(size=14, color="red"))
        
        fig.update_layout(
            title='키워드 성과 매트릭스 (CTR vs CVR)',
            xaxis_title='클릭률 (CTR)',
            yaxis_title='전환률 (CVR)',
            height=600,
            xaxis=dict(tickformat='.1%'),
            yaxis=dict(tickformat='.1%')
        )
        
        return fig
    
    def create_campaign_comparison_radar(self, campaigns_data: pd.DataFrame) -> go.Figure:
        """캠페인 비교 레이더 차트"""
        fig = go.Figure()
        
        metrics = ['CTR', 'CVR', 'ROAS', 'Quality Score', 'Brand Awareness']
        
        for _, campaign in campaigns_data.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[campaign['ctr']*100, campaign['cvr']*100, 
                   campaign['roas']*10, campaign['quality_score']*10,
                   campaign['brand_awareness']],
                theta=metrics,
                fill='toself',
                name=campaign['campaign_name']
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="캠페인 성과 비교 (레이더 차트)",
            height=600
        )
        
        return fig

class InteractiveDashboard:
    """인터랙티브 대시보드 클래스"""
    
    def __init__(self):
        self.visualizer = AdDataVisualizer()
        
    def create_campaign_filter_dashboard(self, df: pd.DataFrame):
        """필터링 가능한 캠페인 대시보드"""
        import dash
        from dash import dcc, html, Input, Output
        
        app = dash.Dash(__name__)
        
        app.layout = html.Div([
            html.H1("광고 캠페인 인터랙티브 대시보드"),
            
            # 필터 컨트롤
            html.Div([
                html.Div([
                    html.Label("캠페인 선택:"),
                    dcc.Dropdown(
                        id='campaign-dropdown',
                        options=[{'label': camp, 'value': camp} 
                                for camp in df['campaign'].unique()],
                        value=df['campaign'].unique()[:5],
                        multi=True
                    )
                ], style={'width': '48%', 'display': 'inline-block'}),
                
                html.Div([
                    html.Label("날짜 범위:"),
                    dcc.DatePickerRange(
                        id='date-picker',
                        start_date=df['date'].min(),
                        end_date=df['date'].max()
                    )
                ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
            ]),
            
            # 차트 컨테이너
            html.Div([
                dcc.Graph(id='performance-chart'),
                dcc.Graph(id='funnel-chart'),
            ]),
            
            # 데이터 테이블
            html.Div(id='data-table')
        ])
        
        @app.callback(
            [Output('performance-chart', 'figure'),
             Output('funnel-chart', 'figure'),
             Output('data-table', 'children')],
            [Input('campaign-dropdown', 'value'),
             Input('date-picker', 'start_date'),
             Input('date-picker', 'end_date')]
        )
        def update_dashboard(selected_campaigns, start_date, end_date):
            # 데이터 필터링
            filtered_df = df[
                (df['campaign'].isin(selected_campaigns)) &
                (df['date'] >= start_date) &
                (df['date'] <= end_date)
            ]
            
            # 성과 차트
            perf_fig = self.visualizer.plot_campaign_performance_overview(filtered_df)
            
            # 퍼널 차트
            funnel_fig = self.create_conversion_funnel(filtered_df)
            
            # 데이터 테이블
            table = self.create_summary_table(filtered_df)
            
            return perf_fig, funnel_fig, table
        
        return app
    
    def create_conversion_funnel(self, df: pd.DataFrame) -> go.Figure:
        """전환 퍼널 차트"""
        total_impressions = df['impressions'].sum()
        total_clicks = df['clicks'].sum()
        total_visits = total_clicks * 0.85  # 가정
        total_conversions = df['conversions'].sum()
        
        fig = go.Figure(go.Funnel(
            y=['노출', '클릭', '방문', '전환'],
            x=[total_impressions, total_clicks, total_visits, total_conversions],
            textinfo="value+percent initial+percent previous",
            marker=dict(
                color=["deepskyblue", "lightsalmon", "tan", "teal"]
            )
        ))
        
        fig.update_layout(title="전환 퍼널 분석")
        return fig
    
    def create_summary_table(self, df: pd.DataFrame) -> html.Table:
        """요약 테이블 생성"""
        summary = df.groupby('campaign').agg({
            'impressions': 'sum',
            'clicks': 'sum', 
            'cost': 'sum',
            'conversions': 'sum',
            'revenue': 'sum'
        }).round(2)
        
        summary['CTR'] = (summary['clicks'] / summary['impressions'] * 100).round(2)
        summary['CPA'] = (summary['cost'] / summary['conversions']).round(2)
        summary['ROAS'] = (summary['revenue'] / summary['cost']).round(2)
        
        return html.Table([
            html.Thead([
                html.Tr([html.Th(col) for col in ['캠페인'] + list(summary.columns)])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(campaign),
                    *[html.Td(f"{summary.loc[campaign, col]:,}" if col in ['impressions', 'clicks', 'conversions'] 
                             else f"{summary.loc[campaign, col]:.2f}") 
                      for col in summary.columns]
                ]) for campaign in summary.index
            ])
        ])

class AdvancedVisualization:
    """고급 시각화 기법"""
    
    def create_animated_performance_timeline(self, df: pd.DataFrame) -> go.Figure:
        """애니메이션 타임라인"""
        fig = px.scatter(
            df, x="ctr", y="cvr", size="cost", color="campaign",
            hover_name="campaign", size_max=60,
            animation_frame="date", animation_group="campaign",
            title="캠페인 성과 변화 (애니메이션)",
            labels={'ctr': 'CTR (%)', 'cvr': 'CVR (%)'}
        )
        
        fig.update_layout(height=600)
        return fig
    
    def create_3d_performance_scatter(self, df: pd.DataFrame) -> go.Figure:
        """3D 성과 산점도"""
        fig = go.Figure(data=[go.Scatter3d(
            x=df['ctr'],
            y=df['cvr'],
            z=df['roas'],
            mode='markers',
            marker=dict(
                size=df['cost']/1000,
                color=df['roas'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="ROAS")
            ),
            text=df['campaign'],
            hovertemplate='<b>%{text}</b><br>' +
                         'CTR: %{x:.2%}<br>' +
                         'CVR: %{y:.2%}<br>' +
                         'ROAS: %{z:.1f}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            title='3D 캠페인 성과 분석',
            scene=dict(
                xaxis_title='CTR',
                yaxis_title='CVR', 
                zaxis_title='ROAS'
            ),
            height=700
        )
        
        return fig
    
    def create_sankey_user_journey(self, journey_data: pd.DataFrame) -> go.Figure:
        """사용자 여정 산키 다이어그램"""
        # 터치포인트 간 흐름 계산
        sources = []
        targets = []
        values = []
        labels = []
        
        touchpoints = journey_data['touchpoint'].unique()
        label_map = {tp: i for i, tp in enumerate(touchpoints)}
        labels = list(touchpoints)
        
        for i in range(len(journey_data) - 1):
            current = journey_data.iloc[i]['touchpoint']
            next_tp = journey_data.iloc[i + 1]['touchpoint']
            
            if current != next_tp:
                sources.append(label_map[current])
                targets.append(label_map[next_tp])
                values.append(1)
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color="blue"
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values
            )
        )])
        
        fig.update_layout(title_text="사용자 여정 흐름도", font_size=10)
        return fig

# 사용 예시
def create_sample_dashboard():
    """샘플 대시보드 생성"""
    # 샘플 데이터 생성
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
    
    df = pd.DataFrame({
        'date': np.repeat(dates, 3),
        'campaign': np.tile(['Campaign A', 'Campaign B', 'Campaign C'], len(dates)),
        'impressions': np.random.randint(1000, 10000, len(dates) * 3),
        'clicks': np.random.randint(50, 500, len(dates) * 3),
        'cost': np.random.uniform(100, 1000, len(dates) * 3),
        'conversions': np.random.randint(1, 50, len(dates) * 3),
        'revenue': np.random.uniform(200, 2000, len(dates) * 3)
    })
    
    # 계산된 지표 추가
    df['ctr'] = df['clicks'] / df['impressions']
    df['cvr'] = df['conversions'] / df['clicks']
    df['cpa'] = df['cost'] / df['conversions']
    df['roas'] = df['revenue'] / df['cost']
    
    # 시각화 생성
    visualizer = AdDataVisualizer()
    dashboard_fig = visualizer.plot_campaign_performance_overview(df)
    
    return dashboard_fig, df
```

## 🚀 프로젝트
1. **실시간 광고 성과 대시보드**
2. **인터랙티브 캠페인 분석 도구**
3. **고객 여정 시각화 플랫폼**
4. **A/B 테스트 결과 시각화 시스템**