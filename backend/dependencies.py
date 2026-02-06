from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from uuid import UUID
import asyncpg

from auth import decode_access_token
from database import get_db

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    user_type = payload.get("user_type")
    
    if not user_id or not user_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return {"user_id": UUID(user_id), "user_type": user_type}


async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Get current active user and verify account exists"""
    async with get_db() as conn:
        if current_user["user_type"] == "user":
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1 AND is_active = TRUE",
                current_user["user_id"]
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account not found or inactive"
                )
        elif current_user["user_type"] == "owner":
            owner = await conn.fetchrow(
                "SELECT * FROM owners WHERE id = $1 AND is_active = TRUE",
                current_user["user_id"]
            )
            if not owner:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Owner account not found or inactive"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user type"
            )
    
    return current_user


async def get_current_owner(current_user: dict = Depends(get_current_active_user)):
    """Ensure current user is an owner"""
    if current_user["user_type"] != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can access this resource"
        )
    return current_user
