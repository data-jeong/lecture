"""
설정 관리
"""

import os
from typing import Optional
from pathlib import Path
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv


class Config(BaseModel):
    """애플리케이션 설정"""
    
    # API Keys
    openweather_api_key: str = Field(..., description="OpenWeatherMap API 키")
    google_maps_api_key: Optional[str] = Field(None, description="Google Maps API 키")
    public_data_api_key: Optional[str] = Field(None, description="공공데이터 포털 API 키")
    
    # Redis Settings
    redis_host: str = Field("localhost", description="Redis 호스트")
    redis_port: int = Field(6379, description="Redis 포트")
    redis_db: int = Field(0, description="Redis 데이터베이스")
    
    # Cache Settings
    cache_expiry_minutes: int = Field(30, description="캐시 만료 시간 (분)")
    default_cache_size: int = Field(1000, description="기본 캐시 크기")
    
    # Application Settings
    default_language: str = Field("ko", description="기본 언어")
    default_units: str = Field("metric", description="기본 단위 (metric, imperial)")
    request_timeout: int = Field(30, description="요청 타임아웃 (초)")
    max_retries: int = Field(3, description="최대 재시도 횟수")
    
    # Notification Settings
    enable_notifications: bool = Field(False, description="알림 활성화")
    smtp_host: Optional[str] = Field(None, description="SMTP 호스트")
    smtp_port: int = Field(587, description="SMTP 포트")
    smtp_user: Optional[str] = Field(None, description="SMTP 사용자")
    smtp_password: Optional[str] = Field(None, description="SMTP 비밀번호")
    
    # Logging
    log_level: str = Field("INFO", description="로그 레벨")
    log_file: Optional[str] = Field(None, description="로그 파일 경로")
    
    @validator('openweather_api_key')
    def validate_openweather_key(cls, v):
        """OpenWeatherMap API 키 검증"""
        if not v or v == "your_openweather_api_key_here":
            raise ValueError("유효한 OpenWeatherMap API 키가 필요합니다")
        return v
    
    @validator('default_units')
    def validate_units(cls, v):
        """단위 시스템 검증"""
        if v not in ['metric', 'imperial', 'kelvin']:
            raise ValueError("units는 'metric', 'imperial', 'kelvin' 중 하나여야 합니다")
        return v
    
    @validator('default_language')
    def validate_language(cls, v):
        """언어 코드 검증"""
        supported_languages = ['ko', 'en', 'ja', 'zh', 'es', 'fr', 'de']
        if v not in supported_languages:
            raise ValueError(f"지원되는 언어: {', '.join(supported_languages)}")
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """로그 레벨 검증"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"로그 레벨은 {', '.join(valid_levels)} 중 하나여야 합니다")
        return v.upper()
    
    def get_redis_url(self) -> str:
        """Redis URL 생성"""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    def get_openweather_base_url(self) -> str:
        """OpenWeatherMap 기본 URL"""
        return "https://api.openweathermap.org/data/2.5"
    
    def get_openweather_geocoding_url(self) -> str:
        """OpenWeatherMap 지오코딩 URL"""
        return "http://api.openweathermap.org/geo/1.0"
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> 'Config':
        """환경 변수에서 설정 로드"""
        if env_file:
            load_dotenv(env_file)
        else:
            # 현재 디렉토리와 상위 디렉토리에서 .env 파일 찾기
            for path in [Path.cwd(), Path.cwd().parent]:
                env_path = path / '.env'
                if env_path.exists():
                    load_dotenv(env_path)
                    break
        
        # 환경 변수에서 값 읽기
        config_data = {
            'openweather_api_key': os.getenv('OPENWEATHER_API_KEY', ''),
            'google_maps_api_key': os.getenv('GOOGLE_MAPS_API_KEY'),
            'public_data_api_key': os.getenv('PUBLIC_DATA_API_KEY'),
            
            'redis_host': os.getenv('REDIS_HOST', 'localhost'),
            'redis_port': int(os.getenv('REDIS_PORT', '6379')),
            'redis_db': int(os.getenv('REDIS_DB', '0')),
            
            'cache_expiry_minutes': int(os.getenv('CACHE_EXPIRY_MINUTES', '30')),
            'default_cache_size': int(os.getenv('DEFAULT_CACHE_SIZE', '1000')),
            
            'default_language': os.getenv('DEFAULT_LANGUAGE', 'ko'),
            'default_units': os.getenv('DEFAULT_UNITS', 'metric'),
            'request_timeout': int(os.getenv('REQUEST_TIMEOUT', '30')),
            'max_retries': int(os.getenv('MAX_RETRIES', '3')),
            
            'enable_notifications': os.getenv('ENABLE_NOTIFICATIONS', 'false').lower() == 'true',
            'smtp_host': os.getenv('SMTP_HOST'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'smtp_user': os.getenv('SMTP_USER'),
            'smtp_password': os.getenv('SMTP_PASSWORD'),
            
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'log_file': os.getenv('LOG_FILE'),
        }
        
        return cls(**config_data)


# 전역 설정 인스턴스
_config: Optional[Config] = None


def get_config(env_file: Optional[str] = None, reload: bool = False) -> Config:
    """설정 인스턴스 반환"""
    global _config
    
    if _config is None or reload:
        _config = Config.from_env(env_file)
    
    return _config


def load_config_from_file(config_file: str) -> Config:
    """설정 파일에서 직접 로드"""
    import json
    import yaml
    
    config_path = Path(config_file)
    
    if not config_path.exists():
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_file}")
    
    if config_path.suffix.lower() == '.json':
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif config_path.suffix.lower() in ['.yml', '.yaml']:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    else:
        raise ValueError("지원되는 설정 파일 형식: .json, .yml, .yaml")
    
    return Config(**data)


def create_sample_config(output_file: str = "config.json"):
    """샘플 설정 파일 생성"""
    sample_config = {
        "openweather_api_key": "your_openweather_api_key_here",
        "google_maps_api_key": "your_google_maps_api_key_here",
        "public_data_api_key": "your_public_data_api_key_here",
        
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
        
        "cache_expiry_minutes": 30,
        "default_cache_size": 1000,
        
        "default_language": "ko",
        "default_units": "metric",
        "request_timeout": 30,
        "max_retries": 3,
        
        "enable_notifications": False,
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "your_email@gmail.com",
        "smtp_password": "your_app_password",
        
        "log_level": "INFO",
        "log_file": "weather_client.log"
    }
    
    import json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2, ensure_ascii=False)
    
    print(f"샘플 설정 파일이 생성되었습니다: {output_file}")
    print("API 키를 설정한 후 사용하세요.")