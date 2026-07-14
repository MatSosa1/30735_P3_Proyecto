from sqlalchemy.orm import sessionmaker

from src.db.conn import engine

SessionLocal = sessionmaker(
  bind=engine,
  autoflush=False,
  autocommit=False,
  expire_on_commit=False
)