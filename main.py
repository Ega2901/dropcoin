from fastapi import FastAPI
from routers.auth import router as auth_router
from routers.casino import router as casino_router
app = FastAPI()

app.include_router(auth_router, casino_router)