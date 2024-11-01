from fastapi import FastAPI

from src.auth.views import router as auth_router
from src.tasks.router import router as task_router


app = FastAPI()

app.include_router(auth_router)
app.include_router(task_router)

