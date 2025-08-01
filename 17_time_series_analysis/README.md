# 17. Time Series Analysis - 시계열 분석

## 📚 과정 소개
광고 성과 데이터의 시계열 분석을 마스터합니다. 트렌드 분석, 계절성 탐지, 예측 모델링을 통해 광고 캠페인 최적화와 예산 계획을 수립합니다.

## 🎯 학습 목표
- 광고 성과 시계열 분석
- 계절성 및 트렌드 분해
- ARIMA, Prophet 예측 모델
- 이상 탐지 및 조기 경보 시스템

## 📖 주요 내용

### 광고 시계열 데이터 분석
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 시계열 분석 라이브러리
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Prophet (Facebook)
try:
    from prophet import Prophet
    from prophet.diagnostics import cross_validation, performance_metrics
    from prophet.plot import plot_cross_validation_metric
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("Prophet not available. Install with: pip install prophet")

# 머신러닝
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class AdTimeSeriesAnalyzer:
    """광고 시계열 분석기"""
    
    def __init__(self):
        self.data = None
        self.decomposition = None
        self.models = {}
        
    def load_ad_performance_data(self, file_path: str = None) -> pd.DataFrame:
        """광고 성과 데이터 로드"""
        if file_path:
            self.data = pd.read_csv(file_path, parse_dates=['date'])
        else:
            # 샘플 데이터 생성
            self.data = self._generate_sample_data()
            
        self.data.set_index('date', inplace=True)
        return self.data
    
    def _generate_sample_data(self) -> pd.DataFrame:
        """샘플 광고 성과 데이터 생성"""
        # 2년간의 일별 데이터
        dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
        
        # 기본 트렌드 + 계절성 + 노이즈
        np.random.seed(42)
        n_days = len(dates)
        
        # 트렌드 (점진적 증가)
        trend = np.linspace(1000, 1500, n_days)
        
        # 주간 계절성 (주말 효과)
        weekly_pattern = 100 * np.sin(2 * np.pi * np.arange(n_days) / 7)
        
        # 연간 계절성 (연말 쇼핑 시즌)
        yearly_pattern = 200 * np.sin(2 * np.pi * np.arange(n_days) / 365.25 - np.pi/2)
        
        # 특별 이벤트 (Black Friday, Christmas 등)
        special_events = np.zeros(n_days)
        for i, date in enumerate(dates):
            if date.month == 11 and date.day >= 20:  # Black Friday 시즌
                special_events[i] = 300
            elif date.month == 12 and date.day >= 15:  # Christmas 시즌
                special_events[i] = 500
            elif date.month == 3 and date.day <= 14:  # 화이트데이
                special_events[i] = 150
        
        # 노이즈
        noise = np.random.normal(0, 50, n_days)
        
        # 최종 임프레션 수
        impressions = trend + weekly_pattern + yearly_pattern + special_events + noise
        impressions = np.maximum(impressions, 0)  # 음수 방지
        
        # 클릭수 (CTR 기반)
        base_ctr = 0.02
        ctr_noise = np.random.normal(0, 0.005, n_days)
        ctr = np.maximum(base_ctr + ctr_noise, 0.001)
        clicks = impressions * ctr
        
        # 비용 (CPC 기반)
        base_cpc = 0.5
        cpc_noise = np.random.normal(0, 0.1, n_days)
        cpc = np.maximum(base_cpc + cpc_noise, 0.1)
        cost = clicks * cpc
        
        # 전환수 (CVR 기반)
        base_cvr = 0.05
        cvr_noise = np.random.normal(0, 0.01, n_days)
        cvr = np.maximum(base_cvr + cvr_noise, 0.001)
        conversions = clicks * cvr
        
        # 매출 (평균 주문가격 기반)
        avg_order_value = 50
        aov_noise = np.random.normal(0, 10, n_days)
        aov = np.maximum(avg_order_value + aov_noise, 10)
        revenue = conversions * aov
        
        return pd.DataFrame({
            'date': dates,
            'impressions': impressions.astype(int),
            'clicks': clicks.astype(int),
            'cost': np.round(cost, 2),
            'conversions': conversions.astype(int),
            'revenue': np.round(revenue, 2),
            'ctr': np.round(clicks / impressions, 4),
            'cpc': np.round(cost / clicks, 2),
            'cvr': np.round(conversions / clicks, 4),
            'roas': np.round(revenue / cost, 2)
        })
    
    def decompose_time_series(self, column: str = 'impressions', 
                            model: str = 'additive') -> Dict:
        """시계열 분해"""
        if self.data is None:
            raise ValueError("데이터를 먼저 로드하세요.")
        
        # 시계열 분해
        self.decomposition = seasonal_decompose(
            self.data[column], 
            model=model, 
            period=7  # 주간 계절성
        )
        
        # 분해 결과 시각화
        fig, axes = plt.subplots(4, 1, figsize=(15, 12))
        
        self.decomposition.observed.plot(ax=axes[0], title='Original')
        self.decomposition.trend.plot(ax=axes[1], title='Trend')
        self.decomposition.seasonal.plot(ax=axes[2], title='Seasonal')
        self.decomposition.resid.plot(ax=axes[3], title='Residual')
        
        plt.tight_layout()
        plt.show()
        
        # 계절성 강도 계산
        seasonal_strength = self._calculate_seasonal_strength(column)
        trend_strength = self._calculate_trend_strength(column)
        
        return {
            'seasonal_strength': seasonal_strength,
            'trend_strength': trend_strength,
            'decomposition': self.decomposition
        }
    
    def _calculate_seasonal_strength(self, column: str) -> float:
        """계절성 강도 계산"""
        if self.decomposition is None:
            return 0.0
        
        var_residual = np.var(self.decomposition.resid.dropna())
        var_seasonal_residual = np.var(
            (self.decomposition.seasonal + self.decomposition.resid).dropna()
        )
        
        if var_seasonal_residual == 0:
            return 0.0
        
        return max(0, 1 - var_residual / var_seasonal_residual)
    
    def _calculate_trend_strength(self, column: str) -> float:
        """트렌드 강도 계산"""
        if self.decomposition is None:
            return 0.0
        
        var_residual = np.var(self.decomposition.resid.dropna())
        var_trend_residual = np.var(
            (self.decomposition.trend + self.decomposition.resid).dropna()
        )
        
        if var_trend_residual == 0:
            return 0.0
        
        return max(0, 1 - var_residual / var_trend_residual)
    
    def stationarity_test(self, column: str = 'impressions') -> Dict:
        """정상성 검정"""
        series = self.data[column].dropna()
        
        # Augmented Dickey-Fuller Test
        adf_result = adfuller(series)
        
        result = {
            'adf_statistic': adf_result[0],
            'p_value': adf_result[1],
            'critical_values': adf_result[4],
            'is_stationary': adf_result[1] < 0.05
        }
        
        print(f"ADF Test Results for {column}:")
        print(f"ADF Statistic: {result['adf_statistic']:.6f}")
        print(f"p-value: {result['p_value']:.6f}")
        print(f"Is Stationary: {result['is_stationary']}")
        
        for key, value in result['critical_values'].items():
            print(f"Critical Value ({key}): {value:.3f}")
        
        return result
    
    def make_stationary(self, column: str = 'impressions') -> pd.Series:
        """시계열 정상화"""
        series = self.data[column]
        
        # 1차 차분
        diff_series = series.diff().dropna()
        
        # 정상성 확인
        adf_result = adfuller(diff_series)
        
        if adf_result[1] < 0.05:
            print("1차 차분으로 정상성 달성")
            return diff_series
        else:
            # 2차 차분
            diff2_series = diff_series.diff().dropna()
            print("2차 차분 적용")
            return diff2_series
    
    def find_arima_parameters(self, column: str = 'impressions', 
                            max_p: int = 5, max_q: int = 5) -> Tuple[int, int, int]:
        """ARIMA 파라미터 자동 탐색"""
        series = self.data[column].dropna()
        
        best_aic = float('inf')
        best_params = (0, 0, 0)
        
        # Grid Search
        for p in range(max_p + 1):
            for d in range(2):  # 보통 0, 1차 차분
                for q in range(max_q + 1):
                    try:
                        model = ARIMA(series, order=(p, d, q))
                        fitted_model = model.fit()
                        
                        if fitted_model.aic < best_aic:
                            best_aic = fitted_model.aic
                            best_params = (p, d, q)
                            
                    except Exception:
                        continue
        
        print(f"Best ARIMA parameters: {best_params} (AIC: {best_aic:.2f})")
        return best_params
    
    def fit_arima_model(self, column: str = 'impressions', 
                       order: Tuple[int, int, int] = None) -> Dict:
        """ARIMA 모델 학습"""
        series = self.data[column].dropna()
        
        if order is None:
            order = self.find_arima_parameters(column)
        
        # 모델 학습
        model = ARIMA(series, order=order)
        fitted_model = model.fit()
        
        # 모델 저장
        self.models[f'arima_{column}'] = fitted_model
        
        # 모델 진단
        residuals = fitted_model.resid
        
        # 진단 플롯
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 잔차 플롯
        residuals.plot(ax=axes[0, 0], title='Residuals')
        
        # Q-Q 플롯
        from scipy import stats
        stats.probplot(residuals, dist="norm", plot=axes[0, 1])
        axes[0, 1].set_title('Q-Q Plot')
        
        # ACF/PACF
        plot_acf(residuals, ax=axes[1, 0], lags=20)
        plot_pacf(residuals, ax=axes[1, 1], lags=20)
        
        plt.tight_layout()
        plt.show()
        
        return {
            'model': fitted_model,
            'aic': fitted_model.aic,
            'bic': fitted_model.bic,
            'order': order,
            'summary': fitted_model.summary()
        }
    
    def forecast_arima(self, column: str = 'impressions', 
                      steps: int = 30) -> Dict:
        """ARIMA 예측"""
        model_key = f'arima_{column}'
        if model_key not in self.models:
            print(f"{column}에 대한 ARIMA 모델이 없습니다. 먼저 모델을 학습하세요.")
            return {}
        
        model = self.models[model_key]
        
        # 예측
        forecast = model.forecast(steps=steps)
        conf_int = model.get_forecast(steps=steps).conf_int()
        
        # 예측 결과 시각화
        plt.figure(figsize=(15, 6))
        
        # 원본 데이터 (마지막 100일)
        original_data = self.data[column].tail(100)
        plt.plot(original_data.index, original_data.values, 
                label='Observed', color='blue')
        
        # 예측 데이터
        future_dates = pd.date_range(
            start=self.data.index[-1] + timedelta(days=1), 
            periods=steps, 
            freq='D'
        )
        
        plt.plot(future_dates, forecast, label='Forecast', 
                color='red', linestyle='--')
        
        # 신뢰구간
        plt.fill_between(future_dates, 
                        conf_int.iloc[:, 0], 
                        conf_int.iloc[:, 1], 
                        color='red', alpha=0.3)
        
        plt.title(f'{column.capitalize()} ARIMA Forecast')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
        return {
            'forecast': forecast,
            'confidence_interval': conf_int,
            'future_dates': future_dates
        }

class ProphetAnalyzer:
    """Prophet을 활용한 시계열 분석"""
    
    def __init__(self):
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet이 설치되지 않았습니다.")
        self.models = {}
        
    def prepare_prophet_data(self, data: pd.DataFrame, column: str) -> pd.DataFrame:
        """Prophet용 데이터 준비"""
        prophet_data = data.reset_index()
        prophet_data = prophet_data[['date', column]].rename(
            columns={'date': 'ds', column: 'y'}
        )
        return prophet_data
    
    def add_holiday_effects(self, data: pd.DataFrame) -> pd.DataFrame:
        """한국 쇼핑 시즌 휴일 효과 추가"""
        holidays = pd.DataFrame({
            'holiday': 'shopping_season',
            'ds': pd.to_datetime([
                '2022-11-11', '2022-11-25', '2022-12-25',  # 2022년
                '2023-03-14', '2023-11-11', '2023-11-24', '2023-12-25',  # 2023년
                '2024-03-14', '2024-11-11', '2024-11-29', '2024-12-25'   # 2024년
            ]),
            'lower_window': -3,
            'upper_window': 3,
        })
        
        return holidays
    
    def fit_prophet_model(self, data: pd.DataFrame, column: str, 
                         include_holidays: bool = True) -> Dict:
        """Prophet 모델 학습"""
        # 데이터 준비
        prophet_data = self.prepare_prophet_data(data, column)
        
        # 모델 초기화
        model_params = {
            'daily_seasonality': True,
            'weekly_seasonality': True,
            'yearly_seasonality': True,
            'changepoint_prior_scale': 0.05,
            'seasonality_prior_scale': 10.0
        }
        
        if include_holidays:
            holidays = self.add_holiday_effects(prophet_data)
            model_params['holidays'] = holidays
        
        model = Prophet(**model_params)
        
        # 커스텀 계절성 추가 (월별)
        model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
        
        # 모델 학습
        model.fit(prophet_data)
        
        # 모델 저장
        self.models[f'prophet_{column}'] = {
            'model': model,
            'data': prophet_data
        }
        
        return {
            'model': model,
            'training_data': prophet_data
        }
    
    def forecast_prophet(self, column: str, periods: int = 30) -> Dict:
        """Prophet 예측"""
        model_info = self.models.get(f'prophet_{column}')
        if not model_info:
            raise ValueError(f"{column}에 대한 Prophet 모델이 없습니다.")
        
        model = model_info['model']
        
        # 미래 날짜 생성
        future = model.make_future_dataframe(periods=periods)
        
        # 예측
        forecast = model.predict(future)
        
        # 시각화
        fig1 = model.plot(forecast, figsize=(15, 6))
        plt.title(f'{column.capitalize()} Prophet Forecast')
        plt.show()
        
        # 구성요소 분해
        fig2 = model.plot_components(forecast, figsize=(15, 10))
        plt.show()
        
        return {
            'forecast': forecast,
            'future_dates': future,
            'model': model
        }
    
    def cross_validate_prophet(self, column: str, 
                             initial: str = '365 days',
                             period: str = '30 days', 
                             horizon: str = '30 days') -> Dict:
        """Prophet 교차 검증"""
        model_info = self.models.get(f'prophet_{column}')
        if not model_info:
            raise ValueError(f"{column}에 대한 Prophet 모델이 없습니다.")
        
        model = model_info['model']
        
        # 교차 검증
        df_cv = cross_validation(
            model, 
            initial=initial, 
            period=period, 
            horizon=horizon
        )
        
        # 성능 메트릭 계산
        df_p = performance_metrics(df_cv)
        
        # 성능 시각화
        fig = plot_cross_validation_metric(df_cv, metric='mape')
        plt.show()
        
        return {
            'cross_validation': df_cv,
            'performance_metrics': df_p
        }

class AnomalyDetector:
    """시계열 이상 탐지"""
    
    def __init__(self):
        self.detectors = {}
        
    def statistical_anomaly_detection(self, data: pd.Series, 
                                   window: int = 30, 
                                   threshold: float = 3.0) -> Dict:
        """통계적 이상 탐지"""
        # 이동 평균과 표준편차
        rolling_mean = data.rolling(window=window).mean()
        rolling_std = data.rolling(window=window).std()
        
        # Z-score 계산
        z_scores = np.abs((data - rolling_mean) / rolling_std)
        
        # 이상치 탐지
        anomalies = z_scores > threshold
        anomaly_dates = data[anomalies].index
        anomaly_values = data[anomalies].values
        
        # 시각화
        plt.figure(figsize=(15, 6))
        plt.plot(data.index, data.values, label='Original Data', alpha=0.7)
        plt.plot(rolling_mean.index, rolling_mean.values, label='Rolling Mean', color='green')
        
        # 신뢰구간
        plt.fill_between(data.index, 
                        rolling_mean - threshold * rolling_std,
                        rolling_mean + threshold * rolling_std,
                        alpha=0.3, color='green', label='Confidence Interval')
        
        # 이상치 표시
        plt.scatter(anomaly_dates, anomaly_values, 
                   color='red', s=50, label='Anomalies', zorder=5)
        
        plt.title('Statistical Anomaly Detection')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
        return {
            'anomalies': anomalies,
            'anomaly_dates': anomaly_dates,
            'anomaly_values': anomaly_values,
            'z_scores': z_scores
        }
    
    def isolation_forest_detection(self, data: pd.DataFrame, 
                                 columns: List[str],
                                 contamination: float = 0.1) -> Dict:
        """Isolation Forest를 이용한 이상 탐지"""
        # 특성 데이터 준비
        feature_data = data[columns].fillna(method='ffill')
        
        # 표준화
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(feature_data)
        
        # Isolation Forest
        iso_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        
        # 이상치 예측 (-1: 이상치, 1: 정상)
        anomaly_labels = iso_forest.fit_predict(scaled_data)
        anomaly_scores = iso_forest.decision_function(scaled_data)
        
        # 결과 데이터프레임
        results_df = data[columns].copy()
        results_df['anomaly'] = anomaly_labels
        results_df['anomaly_score'] = anomaly_scores
        
        # 이상치만 추출
        anomalies = results_df[results_df['anomaly'] == -1]
        
        # 시각화 (2D 예시 - 첫 번째와 두 번째 컬럼)
        if len(columns) >= 2:
            plt.figure(figsize=(12, 8))
            
            normal_points = results_df[results_df['anomaly'] == 1]
            anomaly_points = results_df[results_df['anomaly'] == -1]
            
            plt.scatter(normal_points[columns[0]], normal_points[columns[1]], 
                       c='blue', alpha=0.6, label='Normal')
            plt.scatter(anomaly_points[columns[0]], anomaly_points[columns[1]], 
                       c='red', alpha=0.8, label='Anomaly')
            
            plt.xlabel(columns[0])
            plt.ylabel(columns[1])
            plt.title('Isolation Forest Anomaly Detection')
            plt.legend()
            plt.show()
        
        return {
            'anomalies': anomalies,
            'anomaly_scores': anomaly_scores,
            'model': iso_forest,
            'scaler': scaler
        }
    
    def prophet_anomaly_detection(self, data: pd.DataFrame, column: str,
                                uncertainty_interval: float = 0.95) -> Dict:
        """Prophet을 이용한 이상 탐지"""
        # Prophet 모델 학습
        prophet_analyzer = ProphetAnalyzer()
        model_result = prophet_analyzer.fit_prophet_model(data, column)
        model = model_result['model']
        
        # 예측 (기존 데이터에 대해)
        future = model.make_future_dataframe(periods=0)
        forecast = model.predict(future)
        
        # 신뢰구간 밖의 데이터를 이상치로 판단
        lower_bound = forecast['yhat_lower']
        upper_bound = forecast['yhat_upper']
        actual_values = data[column].values
        
        # 이상치 탐지
        anomalies = (actual_values < lower_bound) | (actual_values > upper_bound)
        anomaly_dates = data.index[anomalies]
        anomaly_values = actual_values[anomalies]
        
        # 시각화
        plt.figure(figsize=(15, 6))
        plt.plot(data.index, actual_values, label='Actual', color='blue')
        plt.plot(forecast['ds'], forecast['yhat'], label='Predicted', color='orange')
        plt.fill_between(forecast['ds'], lower_bound, upper_bound, 
                        alpha=0.3, color='orange', label='Confidence Interval')
        plt.scatter(anomaly_dates, anomaly_values, 
                   color='red', s=50, label='Anomalies', zorder=5)
        
        plt.title(f'Prophet-based Anomaly Detection for {column}')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
        return {
            'anomalies': anomalies,
            'anomaly_dates': anomaly_dates,
            'anomaly_values': anomaly_values,
            'forecast': forecast,
            'model': model
        }

class CampaignPerformancePredictor:
    """캠페인 성과 예측기"""
    
    def __init__(self):
        self.models = {}
        
    def predict_campaign_metrics(self, historical_data: pd.DataFrame,
                               prediction_days: int = 30) -> Dict:
        """캠페인 지표 예측"""
        results = {}
        
        # 각 지표별 예측
        metrics = ['impressions', 'clicks', 'cost', 'conversions', 'revenue']
        
        for metric in metrics:
            if metric in historical_data.columns:
                # ARIMA 예측
                arima_analyzer = AdTimeSeriesAnalyzer()
                arima_analyzer.data = historical_data
                
                try:
                    arima_result = arima_analyzer.fit_arima_model(metric)
                    forecast_result = arima_analyzer.forecast_arima(metric, prediction_days)
                    
                    results[f'{metric}_arima'] = {
                        'forecast': forecast_result['forecast'],
                        'confidence_interval': forecast_result['confidence_interval'],
                        'dates': forecast_result['future_dates']
                    }
                except Exception as e:
                    print(f"ARIMA 예측 실패 for {metric}: {e}")
                
                # Prophet 예측 (사용 가능한 경우)
                if PROPHET_AVAILABLE:
                    try:
                        prophet_analyzer = ProphetAnalyzer()
                        prophet_result = prophet_analyzer.fit_prophet_model(historical_data, metric)
                        forecast_result = prophet_analyzer.forecast_prophet(metric, prediction_days)
                        
                        results[f'{metric}_prophet'] = {
                            'forecast': forecast_result['forecast'],
                            'model': forecast_result['model']
                        }
                    except Exception as e:
                        print(f"Prophet 예측 실패 for {metric}: {e}")
        
        return results
    
    def calculate_prediction_accuracy(self, actual: pd.Series, 
                                    predicted: pd.Series) -> Dict:
        """예측 정확도 계산"""
        mae = mean_absolute_error(actual, predicted)
        mse = mean_squared_error(actual, predicted)
        rmse = np.sqrt(mse)
        
        # MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        
        return {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'mape': mape
        }

# 사용 예시
def example_time_series_analysis():
    """시계열 분석 예시"""
    # 분석기 초기화
    analyzer = AdTimeSeriesAnalyzer()
    
    # 데이터 로드
    print("샘플 광고 데이터 생성 중...")
    data = analyzer.load_ad_performance_data()
    print(f"데이터 형태: {data.shape}")
    print(data.head())
    
    # 시계열 분해
    print("\n시계열 분해 중...")
    decomp_result = analyzer.decompose_time_series('impressions')
    print(f"계절성 강도: {decomp_result['seasonal_strength']:.3f}")
    print(f"트렌드 강도: {decomp_result['trend_strength']:.3f}")
    
    # 정상성 검정
    print("\n정상성 검정 중...")
    stationarity_result = analyzer.stationarity_test('impressions')
    
    # ARIMA 모델
    print("\nARIMA 모델 학습 중...")
    arima_result = analyzer.fit_arima_model('impressions')
    print(f"AIC: {arima_result['aic']:.2f}")
    
    # ARIMA 예측
    print("\nARIMA 예측 중...")
    forecast_result = analyzer.forecast_arima('impressions', 30)
    
    # Prophet 분석 (사용 가능한 경우)
    if PROPHET_AVAILABLE:
        print("\nProphet 모델 학습 중...")
        prophet_analyzer = ProphetAnalyzer()
        prophet_result = prophet_analyzer.fit_prophet_model(data, 'impressions')
        
        print("\nProphet 예측 중...")
        prophet_forecast = prophet_analyzer.forecast_prophet('impressions', 30)
    
    # 이상 탐지
    print("\n이상 탐지 중...")
    anomaly_detector = AnomalyDetector()
    
    # 통계적 이상 탐지
    stat_anomalies = anomaly_detector.statistical_anomaly_detection(
        data['impressions'], window=30, threshold=2.5
    )
    print(f"발견된 이상치 수: {len(stat_anomalies['anomaly_dates'])}")
    
    # Isolation Forest 이상 탐지
    iso_anomalies = anomaly_detector.isolation_forest_detection(
        data, ['impressions', 'clicks', 'cost'], contamination=0.05
    )
    print(f"Isolation Forest 이상치 수: {len(iso_anomalies['anomalies'])}")
    
    return {
        'data_shape': data.shape,
        'seasonal_strength': decomp_result['seasonal_strength'],
        'arima_aic': arima_result['aic'],
        'anomalies_count': len(stat_anomalies['anomaly_dates'])
    }

if __name__ == "__main__":
    results = example_time_series_analysis()
    print("시계열 분석 완료!")
```

## 🚀 프로젝트
1. **광고 성과 예측 시스템**
2. **계절성 기반 예산 계획**
3. **실시간 이상 탐지 알림**
4. **캠페인 최적화 대시보드**