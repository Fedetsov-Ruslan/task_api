import json

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Response
)


from fastapi import APIRouter, Depends,  HTTPException
from fastapi_users.password import Argon2Hasher
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session, redis_client
from src.auth.orm_query import get_add_user, get_user
from src.auth.schema import LoginData
from src.auth.base_config import  get_jwt_strategy
from src.config import  LIFESPAN_REFRESH_TOKEN
from src.auth.auth_jwt import refresh_token, get_refresh_token
from src.users.models import User


router = APIRouter(prefix="/auth", tags=["auth"])

jwt_strategy = get_jwt_strategy()  


@router.post("/login")
async def login(
    data: LoginData,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
):
    user = await get_user(session, data.username)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail ="not authenticated"
        )
    elif Argon2Hasher().verify(data.password, user.pasword_hash):
        token = await jwt_strategy.write_token(user)
        
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,  
            max_age=360,       
            samesite="Lax"  
        )
        user_dict = {
            "id": user.id,
            "username": user.username,
            "password_hash": user.pasword_hash
        }
        rt = refresh_token(user, response, LIFESPAN_REFRESH_TOKEN)
        print(rt)
        redis_client.set(rt, json.dumps(user_dict))
        print(token)
        
        return  {"message": "login success"} 
    else:
        raise HTTPException(
            status_code=401,
            detail ="not authenticated"
        )

    
@router.post("/register/")
async def auth_login(
    username: str = Form(),
    password: str = Form(),
    session: AsyncSession = Depends(get_async_session)
):
    result = await get_add_user(session, username, password)
    return {
        "msg": result["message"],
        "username": result["username"]
    }
    
@router.post("/refresh")
async def refresh(
    response: Response,
    refresh_token: str = Depends(get_refresh_token),
    session: AsyncSession = Depends(get_async_session)
):
    print('refresh_token: ', refresh_token)
    user_data = redis_client.get(refresh_token)
    print(user_data)
    data = json.loads(user_data)
    print(data)
    user = User(id=data["id"], username=data["username"], pasword_hash=data["password_hash"])
    token = await jwt_strategy.write_token(user)
    response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,  
            max_age=360,     
            samesite="Lax"  
        )
    print(token)
    return  {"message": "login success"}
