# Kütüphane Yönetim Sistemi - Pydantic Şemaları
# API istekleri ve yanıtları için veri doğrulama şemaları
# Kitap, Üye ve Kiralama için request/response modelleri

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Kitap şemaları
class KitapBase(BaseModel):
    baslik: str
    yazar: str
    yayin_evi: Optional[str] = None
    yayin_yili: Optional[int] = None
    isbn: Optional[str] = None
    sayfa_sayisi: Optional[int] = None
    aciklama: Optional[str] = None

class KitapCreate(KitapBase):
    pass

class KitapUpdate(KitapBase):
    kiralanabilir: Optional[bool] = None

class Kitap(KitapBase):
    id: int
    kiralanabilir: bool
    olusturma_tarihi: datetime
    
    class Config:
        from_attributes = True

# Üye şemaları
class UyeBase(BaseModel):
    ad: str
    soyad: str
    email: str
    telefon: Optional[str] = None
    adres: Optional[str] = None

class UyeCreate(UyeBase):
    pass

class UyeUpdate(UyeBase):
    aktif: Optional[bool] = None

class Uye(UyeBase):
    id: int
    uyelik_tarihi: datetime
    aktif: bool
    
    class Config:
        from_attributes = True

# Kiralama şemaları
class KiralamaBase(BaseModel):
    kitap_id: int
    uye_id: int
    son_teslim_tarihi: datetime
    notlar: Optional[str] = None

class KiralamaCreate(KiralamaBase):
    pass

class Kiralama(KiralamaBase):
    id: int
    kiralama_tarihi: datetime
    teslim_tarihi: Optional[datetime] = None
    durum: str
    
    class Config:
        from_attributes = True

# Detaylı kiralama bilgisi
class KiralamaDetay(Kiralama):
    kitap: Kitap
    uye: Uye
    
    class Config:
        from_attributes = True
