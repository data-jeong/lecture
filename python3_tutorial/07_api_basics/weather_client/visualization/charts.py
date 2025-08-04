import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import List, Optional, Tuple
from datetime import datetime
import numpy as np
from ..models.weather import WeatherData
from ..models.forecast import ForecastData


class WeatherCharts:
    def __init__(self, style: str = 'seaborn-v0_8'):
        try:
            plt.style.use(style)
        except:
            plt.style.use('default')
        self.fig_size = (12, 6)
        
    def plot_temperature_trend(self, weather_data: List[WeatherData],
                              title: str = "Temperature Trend") -> None:
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        times = [data.timestamp for data in weather_data]
        temperatures = [data.temperature for data in weather_data]
        feels_like = [data.feels_like for data in weather_data]
        
        ax.plot(times, temperatures, 'b-', label='Temperature', linewidth=2)
        ax.plot(times, feels_like, 'r--', label='Feels Like', linewidth=1.5, alpha=0.7)
        
        ax.fill_between(times, temperatures, feels_like, alpha=0.3)
        
        ax.set_xlabel('Time')
        ax.set_ylabel('Temperature (°C)')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()
        
    def plot_forecast_comparison(self, forecasts: List[ForecastData],
                                title: str = "5-Day Forecast") -> None:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        dates = [f.date for f in forecasts]
        date_labels = [d.strftime('%m/%d') for d in dates]
        temp_max = [f.temperature_max for f in forecasts]
        temp_min = [f.temperature_min for f in forecasts]
        temp_avg = [f.temperature_avg for f in forecasts]
        
        x = np.arange(len(dates))
        
        ax1.plot(x, temp_max, 'r-o', label='Max', linewidth=2, markersize=8)
        ax1.plot(x, temp_avg, 'g-s', label='Avg', linewidth=2, markersize=6)
        ax1.plot(x, temp_min, 'b-^', label='Min', linewidth=2, markersize=8)
        
        ax1.fill_between(x, temp_min, temp_max, alpha=0.2)
        
        ax1.set_xticks(x)
        ax1.set_xticklabels(date_labels)
        ax1.set_ylabel('Temperature (°C)')
        ax1.set_title(f'{title} - Temperature')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        humidity = [f.humidity for f in forecasts]
        precipitation = [f.precipitation_probability for f in forecasts]
        
        ax2.bar(x - 0.2, humidity, 0.4, label='Humidity (%)', color='blue', alpha=0.7)
        ax2.bar(x + 0.2, precipitation, 0.4, label='Rain Prob (%)', color='cyan', alpha=0.7)
        
        ax2.set_xticks(x)
        ax2.set_xticklabels(date_labels)
        ax2.set_ylabel('Percentage (%)')
        ax2.set_title('Humidity & Precipitation Probability')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
    def plot_wind_rose(self, weather_data: List[WeatherData],
                      title: str = "Wind Rose") -> None:
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='polar')
        
        wind_dirs = [np.radians(data.wind_direction) for data in weather_data]
        wind_speeds = [data.wind_speed for data in weather_data]
        
        bars = ax.bar(wind_dirs, wind_speeds, width=0.5, bottom=0.0)
        
        for r, bar in zip(wind_speeds, bars):
            if r < 2:
                bar.set_facecolor('green')
            elif r < 5:
                bar.set_facecolor('yellow')
            elif r < 8:
                bar.set_facecolor('orange')
            else:
                bar.set_facecolor('red')
                
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_title(title)
        
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        angles = np.linspace(0, 2 * np.pi, len(directions), endpoint=False)
        ax.set_xticks(angles)
        ax.set_xticklabels(directions)
        
        plt.show()
        
    def plot_weather_overview(self, weather: WeatherData) -> None:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        categories = ['Temp', 'Feels', 'Humidity', 'Pressure']
        values = [
            weather.temperature,
            weather.feels_like,
            weather.humidity,
            weather.pressure / 10
        ]
        colors = ['red', 'orange', 'blue', 'green']
        
        bars = ax1.bar(categories, values, color=colors, alpha=0.7)
        ax1.set_ylabel('Value')
        ax1.set_title('Current Conditions')
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f}', ha='center', va='bottom')
                    
        theta = np.radians(weather.wind_direction)
        ax2 = plt.subplot(222, projection='polar')
        ax2.arrow(theta, 0, 0, weather.wind_speed, 
                 head_width=0.3, head_length=0.5, fc='blue', ec='blue')
        ax2.set_theta_zero_location('N')
        ax2.set_theta_direction(-1)
        ax2.set_title(f'Wind: {weather.wind_speed:.1f} m/s')
        
        cloud_data = [weather.clouds, 100 - weather.clouds]
        ax3.pie(cloud_data, labels=['Cloudy', 'Clear'], 
               colors=['gray', 'lightblue'], autopct='%1.1f%%')
        ax3.set_title('Cloud Coverage')
        
        info_text = [
            f"Description: {weather.description}",
            f"Visibility: {weather.visibility:.1f} km",
            f"Time: {weather.timestamp.strftime('%Y-%m-%d %H:%M')}",
        ]
        
        ax4.text(0.1, 0.5, '\n'.join(info_text), fontsize=12,
                verticalalignment='center')
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.axis('off')
        ax4.set_title('Additional Info')
        
        plt.suptitle('Weather Overview', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()
        
    def plot_hourly_comparison(self, hourly_data: List[WeatherData],
                              metrics: List[str] = None) -> None:
        if not metrics:
            metrics = ['temperature', 'humidity', 'wind_speed', 'pressure']
            
        fig, axes = plt.subplots(len(metrics), 1, figsize=(12, 3 * len(metrics)),
                                 sharex=True)
        
        if len(metrics) == 1:
            axes = [axes]
            
        times = [data.timestamp for data in hourly_data]
        
        for ax, metric in zip(axes, metrics):
            values = [getattr(data, metric) for data in hourly_data]
            
            ax.plot(times, values, linewidth=2)
            ax.fill_between(times, values, alpha=0.3)
            ax.set_ylabel(metric.replace('_', ' ').title())
            ax.grid(True, alpha=0.3)
            
            if metric == 'temperature':
                ax.axhline(y=0, color='blue', linestyle='--', alpha=0.5)
                ax.set_ylabel('Temperature (°C)')
            elif metric == 'humidity':
                ax.set_ylabel('Humidity (%)')
            elif metric == 'wind_speed':
                ax.set_ylabel('Wind Speed (m/s)')
            elif metric == 'pressure':
                ax.set_ylabel('Pressure (hPa)')
                
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        axes[-1].xaxis.set_major_locator(mdates.HourLocator(interval=3))
        plt.xticks(rotation=45)
        
        axes[-1].set_xlabel('Time')
        fig.suptitle('Hourly Weather Metrics', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
        
    def save_chart(self, filename: str, dpi: int = 100) -> None:
        plt.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"Chart saved as {filename}")