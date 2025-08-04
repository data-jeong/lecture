"""Configuration management utilities"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager"""
    
    def __init__(self, config_file: str = "dashboard/config.yml"):
        self.config_file = config_file
        self.config = self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                if self.config_file.endswith('.yml') or self.config_file.endswith('.yaml'):
                    return yaml.safe_load(f) or {}
                elif self.config_file.endswith('.json'):
                    return json.load(f)
        
        # Return default config
        return self.get_default_config()
    
    def save(self, config: Dict[str, Any]):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            if self.config_file.endswith('.yml') or self.config_file.endswith('.yaml'):
                yaml.dump(config, f, default_flow_style=False)
            elif self.config_file.endswith('.json'):
                json.dump(config, f, indent=2)
        
        self.config = config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save(self.config)
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'app': {
                'name': 'Dashboard',
                'version': '1.0.0',
                'debug': False,
                'theme': 'light'
            },
            'server': {
                'host': 'localhost',
                'port': 8501,
                'base_url': 'http://localhost:8501'
            },
            'database': {
                'url': 'sqlite:///dashboard.db',
                'pool_size': 5,
                'echo': False
            },
            'cache': {
                'enabled': True,
                'ttl': 3600,
                'max_size': 100
            },
            'auth': {
                'enabled': True,
                'session_timeout': 1800,
                'max_attempts': 3
            },
            'api': {
                'weather_api_key': '',
                'news_api_key': '',
                'stock_api_key': ''
            },
            'features': {
                'analytics': True,
                'text_tools': True,
                'grade_management': True,
                'weather': True,
                'blog': True,
                'file_processing': True,
                'crawler': True
            },
            'ui': {
                'sidebar_state': 'expanded',
                'show_header': True,
                'show_footer': True,
                'max_upload_size': 200  # MB
            }
        }


def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration"""
    if config_file is None:
        config_file = os.environ.get('CONFIG_FILE', 'dashboard/config.yml')
    
    config = Config(config_file)
    return config.config


def save_config(config: Dict[str, Any], config_file: Optional[str] = None):
    """Save configuration"""
    if config_file is None:
        config_file = os.environ.get('CONFIG_FILE', 'dashboard/config.yml')
    
    config_manager = Config(config_file)
    config_manager.save(config)


def get_env_var(key: str, default: Any = None) -> Any:
    """Get environment variable"""
    return os.environ.get(key, default)


def load_secrets(secrets_file: str = "dashboard/.streamlit/secrets.toml") -> Dict[str, Any]:
    """Load secrets from file"""
    if os.path.exists(secrets_file):
        import toml
        return toml.load(secrets_file)
    return {}