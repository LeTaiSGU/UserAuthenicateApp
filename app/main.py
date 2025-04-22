import os
from fastapi import FastAPI
from app import models, database
from app.auth import routes as auth_routes
from starlette.middleware.sessions import SessionMiddleware

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "your_session_secret_key"),  # Dùng key riêng cho session!
    same_site="lax",  # hoặc "none" nếu dùng HTTPS
    https_only=False  # True nếu chạy HTTPS
)

app.include_router(auth_routes.router)

@app.get("/")
def root():
    return {"message": "Welcome to Auth API"}
