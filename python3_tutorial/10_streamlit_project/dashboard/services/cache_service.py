"""Cache service for optimizing data access"""

import streamlit as st
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
import hashlib
import json
import pickle
import os


class CacheService:
    """Service for managing cached data"""
    
    def __init__(self, cache_dir: str = "dashboard/.cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.memory_cache = {}
    
    def get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if self._is_valid(entry):
                return entry['data']
            else:
                del self.memory_cache[key]
        
        # Check file cache
        file_path = os.path.join(self.cache_dir, f"{key}.pkl")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    entry = pickle.load(f)
                    if self._is_valid(entry):
                        # Load to memory cache
                        self.memory_cache[key] = entry
                        return entry['data']
                    else:
                        os.remove(file_path)
            except:
                pass
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL (time to live) in seconds"""
        entry = {
            'data': value,
            'timestamp': datetime.now(),
            'ttl': ttl
        }
        
        # Save to memory cache
        self.memory_cache[key] = entry
        
        # Save to file cache
        file_path = os.path.join(self.cache_dir, f"{key}.pkl")
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(entry, f)
        except:
            pass
    
    def delete(self, key: str):
        """Delete value from cache"""
        # Remove from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # Remove from file cache
        file_path = os.path.join(self.cache_dir, f"{key}.pkl")
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def clear(self):
        """Clear all cache"""
        # Clear memory cache
        self.memory_cache.clear()
        
        # Clear file cache
        for file in os.listdir(self.cache_dir):
            if file.endswith('.pkl'):
                os.remove(os.path.join(self.cache_dir, file))
    
    def _is_valid(self, entry: dict) -> bool:
        """Check if cache entry is still valid"""
        if 'ttl' not in entry or 'timestamp' not in entry:
            return False
        
        age = (datetime.now() - entry['timestamp']).total_seconds()
        return age < entry['ttl']
    
    def cached_function(self, ttl: int = 3600):
        """Decorator for caching function results"""
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self.get_cache_key(func.__name__, *args, **kwargs)
                
                # Check cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Cache result
                self.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        return decorator
    
    def get_cache_info(self) -> dict:
        """Get information about cache"""
        memory_size = len(self.memory_cache)
        
        file_count = 0
        file_size = 0
        for file in os.listdir(self.cache_dir):
            if file.endswith('.pkl'):
                file_count += 1
                file_path = os.path.join(self.cache_dir, file)
                file_size += os.path.getsize(file_path)
        
        return {
            'memory_entries': memory_size,
            'file_entries': file_count,
            'file_size_mb': file_size / (1024 * 1024),
            'cache_dir': self.cache_dir
        }
    
    def cleanup_expired(self):
        """Remove expired entries from cache"""
        # Cleanup memory cache
        expired_keys = []
        for key, entry in self.memory_cache.items():
            if not self._is_valid(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Cleanup file cache
        for file in os.listdir(self.cache_dir):
            if file.endswith('.pkl'):
                file_path = os.path.join(self.cache_dir, file)
                try:
                    with open(file_path, 'rb') as f:
                        entry = pickle.load(f)
                        if not self._is_valid(entry):
                            os.remove(file_path)
                except:
                    # Remove corrupted cache files
                    os.remove(file_path)
    
    @staticmethod
    def use_streamlit_cache(ttl: int = 3600):
        """Use Streamlit's built-in cache"""
        return st.cache_data(ttl=ttl)