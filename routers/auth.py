from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from configs.auth import tweepy_client
from configs.db import get_session
from services.auth import authenticate_user, generate_jwt
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.auth import AuthUrlResponse, AuthData, TokenRefreshRequest
from jose import jwt
import os
from models.UserModel import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.get("/twitter/auth_url", response_model=AuthUrlResponse)
async def get_twitter_auth_url():
    """
    Generates a Twitter authentication URL which the user is redirected to for authentication.
    After successful authentication, it redirects to a predefined URL on the server, currently set to 
    'https://www.booster.trading/farming/auth/twitter/callback' (placeholder, contact backend for changes).
    """

    auth = tweepy_client()
    try:
        redirect_url = auth.get_authorization_url()
        return AuthUrlResponse(url=redirect_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get authorization URL: {str(e)}")

@router.post("/twitter/authenticate")
async def twitter_authenticate(auth_data: AuthData, db: AsyncSession = Depends(get_session)):
    """
    Authenticates a user using the received oauth_token and oauth_verifier. 
    If authentication is successful, it returns JWT access and refresh tokens.
    """
    response, tokens = await authenticate_user(auth_data.oauth_token, auth_data.oauth_verifier, db)
    if response:
        return JSONResponse(content={"status": "success", "access_token": tokens[0], "refresh_token": tokens[1]})
    else:
        raise HTTPException(status_code=400, detail="Authentication failed or user could not be created.")
    

@router.post("/token/refresh")
async def refresh_token(request: TokenRefreshRequest, db: AsyncSession = Depends(get_session)):
    """
    Accepts a valid refresh token and returns a new access token. Validates the refresh token and checks 
    its type, ensuring it is a 'refresh' type. Generates a new access token valid for 15 minutes if the 
    refresh token is valid.

    It won't return a new refresh token due to security & storaging reasons. The user must authenticate again to get a new refresh token.
    """
    refresh_token = request.refresh_token
    try:
        payload = jwt.decode(refresh_token, os.getenv('JWT_SECRET'), algorithms=["HS256"])
        if payload["type"] != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user = await db.get(User, payload["sub"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        access_token = generate_jwt(payload["sub"], "access", 15)  # Valid for 15 minutes
        return {"access_token": access_token}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")