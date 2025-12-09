from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database import execute_query, execute_procedure
from passlib.hash import bcrypt
from utils import safe_print

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    id: str
    username: str
    full_name: Optional[str]
    role: str


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Login endpoint - verifies username and password
    Uses PostgreSQL crypt() function for bcrypt verification
    """
    try:
        # Call verify_user_password function
        query = "SELECT * FROM call.qc_users WHERE username = $username AND password = $password"
        result = execute_query(query, (credentials.username, credentials.password), fetch_one=True)

        if not result:
            raise HTTPException(status_code=401, detail="نام کاربری یا رمز عبور اشتباه است")


        return LoginResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        safe_print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="خطا در ورود به سیستم")
