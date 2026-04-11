import logging
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from uuid import uuid4
import os

from app.core.config import settings
from app.services.redis_service import redis_service
from app.services.postgres_service import PostgreSQLService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ===== IN-MEMORY USER STORAGE (Fallback for Supabase) =====
_users_db = {}  # email -> user_data dict

app = FastAPI(title="Auth Service", version="2.0.0")

@app.on_event("startup")
async def startup_event():
    """Initialize PostgreSQL pool on startup"""
    await PostgreSQLService.init_pool()
    logger.info("✅ PostgreSQL service initialized")

@app.middleware("http")
async def db_session_middleware(request, call_next):
    # This just ensures we can talk to PG
    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    house: str = "gryffindor"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    user_id: str
    username: str
    house: str
    message: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def get_current_user(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/health")
def health(): 
    return {"status": "healthy", "service": "auth"}


@app.post("/api/v1/auth/register", response_model=AuthResponse)
async def register(req: RegisterRequest):
    logger.info(f"📝 Registering user: {req.email}")
    
    # Check if user already exists in memory
    if req.email in _users_db:
        logger.warning(f"❌ User already exists: {req.email}")
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    user_id = str(uuid4())
    user_data = {
        "id": user_id,
        "email": req.email,
        "username": req.username,
        "password_hash": hash_password(req.password),
        "house": req.house.lower(),
        "created_at": datetime.utcnow().isoformat(),
        "total_score": 0,
        "problems_solved": 0,
    }
    
    # Store in memory (for speed/fallback)
    _users_db[req.email] = user_data
    logger.info(f"✅ User stored in memory: {req.email}")
    
    # Store in PostgreSQL (for persistence across services)
    await PostgreSQLService.create_user(
        user_id, req.email, req.username, user_data["password_hash"], req.house
    )
    logger.info(f"✅ User persisted to DB: {req.email}")
    
    # Create JWT token
    token = create_access_token(user_id, req.email)
    
    return AuthResponse(
        access_token=token,
        user_id=user_id,
        username=req.username,
        house=req.house.lower(),
        message=f"Welcome to CODUKU! You've been sorted into {req.house.title()}! 🧙"
    )


@app.post("/api/v1/auth/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    logger.info(f"🔐 Login attempt: {req.email}")
    
    # Find user in memory
    user = _users_db.get(req.email)
    
    # Fallback to DB if not in memory
    if not user:
        user = await PostgreSQLService.get_user_by_email(req.email)
        if user:
            _users_db[req.email] = user # Cache back to memory
            logger.info(f"✅ User found in DB and cached: {req.email}")
            
    if not user:
        logger.warning(f"❌ User not found: {req.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(req.password, user["password_hash"]):
        logger.warning(f"❌ Invalid password: {req.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(user["id"], user["email"])
    logger.info(f"✅ Login successful: {req.email}")
    
    return AuthResponse(
        access_token=token,
        user_id=user["id"],
        username=user["username"],
        house=user["house"],
        message=f"Welcome back! 🧙"
    )


@app.get("/api/v1/auth/me")
async def get_me(user_id: str = Depends(get_current_user)):
    logger.info(f"📋 Getting user profile: {user_id}")
    
    # Find user in memory
    user_found = None
    for user in _users_db.values():
        if user.get("id") == user_id:
            user_found = user
            break
    
    if not user_found:
        logger.warning(f"❌ User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        rank = await redis_service.get_user_rank("global", user_id)
    except Exception as e:
        logger.debug(f"Could not get user rank from Redis: {e}")
        rank = None
    
    return {**user_found, "rank": rank}


