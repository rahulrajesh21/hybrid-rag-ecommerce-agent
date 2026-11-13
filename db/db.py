from sqlalchemy.orm import declarative_base,sessionmaker
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from config import DB_PASSWORD,DB_NAME

password = quote_plus(DB_PASSWORD)
db_url = f"postgresql+psycopg2://postgres:{password}@localhost:5432/{DB_NAME}"

engine = create_engine(
    url = db_url,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()