from sqlalchemy import create_engine

from src.config.env import DB_NAME, DB_USERNAME, DB_PASSWORD, DB_PORT, DB_HOSTNAME

engine = create_engine(
  f'postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}',
  # echo=True
)
