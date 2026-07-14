from src.models.models import Base
from src.db.conn import engine

Base.metadata.create_all(engine)
