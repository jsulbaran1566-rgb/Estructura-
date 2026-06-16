from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Cambiamos el prefijo a postgresql+psycopg2 y ajustamos las credenciales
# Formato: postgresql+psycopg2://usuario:contraseña@host/nombre_base_datos
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:1234@localhost/agro_mercado"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
  
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()