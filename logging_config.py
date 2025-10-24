# Kütüphane Yönetim Sistemi - Logging Konfigürasyonu
# Gelişmiş log yönetimi ve sistem izleme
# Structlog ile yapılandırılmış loglar

import structlog
import logging
import sys
from datetime import datetime
from pathlib import Path
import json

# Log dosyaları için klasör oluştur
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Log formatter - Yapılandırılmış log formatı
def configure_logging():
    """Logging sistemini yapılandır"""
    
    # Structlog konfigürasyonu
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Console handler - Terminal çıktısı
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler - Dosya logları
    file_handler = logging.FileHandler(
        log_dir / f"kutuphane_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Error handler - Hata logları
    error_handler = logging.FileHandler(
        log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    
    # Root logger konfigürasyonu
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    return root_logger

# Logger sınıfı - Özel log fonksiyonları
class LibraryLogger:
    """Kütüphane özel logger sınıfı"""
    
    def __init__(self, name: str):
        self.logger = structlog.get_logger(name)
    
    def info(self, message: str, **kwargs):
        """Bilgi logu"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Uyarı logu"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Hata logu"""
        self.logger.error(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Debug logu"""
        self.logger.debug(message, **kwargs)
    
    # Özel log fonksiyonları
    def api_request(self, method: str, endpoint: str, user_ip: str, **kwargs):
        """API istek logu"""
        self.logger.info(
            "API Request",
            method=method,
            endpoint=endpoint,
            user_ip=user_ip,
            **kwargs
        )
    
    def api_response(self, status_code: int, response_time: float, **kwargs):
        """API yanıt logu"""
        self.logger.info(
            "API Response",
            status_code=status_code,
            response_time=response_time,
            **kwargs
        )
    
    def database_operation(self, operation: str, table: str, **kwargs):
        """Veritabanı işlem logu"""
        self.logger.info(
            "Database Operation",
            operation=operation,
            table=table,
            **kwargs
        )
    
    def user_action(self, action: str, user_id: int = None, **kwargs):
        """Kullanıcı işlem logu"""
        self.logger.info(
            "User Action",
            action=action,
            user_id=user_id,
            **kwargs
        )
    
    def security_event(self, event_type: str, severity: str, **kwargs):
        """Güvenlik olay logu"""
        self.logger.warning(
            "Security Event",
            event_type=event_type,
            severity=severity,
            **kwargs
        )
    
    def performance_metric(self, metric_name: str, value: float, **kwargs):
        """Performans metrik logu"""
        self.logger.info(
            "Performance Metric",
            metric_name=metric_name,
            value=value,
            **kwargs
        )

# Global logger instances
app_logger = LibraryLogger("kutuphane_app")
api_logger = LibraryLogger("kutuphane_api")
db_logger = LibraryLogger("kutuphane_db")
security_logger = LibraryLogger("kutuphane_security")

# Log decorator - Fonksiyon logları
def log_function_call(func):
    """Fonksiyon çağrılarını logla"""
    def wrapper(*args, **kwargs):
        app_logger.info(
            f"Function called: {func.__name__}",
            function=func.__name__,
            args=str(args),
            kwargs=str(kwargs)
        )
        try:
            result = func(*args, **kwargs)
            app_logger.info(
                f"Function completed: {func.__name__}",
                function=func.__name__,
                success=True
            )
            return result
        except Exception as e:
            app_logger.error(
                f"Function failed: {func.__name__}",
                function=func.__name__,
                error=str(e),
                success=False
            )
            raise
    return wrapper

# Log temizleme fonksiyonu
def cleanup_old_logs(days: int = 30):
    """Eski log dosyalarını temizle"""
    try:
        cutoff_date = datetime.now().timestamp() - (days * 24 * 3600)
        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_date:
                log_file.unlink()
                app_logger.info(f"Eski log dosyası silindi: {log_file}")
    except Exception as e:
        app_logger.error(f"Log temizleme hatası: {e}")

# Log istatistikleri
def get_log_stats():
    """Log istatistiklerini al"""
    try:
        today = datetime.now().strftime('%Y%m%d')
        log_file = log_dir / f"kutuphane_{today}.log"
        
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            return {
                'total_logs': len(lines),
                'error_count': len([line for line in lines if 'ERROR' in line]),
                'warning_count': len([line for line in lines if 'WARNING' in line]),
                'info_count': len([line for line in lines if 'INFO' in line]),
                'file_size': log_file.stat().st_size
            }
        return {}
    except Exception as e:
        app_logger.error(f"Log stats hatası: {e}")
        return {}
