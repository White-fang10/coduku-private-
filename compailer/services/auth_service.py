from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime

# In a true microservice, this would have its own database connection.
# For our decomposed monolith, we import the shared data layers.
import main

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

class AuthResponse(BaseModel):
    access_token: str
    user_id: str
    name: str
    username: str
    email: str
    house: str

class RegisterRequest(BaseModel):
    name: str | None = None
    username: str | None = None
    email: EmailStr
    password: str
    house: str = "gryffindor"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    valid_houses = ["gryffindor", "hufflepuff", "ravenclaw", "slytherin"]
    if request.house.lower() not in valid_houses:
        raise HTTPException(status_code=400, detail="Invalid house")
    
    if await main.user_exists(request.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    display_name = request.name or request.username
    if not display_name:
        raise HTTPException(status_code=400, detail="Missing name/username")

    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "name": display_name,
        "email": request.email,
        "password_hash": main.hash_password(request.password),
        "house": request.house.lower(),
        "role": "student",
        "created_at": datetime.utcnow().isoformat(),
        "total_score": 0,
        "problems_solved": 0,
        "submissions": 0
    }
    
    try:
        await main.insert_user(user_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Email already registered") from e
    token = main.create_jwt_token(user_id, request.email)
    
    return AuthResponse(
        access_token=token,
        user_id=user_id,
        name=display_name,
        username=display_name,
        email=request.email,
        house=request.house.lower()
    )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    user = await main.get_user_by_email(request.email)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not main.verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = main.create_jwt_token(user["id"], request.email)
    
    return AuthResponse(
        access_token=token,
        user_id=user["id"],
        name=user["name"],
        username=user.get("username", user["name"]),
        email=user["email"],
        house=user["house"]
    )

@router.get("/me")
async def get_current_user(payload: dict = Depends(main.verify_jwt_token)):
    email = payload.get("email")
    user = await main.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "house": user["house"],
        "total_score": user["total_score"],
        "problems_solved": user["problems_solved"],
        "submissions": user["submissions"]
    }
