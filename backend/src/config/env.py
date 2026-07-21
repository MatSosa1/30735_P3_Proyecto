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
TEMP_TOKEN_EXPIRE_IN_MINUTES: int = int(os.getenv('TEMP_TOKEN_EXPIRE_IN_MINUTES', 2))
REFRESH_TOKEN_EXPIRE_IN_DAYS: int = int(os.getenv('REFRESH_TOKEN_EXPIRE_IN_DAYS', 7))

# Secreto compartido para que microservicios hijos llamen a /api/internals/validate-token
INTERNAL_SERVICES_SECRET = os.getenv('INTERNAL_SERVICES_SECRET')
