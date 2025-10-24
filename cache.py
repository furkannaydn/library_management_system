# Kütüphane Yönetim Sistemi - Caching Sistemi
# Redis ile hızlı veri erişimi ve performans optimizasyonu
# API yanıtlarını cache'leyerek veritabanı yükünü azaltır

import redis
import json
import asyncio
from typing import Optional, Any
from datetime import timedelta
import logging

# Redis bağlantısı - Cache sistemi
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

# Cache anahtarları - Organize edilmiş cache yapısı
CACHE_KEYS = {
    'kitaplar': 'kitaplar:all',
    'uyeler': 'uyeler:all', 
    'kiralamalar': 'kiralamalar:all',
    'istatistikler': 'stats:dashboard',
    'populer_kitaplar': 'stats:popular_books',
    'aylik_rapor': 'stats:monthly_report'
}

class CacheManager:
    """Cache yönetimi sınıfı - Redis ile veri cache'leme"""
    
    def __init__(self):
        self.redis = redis_client
        self.default_ttl = 300  # 5 dakika varsayılan TTL
    
    async def get(self, key: str) -> Optional[Any]:
        """Cache'den veri al - JSON formatında"""
        try:
            cached_data = self.redis.get(key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logging.error(f"Cache get hatası: {e}")
            return None
    
    async def set(self, key: str, data: Any, ttl: int = None) -> bool:
        """Cache'e veri kaydet - JSON formatında"""
        try:
            ttl = ttl or self.default_ttl
            json_data = json.dumps(data, default=str)
            self.redis.setex(key, ttl, json_data)
            return True
        except Exception as e:
            logging.error(f"Cache set hatası: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Cache'den veri sil"""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logging.error(f"Cache delete hatası: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> bool:
        """Pattern'e uyan tüm cache'leri sil"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
            return True
        except Exception as e:
            logging.error(f"Cache pattern delete hatası: {e}")
            return False
    
    async def clear_all(self) -> bool:
        """Tüm cache'i temizle"""
        try:
            self.redis.flushdb()
            return True
        except Exception as e:
            logging.error(f"Cache clear hatası: {e}")
            return False

# Global cache manager instance
cache_manager = CacheManager()

# Cache decorator - Fonksiyon sonuçlarını otomatik cache'ler
def cache_result(key_prefix: str, ttl: int = 300):
    """Fonksiyon sonuçlarını cache'leyen decorator"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Cache anahtarı oluştur
            cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"
            
            # Cache'den veri al
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Fonksiyonu çalıştır
            result = await func(*args, **kwargs)
            
            # Sonucu cache'e kaydet
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Cache yardımcı fonksiyonları
async def invalidate_kitap_cache():
    """Kitap ile ilgili cache'leri temizle"""
    await cache_manager.delete_pattern("kitaplar:*")
    await cache_manager.delete_pattern("stats:*")

async def invalidate_uye_cache():
    """Üye ile ilgili cache'leri temizle"""
    await cache_manager.delete_pattern("uyeler:*")
    await cache_manager.delete_pattern("stats:*")

async def invalidate_kiralama_cache():
    """Kiralama ile ilgili cache'leri temizle"""
    await cache_manager.delete_pattern("kiralamalar:*")
    await cache_manager.delete_pattern("stats:*")

# Cache istatistikleri
async def get_cache_stats():
    """Cache istatistiklerini al"""
    try:
        info = redis_client.info()
        return {
            'connected_clients': info.get('connected_clients', 0),
            'used_memory': info.get('used_memory_human', '0B'),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
            'total_keys': redis_client.dbsize()
        }
    except Exception as e:
        logging.error(f"Cache stats hatası: {e}")
        return {}
