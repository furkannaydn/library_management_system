# Kütüphane Yönetim Sistemi - Ana Uygulama Dosyası
# FastAPI ile modern web API'si ve HTML arayüzü
# Kitap, üye ve kiralama yönetimi için REST API endpoints

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db, create_tables
from models import Kitap, Uye, Kiralama
from schemas import KitapCreate, KitapUpdate, Kitap as KitapSchema
from schemas import UyeCreate, UyeUpdate, Uye as UyeSchema
from schemas import KiralamaCreate, Kiralama as KiralamaSchema, KiralamaDetay
from datetime import datetime, timedelta
from typing import List, Optional
import os

# Teknik iyileştirmeler - Caching, Rate Limiting, Logging
from cache import cache_manager, cache_result, invalidate_kitap_cache, invalidate_uye_cache, invalidate_kiralama_cache
from rate_limiter import limiter, rate_limit_middleware
from logging_config import configure_logging, app_logger, api_logger, db_logger

# Logging sistemini başlat
configure_logging()

# FastAPI uygulaması oluştur - Ana web uygulaması
app = FastAPI(title="Kütüphane Yönetim Sistemi", version="1.0.0")

# Middleware ekle - Rate limiting ve logging
app.middleware("http")(rate_limit_middleware)

# Statik dosyalar (CSS, JS, resimler) için mount - /static/ URL'inde erişilebilir
app.mount("/static", StaticFiles(directory="static"), name="static")
# HTML şablonları için Jinja2 motoru - templates/ klasöründeki HTML dosyaları
templates = Jinja2Templates(directory="templates")

# Veritabanı tablolarını oluştur - İlk çalıştırmada tablolar oluşturulur
create_tables()

# Uygulama başlatma logu
app_logger.info("Kütüphane Yönetim Sistemi başlatıldı")

# Ana sayfa - Dashboard ve istatistikler
@app.get("/", response_class=HTMLResponse)
async def ana_sayfa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Kitap API'leri - CRUD işlemleri
@app.get("/api/kitaplar", response_model=List[KitapSchema])
@limiter.limit("100/hour")
async def kitaplari_getir(request: Request, db: Session = Depends(get_db)):
    # Cache'den veri al
    cached_data = await cache_manager.get("kitaplar:all")
    if cached_data:
        api_logger.info("Kitaplar cache'den alındı")
        return cached_data
    
    # Veritabanından veri al
    kitaplar = db.query(Kitap).all()
    db_logger.database_operation("SELECT", "kitaplar", count=len(kitaplar))
    
    # Cache'e kaydet
    await cache_manager.set("kitaplar:all", kitaplar, 300)
    api_logger.info("Kitaplar veritabanından alındı ve cache'e kaydedildi")
    
    return kitaplar

@app.get("/api/kitaplar/{kitap_id}", response_model=KitapSchema)
async def kitap_getir(kitap_id: int, db: Session = Depends(get_db)):
    kitap = db.query(Kitap).filter(Kitap.id == kitap_id).first()  # ID'ye göre kitap bul
    if not kitap:
        raise HTTPException(status_code=404, detail="Kitap bulunamadı")  # Kitap yoksa 404 hatası
    return kitap

@app.post("/api/kitaplar", response_model=KitapSchema)
@limiter.limit("50/hour")
async def kitap_ekle(request: Request, kitap: KitapCreate, db: Session = Depends(get_db)):
    db_kitap = Kitap(**kitap.dict())  # Yeni kitap nesnesi oluştur
    db.add(db_kitap)  # Veritabanına ekle
    db.commit()  # Değişiklikleri kaydet
    db.refresh(db_kitap)  # ID'yi al
    
    # Cache'i temizle
    await invalidate_kitap_cache()
    db_logger.database_operation("INSERT", "kitaplar", kitap_id=db_kitap.id)
    api_logger.info("Yeni kitap eklendi", kitap_id=db_kitap.id, baslik=db_kitap.baslik)
    
    return db_kitap

@app.put("/api/kitaplar/{kitap_id}", response_model=KitapSchema)
async def kitap_guncelle(kitap_id: int, kitap: KitapUpdate, db: Session = Depends(get_db)):
    db_kitap = db.query(Kitap).filter(Kitap.id == kitap_id).first()  # Güncellenecek kitabı bul
    if not db_kitap:
        raise HTTPException(status_code=404, detail="Kitap bulunamadı")
    
    # Sadece gönderilen alanları güncelle (exclude_unset=True)
    for field, value in kitap.dict(exclude_unset=True).items():
        setattr(db_kitap, field, value)  # Alan değerini güncelle
    
    db.commit()  # Değişiklikleri kaydet
    db.refresh(db_kitap)  # Güncellenmiş veriyi al
    return db_kitap

@app.delete("/api/kitaplar/{kitap_id}")
async def kitap_sil(kitap_id: int, db: Session = Depends(get_db)):
    db_kitap = db.query(Kitap).filter(Kitap.id == kitap_id).first()  # Silinecek kitabı bul
    if not db_kitap:
        raise HTTPException(status_code=404, detail="Kitap bulunamadı")
    
    db.delete(db_kitap)  # Kitabı sil
    db.commit()  # Değişiklikleri kaydet
    return {"message": "Kitap silindi"}

# Üye API'leri
@app.get("/api/uyeler", response_model=List[UyeSchema])
async def uyeleri_getir(db: Session = Depends(get_db)):
    return db.query(Uye).all()

@app.get("/api/uyeler/{uye_id}", response_model=UyeSchema)
async def uye_getir(uye_id: int, db: Session = Depends(get_db)):
    uye = db.query(Uye).filter(Uye.id == uye_id).first()
    if not uye:
        raise HTTPException(status_code=404, detail="Üye bulunamadı")
    return uye

@app.post("/api/uyeler", response_model=UyeSchema)
async def uye_ekle(uye: UyeCreate, db: Session = Depends(get_db)):
    db_uye = Uye(**uye.dict())
    db.add(db_uye)
    db.commit()
    db.refresh(db_uye)
    return db_uye

@app.put("/api/uyeler/{uye_id}", response_model=UyeSchema)
async def uye_guncelle(uye_id: int, uye: UyeUpdate, db: Session = Depends(get_db)):
    db_uye = db.query(Uye).filter(Uye.id == uye_id).first()
    if not db_uye:
        raise HTTPException(status_code=404, detail="Üye bulunamadı")
    
    for field, value in uye.dict(exclude_unset=True).items():
        setattr(db_uye, field, value)
    
    db.commit()
    db.refresh(db_uye)
    return db_uye

@app.delete("/api/uyeler/{uye_id}")
async def uye_sil(uye_id: int, db: Session = Depends(get_db)):
    db_uye = db.query(Uye).filter(Uye.id == uye_id).first()
    if not db_uye:
        raise HTTPException(status_code=404, detail="Üye bulunamadı")
    
    db.delete(db_uye)
    db.commit()
    return {"message": "Üye silindi"}

# Kiralama API'leri
@app.get("/api/kiralamalar", response_model=List[KiralamaDetay])
async def kiralamalari_getir(db: Session = Depends(get_db)):
    return db.query(Kiralama).all()

@app.post("/api/kiralamalar", response_model=KiralamaSchema)
async def kitap_kirala(kiralama: KiralamaCreate, db: Session = Depends(get_db)):
    # Kitap ve üye kontrolü - Geçerli ID'ler mi?
    kitap = db.query(Kitap).filter(Kitap.id == kiralama.kitap_id).first()
    if not kitap:
        raise HTTPException(status_code=404, detail="Kitap bulunamadı")
    
    uye = db.query(Uye).filter(Uye.id == kiralama.uye_id).first()
    if not uye:
        raise HTTPException(status_code=404, detail="Üye bulunamadı")
    
    # Kitap kiralanabilir mi kontrolü - Kitap müsait mi?
    if not kitap.kiralanabilir:
        raise HTTPException(status_code=400, detail="Kitap şu anda kiralanabilir değil")
    
    # Aktif kiralama var mı kontrolü - Kitap zaten kiralanmış mı?
    aktif_kiralama = db.query(Kiralama).filter(
        Kiralama.kitap_id == kiralama.kitap_id,
        Kiralama.durum == "aktif"
    ).first()
    
    if aktif_kiralama:
        raise HTTPException(status_code=400, detail="Kitap zaten kiralanmış")
    
    # Kiralama oluştur - Yeni kiralama kaydı
    db_kiralama = Kiralama(**kiralama.dict())
    db.add(db_kiralama)
    
    # Kitabı kiralanamaz yap - Kitap artık kiralanamaz durumda
    kitap.kiralanabilir = False
    db.commit()  # Tüm değişiklikleri kaydet
    db.refresh(db_kiralama)  # Yeni kiralama ID'sini al
    
    return db_kiralama

@app.put("/api/kiralamalar/{kiralama_id}/teslim")
async def kitap_teslim_et(kiralama_id: int, db: Session = Depends(get_db)):
    kiralama = db.query(Kiralama).filter(Kiralama.id == kiralama_id).first()  # Kiralama kaydını bul
    if not kiralama:
        raise HTTPException(status_code=404, detail="Kiralama bulunamadı")
    
    if kiralama.durum != "aktif":  # Kiralama aktif mi?
        raise HTTPException(status_code=400, detail="Kiralama zaten teslim edilmiş")
    
    # Teslim işlemi - Teslim tarihini ve durumunu güncelle
    kiralama.teslim_tarihi = datetime.utcnow()  # Şu anki zamanı teslim tarihi yap
    kiralama.durum = "teslim_edildi"  # Durumu teslim edildi yap
    
    # Kitabı tekrar kiralanabilir yap - Kitap artık tekrar kiralanabilir
    kitap = db.query(Kitap).filter(Kitap.id == kiralama.kitap_id).first()
    kitap.kiralanabilir = True  # Kitabı müsait yap
    
    db.commit()  # Tüm değişiklikleri kaydet
    return {"message": "Kitap teslim edildi"}

# Özel sayfalar
@app.get("/kitaplar", response_class=HTMLResponse)
async def kitaplar_sayfasi(request: Request):
    return templates.TemplateResponse("kitaplar.html", {"request": request})

@app.get("/uyeler", response_class=HTMLResponse)
async def uyeler_sayfasi(request: Request):
    return templates.TemplateResponse("uyeler.html", {"request": request})

@app.get("/kiralamalar", response_class=HTMLResponse)
async def kiralamalar_sayfasi(request: Request):
    return templates.TemplateResponse("kiralamalar.html", {"request": request})

# Sistem durumu ve istatistikler
@app.get("/api/system/stats")
async def sistem_istatistikleri():
    """Sistem durumu ve performans istatistikleri"""
    try:
        from cache import get_cache_stats
        from rate_limiter import get_rate_limit_stats
        from logging_config import get_log_stats
        
        cache_stats = await get_cache_stats()
        rate_limit_stats = get_rate_limit_stats()
        log_stats = get_log_stats()
        
        return {
            "cache": cache_stats,
            "rate_limiting": rate_limit_stats,
            "logging": log_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        app_logger.error(f"Sistem istatistikleri hatası: {e}")
        return {"error": "İstatistikler alınamadı"}

@app.get("/api/system/health")
async def sistem_sagligi():
    """Sistem sağlık kontrolü"""
    try:
        # Veritabanı bağlantısı test et
        db = next(get_db())
        db.execute("SELECT 1")
        
        # Cache bağlantısı test et
        await cache_manager.set("health_check", "ok", 10)
        cache_result = await cache_manager.get("health_check")
        
        return {
            "status": "healthy",
            "database": "connected",
            "cache": "connected" if cache_result == "ok" else "disconnected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        app_logger.error(f"Sistem sağlık kontrolü hatası: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
 
