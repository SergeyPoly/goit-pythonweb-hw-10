from fastapi import (
    FastAPI,
    Depends,
    File,
    UploadFile,
    status,
    Request,
)
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import redis.asyncio as redis
from contextlib import asynccontextmanager
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from database import engine, Base, get_db
from models import User
from schemas import UserResponse
from conf.config import settings
from auth import get_current_user
from routes import auth
from routes import contacts
from services.cloud import upload_avatar


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri=f"redis://{settings.redis_host}:{settings.redis_port}",
)

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup complete.")
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded. Try again later."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")


@app.get("/users/me", response_model=UserResponse, tags=["Users"])
@limiter.limit("2/5minute")
def read_users_me(request: Request, current_user: User = Depends(get_current_user)):
    return current_user


@app.patch("/users/avatar", response_model=UserResponse, tags=["Users"])
async def update_avatar(
    file: UploadFile = File(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    public_id_str = f"user_avatar_{current_user.id}"

    url = upload_avatar(file_stream=file.file, public_id=public_id_str, overwrite=True)

    current_user.avatar = url
    db.commit()
    db.refresh(current_user)

    return current_user
