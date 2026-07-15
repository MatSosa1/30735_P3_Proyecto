import os
from dotenv import load_dotenv

load_dotenv()

# DB
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOSTNAME = os.getenv('DB_HOSTNAME', 'localhost')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT', 5432)

JWT_SECRET = os.getenv('JWT_SECRET')
JWT_EXPIRE_IN_MINUTES: int = int(os.getenv('JWT_EXPIRE_IN_MINUTES', 5))
