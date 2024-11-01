import jwt

from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException,
    Query
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.config import SECRET_AUTH
from src.tasks.orm_query import (
    orm_create_task,
    orm_delete_task,
    orm_get_all_tasks_user,
    orm_update_task
)


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)

def get_access_token(
    request: Request
):
    coocke = request.cookies.get("access_token")
    if coocke is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Get access token, on refresh tocken",
            headers={"WWW-Authenticate": "Bearer"},  # Рекомендуется для указания типа авторизации
        )
    else:
        return coocke    


@router.post("/")
async def create_task(
    title: str,
    description: str,
    active: bool = True,
    current_user: str = Depends(get_access_token),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        user = jwt.decode(current_user.encode(), SECRET_AUTH, algorithms=["HS256"], audience=["fastapi-users:auth"])
        print(user)

        query =  await orm_create_task(title, description, active, int(user['sub']), session)
        return query
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired, crete newtoken. Use refresh token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    

@router.get("/")
async def get_tasks(
    current_user: str = Depends(get_access_token),
    is_active: bool = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        user = jwt.decode(current_user.encode(), SECRET_AUTH, algorithms=["HS256"], audience=["fastapi-users:auth"])
        query =  await orm_get_all_tasks_user(int(user['sub']), is_active, session)
        return query
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired, crete newtoken. Use refresh token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    

@router.put("/{id}")
async def update_task(
    id: int,
    title: str,
    description: str,
    active: bool = True,
    current_user: str = Depends(get_access_token),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        user = jwt.decode(current_user.encode(), SECRET_AUTH, algorithms=["HS256"], audience=["fastapi-users:auth"])
        query =  await orm_update_task(id, title, description, active, int(user['sub']), session)
        return query
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired, crete newtoken. Use refresh token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    
@router.delete("/{id}")
async def delete_task(
    id: int,
    current_user: str = Depends(get_access_token),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        user = jwt.decode(current_user.encode(), SECRET_AUTH, algorithms=["HS256"], audience=["fastapi-users:auth"])
        query =  await orm_delete_task(id, int(user['sub']), session)
        return query
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired, crete newtoken. Use refresh token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")