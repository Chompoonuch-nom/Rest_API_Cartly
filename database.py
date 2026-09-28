from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI dependency - เปิด session ต่อ request แล้วปิดอัตโนมัติเมื่อจบ"""
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()