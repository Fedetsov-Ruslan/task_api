from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.tasks.models import Task


async def orm_create_task(
    title:str,
    description:str,
    is_active:bool,
    user_id:int,
    session: AsyncSession
):
    try:
        new_task = Task(
            title=title,
            description=description,
            is_active=is_active,
            user_id=user_id
        )
        session.add(new_task)
        await session.commit()
        return {
            "message": "Task created successfully"
            }
    except Exception as e:
        return {"message": str(e).split(":")[1]}    
    
    
async def orm_get_all_tasks_user(
    user_id:int,
    is_active:bool,
    session: AsyncSession
):
    try:
        query = select(Task).where(Task.user_id == user_id)
        if is_active is not None:
            query = query.where(Task.is_active == is_active)
        result = await session.execute(query)
        tasks = result.scalars().all()
        return tasks
    except Exception as e:
        return {"message": str(e).split(":")[1]}
    

async def orm_update_task(
    task_id:int,
    title:str,
    description:str,
    is_active:bool,
    user_id:int,
    session: AsyncSession
):
    try:
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(query)
        task = result.scalar_one_or_none()
        if task is None:
            return {"message": "Task not found"}
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if is_active is not None:
            task.is_active = is_active
        await session.commit()
        return task
    except Exception as e:
        return {"message": str(e)}
    

async def orm_delete_task(
    task_id:int,
    user_id:int,
    session: AsyncSession
):
    try:
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(query)
        task = result.scalar_one_or_none()
        if task is None:
            return {"message": "Task not found"}
        await session.delete(task)
        await session.commit()
        return task
    except Exception as e:
        return {"message": str(e)}