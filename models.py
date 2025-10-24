# Kütüphane Yönetim Sistemi - Veritabanı Modelleri
# SQLAlchemy ORM ile veritabanı tablolarını tanımlar
# Kitap, Üye ve Kiralama tabloları için model sınıfları

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Kitap(Base):
    __tablename__ = "kitaplar"  # Veritabanı tablo adı
    
    # Ana alanlar - Kitap bilgileri
    id = Column(Integer, primary_key=True, index=True)  # Birincil anahtar, otomatik artan
    baslik = Column(String(200), nullable=False)  # Kitap başlığı, zorunlu
    yazar = Column(String(100), nullable=False)  # Yazar adı, zorunlu
    yayin_evi = Column(String(100))  # Yayın evi, opsiyonel
    yayin_yili = Column(Integer)  # Yayın yılı, opsiyonel
    isbn = Column(String(20), unique=True)  # ISBN numarası, benzersiz
    sayfa_sayisi = Column(Integer)  # Sayfa sayısı, opsiyonel
    aciklama = Column(Text)  # Kitap açıklaması, uzun metin
    
    # Durum alanları - Kiralama durumu
    kiralanabilir = Column(Boolean, default=True)  # Kitap kiralanabilir mi? Varsayılan: Evet
    olusturma_tarihi = Column(DateTime, default=datetime.utcnow)  # Kayıt tarihi, otomatik
    
    # İlişkiler - Diğer tablolarla bağlantı
    kiralama_gecmisi = relationship("Kiralama", back_populates="kitap")  # Bu kitabın kiralama geçmişi

class Uye(Base):
    __tablename__ = "uyeler"  # Veritabanı tablo adı
    
    # Ana alanlar - Üye bilgileri
    id = Column(Integer, primary_key=True, index=True)  # Birincil anahtar, otomatik artan
    ad = Column(String(50), nullable=False)  # Üye adı, zorunlu
    soyad = Column(String(50), nullable=False)  # Üye soyadı, zorunlu
    email = Column(String(100), unique=True, nullable=False)  # E-posta, benzersiz ve zorunlu
    telefon = Column(String(15))  # Telefon numarası, opsiyonel
    adres = Column(Text)  # Adres bilgisi, uzun metin, opsiyonel
    
    # Durum alanları - Üyelik durumu
    uyelik_tarihi = Column(DateTime, default=datetime.utcnow)  # Üyelik tarihi, otomatik
    aktif = Column(Boolean, default=True)  # Üye aktif mi? Varsayılan: Evet
    
    # İlişkiler - Diğer tablolarla bağlantı
    kiralama_gecmisi = relationship("Kiralama", back_populates="uye")  # Bu üyenin kiralama geçmişi

class Kiralama(Base):
    __tablename__ = "kiralamalar"  # Veritabanı tablo adı
    
    # Ana alanlar - Kiralama bilgileri
    id = Column(Integer, primary_key=True, index=True)  # Birincil anahtar, otomatik artan
    kitap_id = Column(Integer, ForeignKey("kitaplar.id"), nullable=False)  # Hangi kitap? Zorunlu
    uye_id = Column(Integer, ForeignKey("uyeler.id"), nullable=False)  # Hangi üye? Zorunlu
    
    # Tarih alanları - Kiralama süreci
    kiralama_tarihi = Column(DateTime, default=datetime.utcnow)  # Ne zaman kiralandı? Otomatik
    teslim_tarihi = Column(DateTime)  # Ne zaman teslim edildi? Opsiyonel
    son_teslim_tarihi = Column(DateTime, nullable=False)  # En son ne zaman teslim edilmeli? Zorunlu
    
    # Durum alanları - Kiralama durumu
    durum = Column(String(20), default="aktif")  # Durum: aktif, teslim_edildi, gecikmis
    notlar = Column(Text)  # Kiralama notları, opsiyonel
    
    # İlişkiler - Diğer tablolarla bağlantı
    kitap = relationship("Kitap", back_populates="kiralama_gecmisi")  # Hangi kitap?
    uye = relationship("Uye", back_populates="kiralama_gecmisi")  # Hangi üye?
