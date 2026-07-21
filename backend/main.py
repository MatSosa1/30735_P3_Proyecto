from fastapi import FastAPI

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.config.rate_limiter import limiter
from src.routes.auth_routes import router as auth_router
from src.routes.users_routes import router as user_router
from src.routes.roles_routes import router as role_router
from src.routes.modules_routes import router as module_router
from src.routes.internal_routes import router as internal_router
from src.routes.menu_routes import router as menu_router


app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router, prefix='/api')
app.include_router(user_router, prefix='/api')
app.include_router(role_router, prefix='/api')
app.include_router(module_router, prefix='/api')
app.include_router(internal_router, prefix='/api')
app.include_router(menu_router, prefix='/api')

@app.get("/")
def root():
  return {
    "message": "Master Gateway API"
  }
