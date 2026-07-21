from fastapi import FastAPI

from src.routes.auth_routes import router as auth_router
from src.routes.users_routes import router as user_router
from src.routes.roles_routes import router as role_router
from src.routes.modules_routes import router as module_router


app = FastAPI()

app.include_router(auth_router, prefix='/api')
app.include_router(user_router, prefix='/api')
app.include_router(role_router, prefix='/api')
app.include_router(module_router, prefix='/api')

@app.get("/")
def root():
  return {
    "message": "Master Gateway API"
  }
