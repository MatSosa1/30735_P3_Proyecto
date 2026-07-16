from sqlalchemy.orm import Session, sessionmaker

from src.db.conn import engine

SessionLocal = sessionmaker(
  bind=engine,
  autoflush=False,
  autocommit=False,
  expire_on_commit=False
)

def get_db():
  db: Session = SessionLocal()

  try:
    yield db
  finally:
    db.close()
