# Kütüphane Yönetim Sistemi - Rate Limiting
# API isteklerini sınırlayarak güvenlik ve performans sağlar
# SlowAPI ile gelişmiş rate limiting

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
import time
import logging

# Rate limiter instance - IP bazlı sınırlama
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000/hour", "100/minute"]  # Varsayılan limitler
)

# Özel rate limit kuralları - Endpoint bazlı sınırlar
RATE_LIMITS = {
    # Genel API limitleri
    "api_general": "1000/hour",
    "api_auth": "10/minute",  # Giriş işlemleri için daha sıkı
    
    # CRUD işlemleri
    "api_create": "50/hour",  # Oluşturma işlemleri
    "api_update": "100/hour", # Güncelleme işlemleri
    "api_delete": "20/hour",  # Silme işlemleri
    
    # Arama işlemleri
    "api_search": "200/hour", # Arama işlemleri
    
    # Rapor işlemleri
    "api_reports": "30/hour", # Rapor oluşturma
}

class CustomRateLimiter:
    """Özel rate limiter - Gelişmiş sınırlama kuralları"""
    
    def __init__(self):
        self.request_counts = {}
        self.window_size = 3600  # 1 saat
        self.max_requests = 1000
    
    def is_allowed(self, client_ip: str, endpoint: str) -> bool:
        """İstek izin verilir mi kontrol et"""
        current_time = time.time()
        key = f"{client_ip}:{endpoint}"
        
        # Eski kayıtları temizle
        self._cleanup_old_requests(current_time)
        
        # İstek sayısını kontrol et
        if key not in self.request_counts:
            self.request_counts[key] = []
        
        # Son 1 saatteki istekleri say
        recent_requests = [
            req_time for req_time in self.request_counts[key]
            if current_time - req_time < self.window_size
        ]
        
        if len(recent_requests) >= self.max_requests:
            return False
        
        # Yeni isteği kaydet
        self.request_counts[key].append(current_time)
        return True
    
    def _cleanup_old_requests(self, current_time: float):
        """Eski istek kayıtlarını temizle"""
        cutoff_time = current_time - self.window_size
        for key in list(self.request_counts.keys()):
            self.request_counts[key] = [
                req_time for req_time in self.request_counts[key]
                if req_time > cutoff_time
            ]
            if not self.request_counts[key]:
                del self.request_counts[key]

# Global rate limiter instance
custom_limiter = CustomRateLimiter()

# Rate limit middleware - Tüm istekleri kontrol eder
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware - İstek sınırlarını kontrol eder"""
    client_ip = get_remote_address(request)
    endpoint = request.url.path
    
    # Endpoint tipine göre limit belirle
    if "/api/kitaplar" in endpoint and request.method == "POST":
        limit_type = "api_create"
    elif "/api/uyeler" in endpoint and request.method == "POST":
        limit_type = "api_create"
    elif "/api/kiralamalar" in endpoint and request.method == "POST":
        limit_type = "api_create"
    elif "/search" in endpoint:
        limit_type = "api_search"
    elif "/reports" in endpoint:
        limit_type = "api_reports"
    else:
        limit_type = "api_general"
    
    # Rate limit kontrolü
    if not custom_limiter.is_allowed(client_ip, limit_type):
        logging.warning(f"Rate limit aşıldı: {client_ip} - {endpoint}")
        raise HTTPException(
            status_code=429,
            detail="Çok fazla istek gönderildi. Lütfen daha sonra tekrar deneyin."
        )
    
    # İsteği devam ettir
    response = await call_next(request)
    return response

# Rate limit exception handler
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Rate limit aşıldığında özel yanıt"""
    return {
        "error": "Rate limit aşıldı",
        "message": "Çok fazla istek gönderildi. Lütfen daha sonra tekrar deneyin.",
        "retry_after": exc.retry_after,
        "status_code": 429
    }

# Rate limit istatistikleri
def get_rate_limit_stats():
    """Rate limit istatistiklerini al"""
    return {
        "active_ips": len(custom_limiter.request_counts),
        "total_requests": sum(len(requests) for requests in custom_limiter.request_counts.values()),
        "window_size": custom_limiter.window_size,
        "max_requests": custom_limiter.max_requests
    }
