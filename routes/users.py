from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from database import execute_query
from utils import sanitize_error_message

router = APIRouter(prefix="/users", tags=["User Management"])


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    role: str = "agent"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class PasswordChange(BaseModel):
    new_password: str


class UserResponse(BaseModel):
    id: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: str


@router.get("/", response_model=List[UserResponse])
async def get_all_users():
    """Get all users"""
    try:
        query = """
            SELECT id, username, full_name, role, is_active, created_at::text
            FROM qc_users
            ORDER BY created_at DESC
        """
        users = execute_query(query)
        return users
    except Exception as e:
#        print(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت لیست کاربران")


@router.post("/", status_code=201)
async def create_user(user: UserCreate):
    """Create a new user with bcrypt hashed password"""
    try:
        # Try using RPC function first
        query = "SELECT create_qc_user(%s, %s, %s, %s)"
        execute_query(
            query,
            (user.full_name, user.password, user.role, user.username),
            fetch_all=False
        )
        return {"message": "کاربر با موفقیت ایجاد شد"}

    except Exception as e:
        error_msg = str(e)

        # Check for duplicate username
        if 'duplicate key' in error_msg or 'already exists' in error_msg:
            raise HTTPException(status_code=400, detail="نام کاربری تکراری است")

        # If function doesn't exist, use direct insert (fallback)
        if 'does not exist' in error_msg or 'function' in error_msg.lower():
            try:
                query = """
                    INSERT INTO qc_users (username, password_hash, full_name, role, is_active)
                    VALUES (%s, %s, %s, %s, true)
                """
                execute_query(
                    query,
                    (user.username, user.password, user.full_name, user.role),
                    fetch_all=False
                )
#                print("[WARNING] User created with plain text password")
                return {"message": "کاربر ایجاد شد (⚠️ بدون hash)"}
            except Exception as e2:
                if 'duplicate key' in str(e2):
                    raise HTTPException(status_code=400, detail="نام کاربری تکراری است")
                raise HTTPException(status_code=500, detail=f"خطا در ایجاد کاربر: {str(e2)}")

        raise HTTPException(status_code=500, detail="خطا در ایجاد کاربر")


@router.put("/{user_id}")
async def update_user(user_id: str, user_update: UserUpdate):
    """Update user information"""
    try:
        # Build dynamic update query
        updates = []
        params = []

        if user_update.full_name is not None:
            updates.append("full_name = %s")
            params.append(user_update.full_name)

        if user_update.role is not None:
            updates.append("role = %s")
            params.append(user_update.role)

        if user_update.is_active is not None:
            updates.append("is_active = %s")
            params.append(user_update.is_active)

        if not updates:
            raise HTTPException(status_code=400, detail="هیچ فیلدی برای به‌روزرسانی ارسال نشده")

        params.append(user_id)
        query = f"UPDATE qc_users SET {', '.join(updates)} WHERE id = %s"

        execute_query(query, tuple(params), fetch_all=False)
        return {"message": "کاربر با موفقیت به‌روزرسانی شد"}

    except HTTPException:
        raise
    except Exception as e:
#        print(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="خطا در به‌روزرسانی کاربر")


@router.put("/{user_id}/password")
async def change_password(user_id: str, password_data: PasswordChange):
    """Change user password"""
    try:
        # Try using RPC function
        query = "SELECT change_user_password(%s, %s)"
        execute_query(query, (password_data.new_password, user_id), fetch_all=False)
        return {"message": "رمز عبور با موفقیت تغییر کرد"}

    except Exception as e:
        # Fallback to direct update
        if 'does not exist' in str(e) or 'function' in str(e).lower():
            try:
                query = "UPDATE qc_users SET password_hash = %s WHERE id = %s"
                execute_query(query, (password_data.new_password, user_id), fetch_all=False)
#                print("[WARNING] Password stored as plain text")
                return {"message": "رمز عبور تغییر کرد (⚠️ بدون hash)"}
            except Exception as e2:
                raise HTTPException(status_code=500, detail=f"خطا در تغییر رمز: {str(e2)}")

        raise HTTPException(status_code=500, detail="خطا در تغییر رمز عبور")


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """Delete a user"""
    try:
        query = "DELETE FROM qc_users WHERE id = %s"
        execute_query(query, (user_id,), fetch_all=False)
        return {"message": "کاربر با موفقیت حذف شد"}

    except Exception as e:
#        print(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="خطا در حذف کاربر")
