# Kütüphane Yönetim Sistemi - Veritabanı Bağlantısı
# SQLAlchemy ile SQLite veritabanı bağlantısı ve yönetimi
# Veritabanı oturumu ve tablo oluşturma fonksiyonları

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

# SQLite veritabanı oluştur
DATABASE_URL = "sqlite:///./kutuphane.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Veritabanı tablolarını oluştur
def create_tables():
    Base.metadata.create_all(bind=engine)

# Veritabanı bağlantısı
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
