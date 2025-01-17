import tweepy
from configs.auth import tweepy_client
from repositories.UserRepository import insert_or_get_user
from models.UserModel import User
from jose import jwt
from datetime import datetime, timezone, timedelta
from configs.environment import get_environment_variables
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from configs.db import get_session
from hashlib import sha256
import os
from schemas.auth import TelegramAuthData
import hmac
import json
from urllib.parse import unquote
authorization_scheme = HTTPBearer(auto_error=False)
JWT_SECRET = get_environment_variables().JWT_SECRET


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(authorization_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=403, detail="Credentials are required")

    token = credentials.credentials
    print("Token is", token)
    try:
        print(token, JWT_SECRET)
        print(type(token), type(JWT_SECRET))
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        print("JIJFOEWJF", payload)
        user_id = payload.get("sub")
        print(user_id)
        if user_id is None:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid JWT: {str(e)}")

    user_result = await session.execute(
        select(User)
        .options(selectinload(User.referrer), selectinload(User.referrals))
        .where(User.id == user_id)
    )
    user = user_result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


def validate(hash_str, init_data, token, c_str="WebAppData"):
    """
    Validates the data received from the Telegram web app, using the
    method documented here:
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app

    hash_str - the hash string passed by the webapp
    init_data - the query string passed by the webapp
    token - Telegram bot's token
    c_str - constant string (default = "WebAppData")
    """
    print("Validation 1", init_data)
    
    # Корректное исключение параметра 'hash'
    init_data = sorted(
        [
            chunk.split("=")
            for chunk in unquote(init_data).split("&")
            if not chunk.startswith("hash=")  # Исключаем параметр 'hash'
        ],
        key=lambda x: x[0],  # Сортируем параметры
    )
    print("Validation 2", init_data)
    
    # Воссоздаем data_check_string
    init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])
    print("Validation 3", init_data)
    
    # Создаем секретный ключ на основе токена и константной строки
    secret_key = hmac.new(c_str.encode(), token.encode(), hashlib.sha256).digest()
    data_check = hmac.new(secret_key, init_data.encode(), hashlib.sha256).hexdigest()

    # Сравниваем вычисленный хэш с предоставленным хэшем
    return data_check == hash_str


def generate_jwt(user_id: str, token_type: str, expiry_minutes: int):
    payload = {
        "sub": user_id,
        "type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


async def authenticate_user(user_id: str, db: AsyncSession):
    try:
        user = await insert_or_get_user(user_id, db)
        if user:
            access_token = generate_jwt(user.id, "access", 15)  # Valid for 15 minutes
            refresh_token = generate_jwt(user.id, "refresh", 43200)  # Valid for 30 days
            return True, (access_token, refresh_token)
        else:
            return False, None
    except Exception as e:
        print(e)
        return False, None
