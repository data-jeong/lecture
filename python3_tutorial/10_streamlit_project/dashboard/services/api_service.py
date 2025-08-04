"""API service for external data integration"""

import requests
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
import aiohttp


class APIService:
    """Service for handling API calls"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url
        self.session = requests.Session()
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def set_auth_token(self, token: str):
        """Set authentication token"""
        self.headers['Authorization'] = f'Bearer {token}'
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        try:
            url = f"{self.base_url}/{endpoint}" if self.base_url else endpoint
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request"""
        try:
            url = f"{self.base_url}/{endpoint}" if self.base_url else endpoint
            response = self.session.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make PUT request"""
        try:
            url = f"{self.base_url}/{endpoint}" if self.base_url else endpoint
            response = self.session.put(url, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def delete(self, endpoint: str) -> bool:
        """Make DELETE request"""
        try:
            url = f"{self.base_url}/{endpoint}" if self.base_url else endpoint
            response = self.session.delete(url, headers=self.headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False
    
    async def async_get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Async GET request"""
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/{endpoint}" if self.base_url else endpoint
                async with session.get(url, params=params, headers=self.headers) as response:
                    return await response.json()
            except Exception as e:
                return {'error': str(e)}
    
    async def fetch_multiple(self, endpoints: List[str]) -> List[Dict[str, Any]]:
        """Fetch data from multiple endpoints concurrently"""
        tasks = [self.async_get(endpoint) for endpoint in endpoints]
        return await asyncio.gather(*tasks)
    
    def get_weather(self, city: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Get weather data (example API integration)"""
        if not api_key:
            # Return mock data for demo
            return {
                'city': city,
                'temperature': 22,
                'description': 'Partly cloudy',
                'humidity': 65,
                'wind_speed': 3.5
            }
        
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }
        
        return self.get(url, params)
    
    def get_news(self, category: str = 'general', api_key: Optional[str] = None) -> List[Dict]:
        """Get news articles (example API integration)"""
        if not api_key:
            # Return mock data for demo
            return [
                {
                    'title': 'Breaking News: Technology Advances',
                    'description': 'Latest developments in AI and machine learning',
                    'url': 'https://example.com/news1',
                    'publishedAt': datetime.now().isoformat()
                },
                {
                    'title': 'Market Update: Stocks Rise',
                    'description': 'Global markets show positive trends',
                    'url': 'https://example.com/news2',
                    'publishedAt': datetime.now().isoformat()
                }
            ]
        
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            'category': category,
            'apiKey': api_key,
            'country': 'us'
        }
        
        response = self.get(url, params)
        return response.get('articles', [])
    
    def get_stock_data(self, symbol: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Get stock market data (example API integration)"""
        if not api_key:
            # Return mock data for demo
            import random
            base_price = 150
            return {
                'symbol': symbol,
                'price': base_price + random.uniform(-5, 5),
                'change': random.uniform(-2, 2),
                'change_percent': random.uniform(-1.5, 1.5),
                'volume': random.randint(1000000, 5000000),
                'high': base_price + 5,
                'low': base_price - 5
            }
        
        # Actual API call would go here
        url = f"https://api.example.com/stock/{symbol}"
        return self.get(url)
    
    def health_check(self) -> bool:
        """Check if API is accessible"""
        try:
            response = self.session.get(
                f"{self.base_url}/health" if self.base_url else "https://httpbin.org/get",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False