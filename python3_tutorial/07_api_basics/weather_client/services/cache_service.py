import json
import os
import pickle
from typing import Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import logging

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, cache_dir: str = ".cache", expiry_minutes: int = 30):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.expiry_minutes = expiry_minutes
        self.memory_cache = {}
        
    def get(self, key: str) -> Optional[Any]:
        cache_key = self._generate_key(key)
        
        if cache_key in self.memory_cache:
            data, expiry = self.memory_cache[cache_key]
            if datetime.now() < expiry:
                logger.debug(f"Memory cache hit for key: {key}")
                return data
            else:
                del self.memory_cache[cache_key]
                
        file_path = self.cache_dir / f"{cache_key}.pkl"
        if file_path.exists():
            try:
                with open(file_path, 'rb') as f:
                    data, expiry = pickle.load(f)
                    if datetime.now() < expiry:
                        logger.debug(f"File cache hit for key: {key}")
                        self.memory_cache[cache_key] = (data, expiry)
                        return data
                    else:
                        file_path.unlink()
            except Exception as e:
                logger.error(f"Failed to load cache for {key}: {e}")
                
        logger.debug(f"Cache miss for key: {key}")
        return None
        
    def set(self, key: str, value: Any, expiry_minutes: Optional[int] = None) -> None:
        cache_key = self._generate_key(key)
        expiry = datetime.now() + timedelta(minutes=expiry_minutes or self.expiry_minutes)
        
        self.memory_cache[cache_key] = (value, expiry)
        
        file_path = self.cache_dir / f"{cache_key}.pkl"
        try:
            with open(file_path, 'wb') as f:
                pickle.dump((value, expiry), f)
            logger.debug(f"Cached data for key: {key}")
        except Exception as e:
            logger.error(f"Failed to cache data for {key}: {e}")
            
    def delete(self, key: str) -> None:
        cache_key = self._generate_key(key)
        
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
            
        file_path = self.cache_dir / f"{cache_key}.pkl"
        if file_path.exists():
            file_path.unlink()
            logger.debug(f"Deleted cache for key: {key}")
            
    def clear(self) -> None:
        self.memory_cache.clear()
        
        for file in self.cache_dir.glob("*.pkl"):
            file.unlink()
            
        logger.info("Cache cleared")
        
    def cleanup_expired(self) -> int:
        cleaned = 0
        
        expired_keys = []
        for cache_key, (data, expiry) in self.memory_cache.items():
            if datetime.now() >= expiry:
                expired_keys.append(cache_key)
                
        for key in expired_keys:
            del self.memory_cache[key]
            cleaned += 1
            
        for file_path in self.cache_dir.glob("*.pkl"):
            try:
                with open(file_path, 'rb') as f:
                    data, expiry = pickle.load(f)
                    if datetime.now() >= expiry:
                        file_path.unlink()
                        cleaned += 1
            except Exception as e:
                logger.error(f"Failed to cleanup {file_path}: {e}")
                file_path.unlink()
                cleaned += 1
                
        logger.info(f"Cleaned up {cleaned} expired cache entries")
        return cleaned
        
    def _generate_key(self, key: str) -> str:
        return hashlib.md5(key.encode()).hexdigest()
        
    def get_cache_stats(self) -> dict:
        memory_entries = len(self.memory_cache)
        file_entries = len(list(self.cache_dir.glob("*.pkl")))
        
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.pkl"))
        
        return {
            'memory_entries': memory_entries,
            'file_entries': file_entries,
            'total_entries': memory_entries + file_entries,
            'cache_dir': str(self.cache_dir),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024)
        }


class RedisCache:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0,
                 expiry_minutes: int = 30):
        self.expiry_minutes = expiry_minutes
        self.redis_client = None
        
        try:
            import redis
            self.redis_client = redis.Redis(host=host, port=port, db=db,
                                           decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis cache initialized")
        except ImportError:
            logger.warning("Redis not installed, falling back to file cache")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, falling back to file cache")
            self.redis_client = None
            
    def get(self, key: str) -> Optional[Any]:
        if not self.redis_client:
            return None
            
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Redis get failed for {key}: {e}")
            
        return None
        
    def set(self, key: str, value: Any, expiry_minutes: Optional[int] = None) -> None:
        if not self.redis_client:
            return
            
        try:
            expiry_seconds = (expiry_minutes or self.expiry_minutes) * 60
            self.redis_client.setex(key, expiry_seconds, json.dumps(value))
        except Exception as e:
            logger.error(f"Redis set failed for {key}: {e}")
            
    def delete(self, key: str) -> None:
        if not self.redis_client:
            return
            
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete failed for {key}: {e}")
            
    def clear(self) -> None:
        if not self.redis_client:
            return
            
        try:
            self.redis_client.flushdb()
        except Exception as e:
            logger.error(f"Redis clear failed: {e}")